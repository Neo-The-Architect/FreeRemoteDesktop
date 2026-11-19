"""FreeRemoteDesktop: capability-gated actions. Python stdlib core, optional GUI/browser packages."""
from __future__ import annotations
import base64, json, os, pathlib, platform, shlex, subprocess, sys, time, hashlib
from dataclasses import dataclass
from typing import Any

APP = pathlib.Path.home() / ".freeremotedesktop"
CONFIG = APP / "config.json"
AUDIT = APP / "audit.jsonl"
MAX_TEXT = 128_000
MAX_OUTPUT = 16_000
DENIED = {".ssh", ".aws", ".gnupg", ".kube", ".git-credentials", ".npmrc", ".env", ".env.local",
          ".env.production", "credentials.json", "secrets.json", "token.json", "id_rsa", "id_ed25519"}
DENIED_SUFFIX = {".pem", ".pfx", ".p12", ".key", ".kdbx"}

def defaults():
    return {"roots": [],
            "allow_write": False, "allow_shell": False, "allow_screen": False,
            "allow_gui": False, "allow_browser": False,
            "shell_commands": ["git status", "git diff", "git log", "python --version",
                               "node --version", "npm --version"],
            "browser_hosts": [], "max_file_bytes": MAX_TEXT}

def load():
    if not CONFIG.is_file():
        value=defaults()
    else:
        value=json.loads(CONFIG.read_text(encoding="utf-8"))
    config = {**defaults(), **value}
    env_root=os.environ.get("FRD_APPROVED_ROOT")
    if env_root:
        path=pathlib.Path(env_root).expanduser().resolve()
        if not path.is_dir() or path == pathlib.Path.home().resolve() or path == pathlib.Path(path.anchor):
            raise ValueError("FRD_APPROVED_ROOT must be a specific existing workspace directory")
        config["roots"]=[str(path)]
    return config

def audit(name, status, detail=""):
    APP.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "action": name, "status": status, "detail": str(detail)[:200]})+"\n")

def authorized_path(raw, cfg, *, writing=False):
    if writing and not cfg.get("allow_write"): raise PermissionError("Write tools disabled; enable explicitly in local config")
    p = pathlib.Path(raw).expanduser().resolve()
    roots = [pathlib.Path(s).expanduser().resolve() for s in cfg["roots"]]
    if not any(p == r or r in p.parents for r in roots):
        raise PermissionError("Path outside approved project roots")
    if any(part.lower() in DENIED for part in p.parts) or p.suffix.lower() in DENIED_SUFFIX:
        raise PermissionError("Credential or sensitive path denied")
    return p

def result(name, args):
    cfg = load()
    try:
        data = action(name, args, cfg)
        audit(name, "ok")
        if isinstance(data, dict) and data.get("mime")=="image/png" and "base64" in data:
            return {"content":[{"type":"image","data":data["base64"],"mimeType":"image/png"}],"isError":False}
        return {"content":[{"type":"text","text":json.dumps(data, ensure_ascii=False)}], "isError":False}
    except Exception as e:
        audit(name, "denied_or_failed", type(e).__name__)
        return {"content":[{"type":"text","text":str(e)}],"isError":True}

def action(name: str, a: dict[str,Any], cfg: dict):
    if name == "desktop_status":
        return {"name":"FreeRemoteDesktop","version":"0.2.1","host":platform.node(),
                "platform":platform.system(),"roots":cfg["roots"],
                "capabilities":{k:v for k,v in cfg.items() if k.startswith("allow_")}}
    if name == "list_directory":
        p=authorized_path(a["path"],cfg)
        if not p.is_dir(): raise ValueError("Not a directory")
        entries = sorted(p.iterdir(), key=lambda x:x.name.lower())
        return {"path":str(p),"entries":[{"name":x.name,"kind":"dir" if x.is_dir() else "file"}
                    for x in entries[:200] if x.name.lower() not in DENIED and x.suffix.lower() not in DENIED_SUFFIX],
                "truncated":len(entries)>200}
    if name == "read_text_file":
        p=authorized_path(a["path"],cfg)
        if not p.is_file(): raise ValueError("Not a file")
        if p.stat().st_size>int(cfg["max_file_bytes"]): raise ValueError("File exceeds configured limit")
        return {"path":str(p),"text":p.read_text(encoding="utf-8")}
    if name == "write_text_file":
        p=authorized_path(a["path"],cfg,writing=True)
        txt=a["text"]
        if len(txt.encode("utf-8"))>int(cfg["max_file_bytes"]): raise ValueError("File exceeds configured limit")
        if p.exists() and not a.get("overwrite",False): raise FileExistsError("Target exists; overwrite=true required")
        if not p.parent.is_dir(): raise FileNotFoundError("Parent directory must exist")
        # no symlink escape: resolved path is checked above
        p.write_text(txt,encoding="utf-8")
        return {"path":str(p),"bytes":len(txt.encode("utf-8"))}
    if name == "run_command":
        if not cfg["allow_shell"]: raise PermissionError("Shell execution disabled")
        raw=a["command"].strip()
        approved=cfg.get("shell_commands",[])
        if raw not in approved: raise PermissionError("Command not in exact-match allowlist")
        cwd=authorized_path(a["cwd"],cfg)
        if not cwd.is_dir(): raise ValueError("cwd must be a directory")
        # no shell=True; command must be exact allowlist entry
        args=shlex.split(raw,posix=(os.name!="nt"))
        proc=subprocess.run(args,cwd=str(cwd),capture_output=True,text=True,errors="replace",
                            timeout=min(max(int(a.get("timeout_seconds",15)),1),30),
                            stdin=subprocess.DEVNULL,env={k:v for k,v in os.environ.items()
                            if not any(t in k.lower() for t in ("token","secret","password","key"))})
        return {"exit_code":proc.returncode,"stdout":proc.stdout[:MAX_OUTPUT],
                "stderr":proc.stderr[:MAX_OUTPUT],"truncated":len(proc.stdout)>MAX_OUTPUT or len(proc.stderr)>MAX_OUTPUT}
    if name == "capture_screen":
        if not cfg["allow_screen"]: raise PermissionError("Screen capture disabled")
        try:
            from PIL import ImageGrab
            import io
        except ImportError: raise RuntimeError("Optional screen dependency missing: pip install pillow")
        img=ImageGrab.grab(all_screens=False)
        img.thumbnail((1280,800))
        stream=io.BytesIO()
        img.save(stream,format="PNG")
        return {"mime":"image/png","base64":base64.b64encode(stream.getvalue()).decode(),
                "width":img.width,"height":img.height}
    if name == "gui_click":
        if not cfg["allow_gui"]: raise PermissionError("GUI input disabled")
        try: import pyautogui
        except ImportError: raise RuntimeError("Optional GUI dependency missing: pip install pyautogui")
        x,y=int(a["x"]),int(a["y"])
        width,height=pyautogui.size()
        if not (0<=x<width and 0<=y<height): raise ValueError("Coordinates outside primary screen")
        pyautogui.FAILSAFE=True
        pyautogui.click(x=x,y=y)
        return {"clicked":[x,y]}
    if name in {"browser_navigate","browser_snapshot","browser_click","browser_screenshot"}:
        from browser_agent import perform
        return perform(name,a,cfg)
    raise ValueError("Unknown tool")

def tool(name, description, properties=None, required=None, read_only=True):
    return {"name":name, "description":description,
            "annotations":{"readOnlyHint":read_only,"destructiveHint":not read_only,
                           "openWorldHint":name in {"browser_open"}},
            "inputSchema":{"type":"object","properties":properties or {},
                           "required":required or [],"additionalProperties":False}}

PATH={"path":{"type":"string","description":"Absolute path under configured approved roots"}}
TOOLS=[
 tool("desktop_status","Return desktop hostname, roots, and enabled capabilities"),
 tool("list_directory","List up to 200 entries in a permitted folder",PATH,["path"]),
 tool("read_text_file","Read a UTF-8 file within configured size limits",PATH,["path"]),
 tool("write_text_file","Write a UTF-8 file; disabled by default; no overwrite without explicit flag",
      {**PATH,"text":{"type":"string"},"overwrite":{"type":"boolean"}},["path","text"],False),
 tool("run_command","Run only an exact allowlisted shell-free command; disabled by default",
      {"command":{"type":"string"},"cwd":{"type":"string"},"timeout_seconds":{"type":"integer"}},
      ["command","cwd"],False),
 tool("capture_screen","Capture primary desktop as PNG; requires explicit opt-in",read_only=True),
 tool("gui_click","Click primary desktop screen coordinates; requires explicit opt-in",
      {"x":{"type":"integer"},"y":{"type":"integer"}},["x","y"],False),
 tool("browser_navigate","Open allowlisted HTTPS URL in persistent headless browser",
      {"url":{"type":"string"}},["url"],True),
 tool("browser_snapshot","Read the visible browser page text",read_only=True),
 tool("browser_click","Click browser element by CSS selector; requires gui+browser capabilities",
      {"selector":{"type":"string"}},["selector"],False),
 tool("browser_screenshot","Capture the current browser viewport as an image",read_only=True)
]
