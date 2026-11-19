import json, os, pathlib, subprocess, sys, tempfile, unittest
from unittest.mock import patch
from core import action, defaults, result, authorized_path
from server import respond
BASE=pathlib.Path(__file__).parent

class ProductTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.tmp.name)
        self.cfg={**defaults(),"roots":[str(self.root)]}
        (self.root/"hello.txt").write_text("hello","utf-8")
    def tearDown(self): self.tmp.cleanup()
    def test_initialize(self):
        r=respond({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}})
        self.assertEqual(r["result"]["serverInfo"]["name"],"FreeRemoteDesktop")
    def test_tools(self):
        self.assertEqual(len(respond({"jsonrpc":"2.0","id":2,"method":"tools/list"})["result"]["tools"]),19)
    def test_read(self):
        self.assertEqual(action("read_text_file",{"path":str(self.root/"hello.txt")},self.cfg)["text"],"hello")
    def test_list(self):
        self.assertEqual(action("list_directory",{"path":str(self.root)},self.cfg)["entries"][0]["name"],"hello.txt")
    def test_traversal(self):
        with self.assertRaises(PermissionError):
            authorized_path(str(self.root/".."/"elsewhere"),self.cfg)
    def test_secret_block(self):
        with self.assertRaises(PermissionError):
            authorized_path(str(self.root/".env"),self.cfg)
    def test_write_disabled(self):
        with self.assertRaises(PermissionError):
            action("write_text_file",{"path":str(self.root/"new"),"text":"a"},self.cfg)
    def test_write_enabled_with_no_overwrite(self):
        self.cfg["allow_write"]=True
        action("write_text_file",{"path":str(self.root/"new"),"text":"a"},self.cfg)
        with self.assertRaises(FileExistsError):
            action("write_text_file",{"path":str(self.root/"new"),"text":"b"},self.cfg)
    def test_shell_disabled(self):
        with self.assertRaises(PermissionError):
            action("run_command",{"command":"git status","cwd":str(self.root)},self.cfg)
    def test_shell_denied(self):
        self.cfg["allow_shell"]=True
        with self.assertRaises(PermissionError):
            action("run_command",{"command":"python -c evil","cwd":str(self.root)},self.cfg)
    def test_screen_disabled(self):
        with self.assertRaises(PermissionError):
            action("capture_screen",{},self.cfg)
    def test_browser_disabled(self):
        with self.assertRaises(PermissionError):
            action("browser_navigate",{"url":"https://example.com"},self.cfg)
    def test_stdio(self):
        req={"jsonrpc":"2.0","id":4,"method":"tools/list"}
        p=subprocess.run([sys.executable,str(BASE/"server.py")],input=json.dumps(req)+"\n",
                         capture_output=True,text=True,timeout=8)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)["id"],4)
    def test_http_requires_auth(self):
        p=subprocess.run([sys.executable,str(BASE/"server.py"),"--transport","http"],
                         capture_output=True,text=True,timeout=8,env={k:v for k,v in os.environ.items() if k!="FRD_BEARER_TOKEN"})
        self.assertNotEqual(p.returncode,0)
        self.assertIn("FRD_BEARER_TOKEN",p.stderr)
    def test_setup_plan(self):
        p=subprocess.run([sys.executable,str(BASE/"setup.py"),"plan","--client","codex"],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("freeremotedesktop",p.stdout)

if __name__=="__main__":
    unittest.main(verbosity=2)
