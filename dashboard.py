"""Local desktop permission dashboard. No web server, no telemetry."""
import json, pathlib, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from core import CONFIG, APP, load
from setup import install
BG="#101923"; PANEL="#192735"; FG="#EEF4FA"; MUTED="#A8BED0"; ACC="#63C8FF"

class UI:
    def __init__(self, root):
        self.root=root
        root.title("FreeRemoteDesktop — Control Center")
        root.geometry("740x715")
        root.configure(bg=BG)
        self.config=load()
        self.flags={}
        f=tk.Frame(root,bg=BG,padx=30,pady=22);f.pack(fill="both",expand=True)
        tk.Label(f,text="FREEREMOTEDESKTOP",font=("Segoe UI",12,"bold"),fg=ACC,bg=BG).pack(anchor="w")
        tk.Label(f,text="Your computer. Your rules.",font=("Segoe UI",26,"bold"),fg=FG,bg=BG).pack(anchor="w",pady=(7,4))
        tk.Label(f,text="Local-only control panel  •  No subscription  •  MIT licensed",font=("Segoe UI",10),fg=MUTED,bg=BG).pack(anchor="w",pady=(0,18))
        card=tk.Frame(f,bg=PANEL,padx=18,pady=16);card.pack(fill="x",pady=7)
        tk.Label(card,text="APPROVED WORKSPACE",font=("Segoe UI",11,"bold"),fg=FG,bg=PANEL).pack(anchor="w")
        self.path=tk.StringVar(value=(self.config.get("roots") or [""])[0])
        entry=tk.Entry(card,textvariable=self.path,font=("Consolas",10),fg=FG,bg=BG,insertbackground=FG,relief="flat")
        entry.pack(fill="x",pady=9,ipady=7)
        tk.Button(card,text="Choose workspace folder",command=self.browse,bg="#314C61",fg=FG,relief="flat",padx=14,pady=5).pack(anchor="w")
        tk.Label(card,text="Only files in this folder are accessible. Never select your whole home folder.",fg=MUTED,bg=PANEL,font=("Segoe UI",9)).pack(anchor="w",pady=(8,0))
        card2=tk.Frame(f,bg=PANEL,padx=18,pady=15);card2.pack(fill="x",pady=7)
        tk.Label(card2,text="CAPABILITIES",font=("Segoe UI",11,"bold"),fg=FG,bg=PANEL).pack(anchor="w",pady=(0,8))
        labels=[
            ("allow_jobs","Run deterministic jobs","Model-free Git checks and approved build validation"),
            ("allow_test_execution","Execute project test code","Runs user project Python test code; trusted repos only"),
            ("allow_write","Write project files","Creates or replaces files inside the workspace"),
            ("allow_shell","Run approved commands","Only exact commands on your allowlist"),
            ("allow_screen","Capture desktop screenshots","May reveal private windows and notifications"),
            ("allow_gui","Click on desktop","Controls your mouse; keep someone supervising"),
            ("allow_browser","Headless browser","Only approved HTTPS sites; requires Playwright")]
        for key,title,description in labels:
            state=tk.BooleanVar(value=bool(self.config.get(key,False)))
            self.flags[key]=state
            row=tk.Frame(card2,bg=PANEL);row.pack(fill="x",pady=4)
            tk.Checkbutton(row,text=title,variable=state,bg=PANEL,fg=FG,selectcolor=BG,
                           activebackground=PANEL,activeforeground=FG,font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Label(row,text=description,font=("Segoe UI",9),fg=MUTED,bg=PANEL).pack(anchor="w",padx=24)
        row=tk.Frame(f,bg=BG);row.pack(fill="x",pady=17)
        tk.Button(row,text="SAVE PERMISSIONS",command=self.save,bg=ACC,fg=BG,font=("Segoe UI",10,"bold"),
                  relief="flat",padx=18,pady=11).pack(side="left",padx=(0,10))
        tk.Button(row,text="Connect Codex",command=lambda:self.connect("codex"),bg="#2C4255",fg=FG,
                  relief="flat",padx=12,pady=11).pack(side="left",padx=(0,10))
        tk.Button(row,text="Connect Claude",command=lambda:self.connect("claude-desktop"),bg="#2C4255",fg=FG,
                  relief="flat",padx=12,pady=11).pack(side="left")
        self.status=tk.StringVar(value="Read-only capabilities are available after installation.")
        tk.Label(f,textvariable=self.status,font=("Segoe UI",10),fg=ACC,bg=BG,wraplength=650).pack(anchor="w",pady=5)
    def browse(self):
        selected=filedialog.askdirectory(title="Select approved workspace")
        if selected: self.path.set(selected)
    def save(self):
        p=pathlib.Path(self.path.get()).expanduser().resolve()
        if not p.is_dir(): messagebox.showerror("Invalid path","Choose an existing workspace directory.");return
        if p==pathlib.Path.home() or p==pathlib.Path(p.anchor):
            messagebox.showerror("Unsafe scope","Choose a specific project folder, not a home or drive root.");return
        risky=[k for k,v in self.flags.items() if v.get()]
        if risky and not messagebox.askyesno("Confirm access","Allow these capabilities?\n\n"+"\n".join(risky)+"\n\nThe agent can use them without another local prompt."):
            return
        self.config["roots"]=[str(p)]
        for k,v in self.flags.items():self.config[k]=v.get()
        APP.mkdir(parents=True,exist_ok=True)
        CONFIG.write_text(json.dumps(self.config,indent=2),encoding="utf-8")
        self.status.set("Permissions saved locally. Reconnect your AI client to reload tools.")
    def connect(self,client):
        try:
            install(client)
            self.status.set(client+" registration finished. Restart that AI client.")
        except Exception as e: messagebox.showerror("Install failed",str(e))

if __name__=="__main__":
    root=tk.Tk()
    UI(root)
    root.mainloop()
