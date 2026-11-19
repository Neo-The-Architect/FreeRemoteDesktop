import json, pathlib, unittest
from unittest.mock import patch
from local_studio import Studio, Handler, BASE

class StudioTests(unittest.TestCase):
    def test_source_assets(self):
        for name in ("studio.html","studio.js","style.css"):
            self.assertTrue((BASE/name).is_file(),name)
        self.assertIn("Engineering Studio",(BASE/"studio.html").read_text(encoding="utf-8"))
    def test_missing_model_rejected(self):
        studio=Studio()
        with patch.object(studio,"available_models",return_value=[]):
            with self.assertRaises(ValueError):
                studio.reply("hello","nonexistent")
    def test_local_response_no_tools(self):
        studio=Studio()
        with patch.object(studio,"available_models",return_value=["mock:latest"]),\
             patch.object(studio,"ask_ollama",return_value={"role":"assistant","content":"Local response"}):
            out=studio.reply("hi","mock:latest")
        self.assertEqual(out["reply"],"Local response")
        self.assertEqual(out["model"],"local:mock:latest")
    def test_model_proposes_write_does_not_execute(self):
        studio=Studio()
        response={"role":"assistant","content":"Need approval",
                  "tool_calls":[{"function":{"name":"write_text_file",
                     "arguments":{"path":"C:/sensitive.txt","text":"untrusted"}}}]}
        with patch.object(studio,"available_models",return_value=["mock:latest"]),\
             patch.object(studio,"ask_ollama",return_value=response),\
             patch("local_studio.result",side_effect=AssertionError("must not run")):
            out=studio.reply("write sensitive file","mock:latest")
        self.assertEqual(len(out["proposed"]),1)
        self.assertIn(out["proposed"][0]["id"],studio.pending)
    def test_approval_runs_capability_policy(self):
        studio=Studio()
        studio.pending["approved"]={"name":"write_text_file",
                                   "arguments":{"path":"C:/sensitive.txt","text":"untrusted"}}
        out=studio.approve("approved")
        self.assertTrue(out["result"]["isError"])
        with self.assertRaises(ValueError): studio.approve("approved")
    def test_read_tools_auto(self):
        studio=Studio()
        responses=iter([
            {"role":"assistant","content":"","tool_calls":[{"function":{"name":"desktop_status","arguments":{}}}]},
            {"role":"assistant","content":"Read done"}])
        with patch.object(studio,"available_models",return_value=["mock:latest"]),\
             patch.object(studio,"ask_ollama",side_effect=lambda *args:next(responses)):
            out=studio.reply("check","mock:latest")
        self.assertEqual(out["reply"],"Read done")
    def test_max_request(self):
        studio=Studio()
        with self.assertRaises(ValueError):studio.reply("z"*9000,"x")

if __name__=="__main__":unittest.main(verbosity=2)
