"""Standalone CLI: run deterministic engineering jobs without any AI connection."""
from __future__ import annotations
import argparse, json, pathlib, sys, time
from core import APP, CONFIG, defaults, load
from jobs import VALID, history, recipes, run

def execute(argv=None):
    p=argparse.ArgumentParser(prog="frd",description="FreeRemoteDesktop offline model-free engineering")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("status")
    sub.add_parser("recipes")
    runp=sub.add_parser("run")
    runp.add_argument("recipe",choices=sorted(VALID))
    runp.add_argument("--workspace",required=True)
    sub.add_parser("history")
    schedule=sub.add_parser("schedule")
    schedule.add_argument("recipe",choices=sorted(VALID))
    schedule.add_argument("--workspace",required=True)
    schedule.add_argument("--every-seconds",type=int,default=3600)
    schedule.add_argument("--count",type=int,default=0,help="0 means continuous until Ctrl+C")
    args=p.parse_args(argv)
    cfg=load()
    if args.command=="status":
        data={"mode":"offline","model_calls":0,"config":str(CONFIG),
              "roots":cfg["roots"],"jobs_enabled":cfg.get("allow_jobs",False)}
    elif args.command=="recipes": data=recipes()
    elif args.command=="history": data=history()
    elif args.command=="run":data=run(args.recipe,args.workspace,cfg)
    elif args.command=="schedule":
        if not cfg.get("allow_jobs"):raise PermissionError("Jobs must be enabled locally")
        if not 60<=args.every_seconds<=604800:raise ValueError("Schedule interval must be 60s–7 days")
        # Validate root and recipe before launching the loop.
        from core import authorized_path
        authorized_path(args.workspace,cfg)
        if args.count<0:raise ValueError("count must be nonnegative")
        completed=0
        print(json.dumps({"schedule":"started","recipe":args.recipe,"interval":args.every_seconds,
                          "model_calls":0}),flush=True)
        try:
            while args.count==0 or completed<args.count:
                try:
                    cfg=load()
                    if not cfg.get("allow_jobs"):break
                    data=run(args.recipe,args.workspace,cfg)
                    print(json.dumps(data,ensure_ascii=False),flush=True)
                except Exception as err:
                    print(json.dumps({"error":str(err),"model_calls":0}),file=sys.stderr,flush=True)
                    break
                completed+=1
                if args.count and completed>=args.count:break
                time.sleep(args.every_seconds)
        except KeyboardInterrupt:
            pass
        return 0
    print(json.dumps(data,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    try:
        sys.exit(execute())
    except (ValueError, PermissionError, OSError) as err:
        print(json.dumps({"error":str(err),"model_calls":0}),file=sys.stderr)
        sys.exit(1)
