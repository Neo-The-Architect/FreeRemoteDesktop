"""Reproducible source bundle for MCPB-compatible hosts."""
import json, pathlib, zipfile
root=pathlib.Path(__file__).parent
required=["manifest.json","pyproject.toml","server.py","core.py","browser_agent.py","jobs.py","retrieval.py","frd.py","local_studio.py","studio.html","studio.js","style.css","LICENSE","README.md","SECURITY.md"]
manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
assert manifest["name"]=="freeremotedesktop"
out=root/"FreeRemoteDesktop-0.3.0.mcpb"
with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
    for f in required:
        z.write(root/f,arcname=f)
print("Built",out,"size",out.stat().st_size,"bytes")
