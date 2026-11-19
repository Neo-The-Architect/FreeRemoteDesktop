"""Persistent Playwright Chromium session with HTTPS host allowlist."""
from __future__ import annotations
from urllib.parse import urlsplit
from threading import RLock
import base64, io

_lock=RLock()
_state={"playwright":None,"browser":None,"page":None}

def _hosts(cfg):
    return {str(host).strip().lower() for host in cfg.get("browser_hosts",[]) if host}

def _check(url,cfg):
    parsed=urlsplit(url)
    if parsed.scheme!="https" or not parsed.hostname or parsed.hostname.lower() not in _hosts(cfg):
        raise PermissionError("Only allowlisted HTTPS hosts are accessible")

def _route(route,cfg):
    try:
        _check(route.request.url,cfg)
        route.continue_()
    except Exception:
        route.abort()

def start(cfg):
    if not cfg.get("allow_browser"): raise PermissionError("Browser automation disabled")
    if not _hosts(cfg): raise PermissionError("No approved browser_hosts")
    with _lock:
        if _state["page"] is not None: return _state["page"]
        try: from playwright.sync_api import sync_playwright
        except ImportError: raise RuntimeError("Install browser extras: pip install playwright && playwright install chromium")
        pw=sync_playwright().start()
        try:
            browser=pw.chromium.launch(headless=True)
            page=browser.new_page(accept_downloads=False,service_workers="block")
            page.route("**/*",lambda route:_route(route,cfg))
            _state.update({"playwright":pw,"browser":browser,"page":page})
            return page
        except Exception:
            pw.stop()
            raise

def perform(name,args,cfg):
    with _lock:
        if name=="browser_navigate":
            _check(args["url"],cfg)
            page=start(cfg)
            page.goto(args["url"],wait_until="domcontentloaded",timeout=15000)
            _check(page.url,cfg)
            return {"url":page.url,"title":page.title(),"text":page.locator("body").inner_text(timeout=5000)[:12000]}
        if name=="browser_snapshot":
            page=start(cfg)
            if not page.url.startswith("https://"): raise ValueError("Navigate to an approved page first")
            _check(page.url,cfg)
            return {"url":page.url,"title":page.title(),"text":page.locator("body").inner_text(timeout=5000)[:12000]}
        if name=="browser_click":
            if not cfg.get("allow_gui"): raise PermissionError("Browser interaction requires allow_gui")
            page=start(cfg)
            _check(page.url,cfg)
            selector=args["selector"]
            if len(selector)>500: raise ValueError("Selector too long")
            page.locator(selector).first.click(timeout=5000)
            _check(page.url,cfg)
            return {"url":page.url,"title":page.title()}
        if name=="browser_screenshot":
            page=start(cfg)
            _check(page.url,cfg)
            data=page.screenshot(type="png",full_page=False)
            return {"mime":"image/png","base64":base64.b64encode(data).decode("ascii")}
        raise ValueError("Unknown browser tool")

def close():
    with _lock:
        if _state["browser"]:_state["browser"].close()
        if _state["playwright"]:_state["playwright"].stop()
        _state.update({"playwright":None,"browser":None,"page":None})
