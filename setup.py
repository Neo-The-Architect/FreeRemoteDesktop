"""Configure MCP clients with preview, backup, install and uninstall commands."""
from __future__ import annotations
import argparse, json, os, pathlib, shutil, sys, time
from core import APP, CONFIG, defaults
BASE=pathlib.Path(__file__).resolve().parent
SERVER=BASE/"server.py"
HOME=pathlib.Path.home()

def codex_path():
    return HOME / ".codex" / "config.toml"

def claude_desktop_path():
    if os.name=="nt":
        return pathlib.Path(os.environ.get("APPDATA",str(HOME/"AppData"/"Roaming"))) / "Claude" / "claude_desktop_config.json"
    if sys.platform=="darwin":
        return HOME/"Library"/"Application Support"/"Claude"/"claude_desktop_config.json"
    return HOME/".config"/"Claude"/"claude_desktop_config.json"

def quoted(s):
    return json.dumps(str(s),ensure_ascii=False)

def backup(p):
    if p.exists():
        dest=p.with_suffix(p.suffix+".backup-"+time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(p,dest)
        print("Backup:",dest)

def init_config():
    if CONFIG.exists():
        print("Existing permissions unchanged:",CONFIG)
        return
    APP.mkdir(parents=True,exist_ok=True)
    CONFIG.write_text(json.dumps(defaults(),indent=2),encoding="utf-8")
    print("Created permissions config:",CONFIG)

def plan(client):
    if client=="codex":
        return f"\n[mcp_servers.freeremotedesktop]\ncommand = {quoted(sys.executable)}\nargs = [{quoted(str(SERVER))}]\n"
    if client=="claude-desktop":
        return {"command":str(sys.executable),"args":[str(SERVER)]}
    raise ValueError("Unknown client")

def install(client):
    init_config()
    if client=="codex":
        p=codex_path()
        txt=p.read_text(encoding="utf-8") if p.exists() else ""
        if "[mcp_servers.freeremotedesktop]" in txt:
            print("Already configured. To change, edit",p); return
        print("Registering Codex STDIO MCP at",p)
        backup(p);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("a",encoding="utf-8") as f:
            f.write("\n"+plan(client))
        print("Added; restart Codex.")
    elif client=="claude-desktop":
        p=claude_desktop_path()
        data=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        if "freeremotedesktop" in data.get("mcpServers",{}):
            print("Already configured:",p);return
        data.setdefault("mcpServers",{})["freeremotedesktop"]=plan(client)
        print("Registering Claude Desktop at",p)
        backup(p);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(data,indent=2),encoding="utf-8")
        print("Added; fully exit and restart Claude Desktop.")
    else:
        raise ValueError("unsupported client")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["plan","install","init"])
    p.add_argument("--client",choices=["codex","claude-desktop"],default="codex")
    args=p.parse_args()
    if args.action=="init": init_config()
    elif args.action=="plan":
        print("Client:",args.client,"Path:",codex_path() if args.client=="codex" else claude_desktop_path())
        print("Proposed registration:",plan(args.client))
        print("No changes made.")
    else: install(args.client)
if __name__=="__main__":main()
