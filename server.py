"""MCP transport: local STDIO by default; opt-in loopback HTTP with bearer auth."""
from __future__ import annotations
import argparse, hmac, http.server, json, os, pathlib, secrets, sys
from core import APP, CONFIG, TOOLS, result

VERSION="2025-03-26"
def respond(message):
    if not isinstance(message,dict): return {"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Invalid request"}}
    if "id" not in message: return None
    ident=message["id"]
    method=message.get("method")
    if method=="initialize":
        value={"protocolVersion":VERSION,"capabilities":{"tools":{"listChanged":False}},
               "serverInfo":{"name":"FreeRemoteDesktop","version":"0.3.0"}}
    elif method=="ping":
        value={}
    elif method=="tools/list":
        value={"tools":TOOLS}
    elif method=="tools/call":
        params=message.get("params") or {}
        value=result(params.get("name",""),params.get("arguments") or {})
    else:
        return {"jsonrpc":"2.0","id":ident,"error":{"code":-32601,"message":"Method not found"}}
    return {"jsonrpc":"2.0","id":ident,"result":value}

def stdio():
    for line in sys.stdin:
        try:
            out=respond(json.loads(line))
            if out is not None:
                sys.stdout.write(json.dumps(out,ensure_ascii=False,separators=(",",":"))+"\n")
                sys.stdout.flush()
        except Exception as err:
            print("Request rejected: "+str(err),file=sys.stderr,flush=True)

class Handler(http.server.BaseHTTPRequestHandler):
    token=""
    server_version="FreeRemoteDesktop/0.3.0"
    def do_POST(self):
        if self.path!="/mcp":
            return self.send_error(404)
        if not hmac.compare_digest(self.headers.get("Authorization",""),"Bearer "+self.token):
            return self.send_error(401)
        if "application/json" not in self.headers.get("Content-Type",""):
            return self.send_error(415)
        try:
            size=int(self.headers.get("Content-Length","0"))
            if size<1 or size>256000: return self.send_error(413)
            request=json.loads(self.rfile.read(size))
            answer=respond(request)
            if answer is None:
                self.send_response(202); self.end_headers(); return
            body=json.dumps(answer,separators=(",",":")).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)))
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            self.wfile.write(body)
        except (ValueError,TypeError,json.JSONDecodeError):
            self.send_error(400)
    def do_GET(self):
        self.send_error(405)
    def log_message(self,fmt,*args):
        pass

def serve(port):
    token=os.environ.get("FRD_BEARER_TOKEN")
    if not token or len(token)<32:
        raise SystemExit("FRD_BEARER_TOKEN must be set to a secret of at least 32 characters")
    Handler.token=token
    # Always loopback; no public binding or bypass of authentication.
    with http.server.ThreadingHTTPServer(("127.0.0.1",port),Handler) as server:
        print("FreeRemoteDesktop bound to 127.0.0.1:"+str(port),file=sys.stderr,flush=True)
        server.serve_forever()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--transport",choices=["stdio","http"],default="stdio")
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    if args.transport=="stdio": stdio()
    else: serve(args.port)
if __name__=="__main__": main()
