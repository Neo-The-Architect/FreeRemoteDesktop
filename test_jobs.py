import pathlib, subprocess, sys, tempfile, unittest
from core import action,defaults
from jobs import recipes,run
from server import respond

class OfflineJobsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.temp.name)
        self.cfg={**defaults(),"roots":[str(self.root)]}
    def tearDown(self):self.temp.cleanup()
    def test_default_deny(self):
        with self.assertRaises(PermissionError):
            run("python_compile",str(self.root),self.cfg)
    def test_recipe_discovery(self):
        self.assertEqual(len(recipes()["recipes"]),4)
    def test_compile(self):
        (self.root/"a.py").write_text("print('ok')\n",encoding="utf-8")
        self.cfg["allow_jobs"]=True
        r=run("python_compile",str(self.root),self.cfg)
        self.assertEqual(r["exit_code"],0,r)
        self.assertEqual(r["model_calls"],0)
    def test_test_code_needs_separate_consent(self):
        self.cfg["allow_jobs"]=True
        with self.assertRaises(PermissionError):
            run("python_tests",str(self.root),self.cfg)
    def test_git_nonrepo_denied(self):
        self.cfg["allow_jobs"]=True
        with self.assertRaises(ValueError):
            run("git_status",str(self.root),self.cfg)
    def test_tool_schema(self):
        names=[x["name"] for x in respond({"jsonrpc":"2.0","id":1,"method":"tools/list"})["result"]["tools"]]
        self.assertIn("run_job",names)
        self.assertIn("job_history",names)
    def test_cli_no_ai(self):
        root=pathlib.Path(__file__).parent
        p=subprocess.run([sys.executable,str(root/"frd.py"),"recipes"],
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("python_compile",p.stdout)

if __name__=="__main__":unittest.main(verbosity=2)
