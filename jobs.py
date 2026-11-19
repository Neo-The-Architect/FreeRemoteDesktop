"""Deterministic, model-free workspace jobs. Explicit opt-in; no shell or network calls."""
from __future__ import annotations
import datetime, json, os, pathlib, subprocess, sys, threading, uuid
from core import APP, authorized_path

JOBS=APP/"jobs.jsonl"
_LOCK=threading.Lock()
VALID={"git_status","git_diff_summary","python_compile","python_tests"}
OUT_LIMIT=12000
def _record(entry):
    APP.mkdir(parents=True, exist_ok=True)
    with _LOCK, JOBS.open("a",encoding="utf-8") as f:
        f.write(json.dumps(entry,ensure_ascii=False)+"\n")

def run(recipe, workspace, cfg):
    if not cfg.get("allow_jobs",False):
        raise PermissionError("Deterministic jobs are disabled; enable allow_jobs locally")
    if recipe not in VALID:
        raise ValueError("Unknown job recipe")
    root=authorized_path(workspace,cfg)
    if not root.is_dir():raise ValueError("Workspace does not exist")
    if not (root/".git").exists() and recipe.startswith("git_"):
        raise ValueError("Not a Git repository")
    if recipe=="git_status": argv=["git","status","--short","--untracked-files=no"]
    elif recipe=="git_diff_summary": argv=["git","diff","--stat"]
    elif recipe=="python_compile": argv=[sys.executable,"-m","compileall","-q","."]
    else:
        if not cfg.get("allow_test_execution",False):
            raise PermissionError("Running workspace test code requires separate allow_test_execution")
        argv=[sys.executable,"-m","unittest","discover","-v"]
    # Untrusted workspaces can execute through Python imports, Git config / filters,
    # or hooks. Only run jobs in trusted local workspaces under a low privilege OS user.
    env={k:v for k,v in os.environ.items() if not any(s in k.lower() for s in ("token","secret","password","api_key"))}
    env.update({"GIT_TERMINAL_PROMPT":"0","GIT_PAGER":"cat","GIT_CONFIG_NOSYSTEM":"1",
                "GIT_CONFIG_GLOBAL":os.devnull,"PYTHONNOUSERSITE":"1","PIP_DISABLE_PIP_VERSION_CHECK":"1"})
    job_id=uuid.uuid4().hex
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p=subprocess.run(argv,cwd=str(root),env=env,capture_output=True,text=True,
                         errors="replace",timeout=90,stdin=subprocess.DEVNULL,
                         creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        response={"id":job_id,"recipe":recipe,"workspace":str(root),"started":started,
                  "exit_code":p.returncode,"stdout":p.stdout[:OUT_LIMIT],"stderr":p.stderr[:OUT_LIMIT],
                  "truncated":len(p.stdout)>OUT_LIMIT or len(p.stderr)>OUT_LIMIT,"model_calls":0}
    except subprocess.TimeoutExpired:
        response={"id":job_id,"recipe":recipe,"workspace":str(root),"started":started,
                  "error":"timeout","model_calls":0}
    _record({k:v for k,v in response.items() if k not in ("stdout","stderr")})
    return response

def history(limit=20):
    if not JOBS.exists():return {"jobs":[]}
    limit=min(max(int(limit),1),100)
    with JOBS.open(encoding="utf-8") as f:
        items=[json.loads(line) for line in f if line.strip()]
    return {"jobs":items[-limit:]}

def recipes():
    return {"recipes":[{"name":n,"requires_test_execution":n=="python_tests"} for n in sorted(VALID)],
            "description":"No AI model calls. Jobs run locally; test execution is separate opt-in."}
