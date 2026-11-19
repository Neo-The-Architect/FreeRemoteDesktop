"""Bounded text retrieval: cheap local filtering before expensive model context."""
from __future__ import annotations
import os, pathlib
from core import authorized_path, DENIED, DENIED_SUFFIX

SKIP_DIRS={".git","node_modules",".venv","venv","dist","build","__pycache__",".next"}
TEXT_EXTS={".py",".js",".jsx",".ts",".tsx",".json",".md",".txt",".toml",".yaml",
           ".yml",".css",".html",".sql",".sh",".ps1",".rs",".go",".java",".c",".cpp",".h"}
MAX_FILES=800
MAX_MATCHES=50
MAX_BYTES=100_000

def read_lines(path,start,end,cfg):
    p=authorized_path(path,cfg)
    if not p.is_file(): raise ValueError("Not a regular file")
    if p.stat().st_size>MAX_BYTES: raise ValueError("File too large for scoped read")
    start=int(start);end=int(end)
    if not (1<=start<=end<=100000) or end-start>=150:
        raise ValueError("Provide 1-based range of at most 150 lines")
    with p.open(encoding="utf-8",errors="replace") as f:
        lines=[f"{i}: {line.rstrip()}" for i,line in enumerate(f,1) if start<=i<=end]
    return {"path":str(p),"start":start,"end":end,"lines":lines}

def search_text(path,needle,cfg):
    p=authorized_path(path,cfg)
    if not p.is_dir(): raise ValueError("search path must be a directory")
    if not isinstance(needle,str) or not 2<=len(needle)<=200:
        raise ValueError("Substring length must be 2..200")
    results=[]; scanned=0; skipped=0
    walked_dirs=0
    for current, dirs, filenames in os.walk(p,topdown=True,followlinks=False):
        walked_dirs+=1
        if walked_dirs>1000 or scanned>=MAX_FILES or len(results)>=MAX_MATCHES:break
        dirs[:]=[d for d in dirs if d.lower() not in SKIP_DIRS
                 and d.lower() not in DENIED and not (pathlib.Path(current)/d).is_symlink()]
        for name in filenames:
            if len(results)>=MAX_MATCHES or scanned>=MAX_FILES:break
            if name.lower() in DENIED:skipped+=1;continue
            f=pathlib.Path(current)/name
            if f.suffix.lower() not in TEXT_EXTS:continue
            try:
                target=authorized_path(str(f),cfg)
                if target.stat().st_size>MAX_BYTES:continue
                scanned+=1
                with target.open(encoding="utf-8",errors="replace") as file:
                    for idx,line in enumerate(file,1):
                        if needle.casefold() in line.casefold():
                            results.append({"path":str(target),"line":idx,
                                            "preview":line.strip()[:220]})
                            if len(results)>=MAX_MATCHES:break
            except (PermissionError,OSError,UnicodeError):
                skipped+=1
    return {"matches":results,"scanned":scanned,"skipped":skipped,
            "truncated":len(results)>=MAX_MATCHES or scanned>=MAX_FILES,
            "model_calls":0}
