"""Optional OpenAI Secure MCP Tunnel onboarding; never proxies a desktop publicly."""
from __future__ import annotations
import argparse, os, pathlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
PROFILE="freeremotedesktop-local"
DOCS="https://github.com/openai/tunnel-client"
PLATFORM="https://platform.openai.com/settings/organization/tunnels"
def main(argv=None):
    parser=argparse.ArgumentParser(description="Set up private outbound-only MCP connectivity for eligible ChatGPT workspaces")
    parser.add_argument("action",choices=["plan","init","doctor","run"],default="plan",nargs="?")
    args=parser.parse_args(argv)
    command=shutil.which("tunnel-client")
    tunnel_id=os.environ.get("CONTROL_PLANE_TUNNEL_ID","")
    key=os.environ.get("CONTROL_PLANE_API_KEY","")
    server=f'"{sys.executable}" "{ROOT/"server.py"}"'
    if args.action=="plan":
        print("FreeRemoteDesktop private ChatGPT connection plan")
        print("1. Install official tunnel-client:",DOCS)
        print("2. Obtain tunnel ID (correct workspace scope):",PLATFORM)
        print("3. Set CONTROL_PLANE_TUNNEL_ID and CONTROL_PLANE_API_KEY securely")
        print("4. Run: python connect_chatgpt.py init")
        print("5. Run: python connect_chatgpt.py doctor")
        print("6. Run: python connect_chatgpt.py run (foreground only)")
        print("7. Add MCP connection from ChatGPT Plugins using Tunnel; workspace permissions apply.")
        print("Binary present:",bool(command),"Tunnel ID present:",bool(tunnel_id),"Runtime key present:",bool(key))
        print("No changes made, no background process started.")
        return 0
    if not command:raise RuntimeError("Install official tunnel-client first: "+DOCS)
    if not tunnel_id.startswith("tunnel_") or not key:
        raise RuntimeError("Set CONTROL_PLANE_TUNNEL_ID and CONTROL_PLANE_API_KEY; do not paste keys into chat.")
    if args.action=="init":
        argv=[command,"init","--sample","sample_mcp_stdio_local",
              "--profile",PROFILE,"--tunnel-id",tunnel_id,"--mcp-command",server]
    elif args.action=="doctor":
        argv=[command,"doctor","--profile",PROFILE,"--explain"]
    else:
        argv=[command,"run","--profile",PROFILE]
    return subprocess.call(argv)
if __name__=="__main__":
    try:sys.exit(main())
    except (RuntimeError,OSError) as err:
        print("ERROR:",err,file=sys.stderr)
        sys.exit(1)
