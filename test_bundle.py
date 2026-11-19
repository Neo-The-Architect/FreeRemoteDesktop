import json, os, pathlib, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parent

class BundleTests(unittest.TestCase):
    def test_mcpb_files(self):
        import zipfile
        path=ROOT/"FreeRemoteDesktop-0.2.1.mcpb"
        if not path.exists(): self.skipTest("Run python pack_mcpb.py first")
        with zipfile.ZipFile(path) as z:
            self.assertTrue({"manifest.json","server.py","core.py","browser_agent.py","pyproject.toml"}.issubset(z.namelist()))
    def test_uv_stdio_and_root_override(self):
        with tempfile.TemporaryDirectory() as temp:
            env={**os.environ,"FRD_APPROVED_ROOT":temp}
            msgs=[{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}},
                  {"jsonrpc":"2.0","id":2,"method":"tools/call",
                   "params":{"name":"desktop_status","arguments":{}}}]
            p=subprocess.run(["uv","run","--project",str(ROOT),"python",str(ROOT/"server.py")],
                             input="\n".join(map(json.dumps,msgs))+"\n",
                             capture_output=True,text=True,timeout=90,env=env)
            self.assertEqual(p.returncode,0,p.stderr)
            outputs=[json.loads(line) for line in p.stdout.splitlines()]
            self.assertEqual(len(outputs),2)
            cfg=json.loads(outputs[1]["result"]["content"][0]["text"])
            self.assertEqual([str(pathlib.Path(temp).resolve())],cfg["roots"])
if __name__=="__main__":unittest.main(verbosity=2)
