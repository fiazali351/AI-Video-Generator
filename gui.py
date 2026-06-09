#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, sys, threading, tkinter as tk, os, re, tempfile
from tkinter import ttk, scrolledtext, messagebox, filedialog

BG="#0d0d0d"; CARD="#1a1a1a"; ACCENT="#ff4444"; TEXT="#ffffff"
SUBTEXT="#888888"; SUCCESS="#00cc66"; BORDER="#2a2a2a"; BLUE="#4488ff"; YELLOW="#ffcc00"
WPM=140

class App:
    def __init__(self, root):
        self.root=root; self.root.title("AI Video Generator")
        self.root.geometry("1100x780"); self.root.configure(bg=BG)
        self.process=None; self.script_path=None
        self.mode=tk.StringVar(value="topic")
        self._ui()

    def _ui(self):
        # Header
        h=tk.Frame(self.root,bg=BG,pady=12); h.pack(fill="x",padx=30)
        tk.Label(h,text="AI Video Generator",font=("Segoe UI",20,"bold"),bg=BG,fg=TEXT).pack(side="left")
        tk.Label(h,text="  |  Generate YouTube videos from any topic!",font=("Segoe UI",10),bg=BG,fg=SUBTEXT).pack(side="left")
        tk.Label(h,text="Created by Fiaz Shah",font=("Segoe UI",9,"italic"),bg=BG,fg=ACCENT).pack(side="right")
        tk.Frame(self.root,bg=BORDER,height=1).pack(fill="x",padx=30)

        main=tk.Frame(self.root,bg=BG); main.pack(fill="both",expand=True,padx=20,pady=10)

        lo=tk.Frame(main,bg=BG,width=460); lo.pack(side="left",fill="y",padx=(0,15)); lo.pack_propagate(False)
        canvas=tk.Canvas(lo,bg=BG,highlightthickness=0,width=440)
        sb=ttk.Scrollbar(lo,orient="vertical",command=canvas.yview); sb.pack(side="right",fill="y")
        canvas.configure(yscrollcommand=sb.set); canvas.pack(side="left",fill="both",expand=True)
        self.left=tk.Frame(canvas,bg=BG)
        win=canvas.create_window((0,0),window=self.left,anchor="nw")
        self.left.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(win,width=e.width))
        canvas.bind_all("<MouseWheel>",lambda e:canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        L=self.left

        # Tabs
        mf=tk.Frame(L,bg=BORDER,padx=2,pady=2); mf.pack(fill="x",pady=(0,12),padx=5)
        self.btn_topic=tk.Button(mf,text="Topic to Video",font=("Segoe UI",9,"bold"),relief="flat",bg=ACCENT,fg=TEXT,padx=8,pady=7,cursor="hand2",command=lambda:self._tab("topic"))
        self.btn_topic.pack(side="left",fill="x",expand=True)
        self.btn_write=tk.Button(mf,text="Write Script",font=("Segoe UI",9,"bold"),relief="flat",bg=CARD,fg=SUBTEXT,padx=8,pady=7,cursor="hand2",command=lambda:self._tab("write"))
        self.btn_write.pack(side="left",fill="x",expand=True)
        self.btn_upload=tk.Button(mf,text="Upload Script",font=("Segoe UI",9,"bold"),relief="flat",bg=CARD,fg=SUBTEXT,padx=8,pady=7,cursor="hand2",command=lambda:self._tab("upload"))
        self.btn_upload.pack(side="left",fill="x",expand=True)

        self.ic=tk.Frame(L,bg=BG); self.ic.pack(fill="x",padx=5)

        # Panel: Topic
        self.p_topic=tk.Frame(self.ic,bg=BG)
        tk.Label(self.p_topic,text="Video Title (Optional):",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",pady=(0,3))
        self.title_var=tk.StringVar()
        tk.Entry(self.p_topic,textvariable=self.title_var,font=("Segoe UI",11),bg=CARD,fg=TEXT,insertbackground=TEXT,relief="flat",highlightthickness=1,highlightcolor=ACCENT,highlightbackground=BORDER).pack(fill="x",ipady=7,pady=(0,8))
        tk.Label(self.p_topic,text="Enter Video Topic:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",pady=(0,3))
        self.topic_var=tk.StringVar()
        te=tk.Entry(self.p_topic,textvariable=self.topic_var,font=("Segoe UI",11),bg=CARD,fg=TEXT,insertbackground=TEXT,relief="flat",highlightthickness=1,highlightcolor=ACCENT,highlightbackground=BORDER)
        te.pack(fill="x",ipady=7,pady=(0,5)); te.insert(0,"10 Amazing Facts About Space")
        ef=tk.Frame(self.p_topic,bg=BG); ef.pack(fill="x",pady=(0,8))
        tk.Label(ef,text="Examples:",font=("Segoe UI",8),bg=BG,fg=SUBTEXT).pack(anchor="w")
        for ex in ["History of Pakistan","How AI Works","Amazing Animals"]:
            tk.Button(ef,text=ex,font=("Segoe UI",8),bg=BORDER,fg=SUBTEXT,relief="flat",cursor="hand2",padx=6,pady=2,command=lambda e=ex:self.topic_var.set(e)).pack(side="left",padx=(0,4),pady=2)

        # Panel: Write
        self.p_write=tk.Frame(self.ic,bg=BG)
        tk.Label(self.p_write,text="Video Title:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",pady=(0,3))
        self.write_title=tk.StringVar()
        tk.Entry(self.p_write,textvariable=self.write_title,font=("Segoe UI",11),bg=CARD,fg=TEXT,insertbackground=TEXT,relief="flat",highlightthickness=1,highlightcolor=ACCENT,highlightbackground=BORDER).pack(fill="x",ipady=7,pady=(0,8))
        ib=tk.Frame(self.p_write,bg=CARD,padx=8,pady=5); ib.pack(fill="x",pady=(0,4))
        tk.Label(ib,text="Words:",font=("Segoe UI",9),bg=CARD,fg=SUBTEXT).pack(side="left")
        self.wc=tk.Label(ib,text="0",font=("Segoe UI",9,"bold"),bg=CARD,fg=YELLOW); self.wc.pack(side="left",padx=(3,12))
        tk.Label(ib,text="Est.Time:",font=("Segoe UI",9),bg=CARD,fg=SUBTEXT).pack(side="left")
        self.dur_lbl=tk.Label(ib,text="0:00",font=("Segoe UI",9,"bold"),bg=CARD,fg=SUCCESS); self.dur_lbl.pack(side="left",padx=(3,0))
        tk.Label(ib,text="Max: 700w = 5min",font=("Segoe UI",8),bg=CARD,fg=SUBTEXT).pack(side="right")
        tk.Label(self.p_write,text="Write Your Script:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",pady=(0,3))
        self.stext=tk.Text(self.p_write,font=("Segoe UI",10),bg=CARD,fg=TEXT,insertbackground=TEXT,relief="flat",height=8,wrap="word",padx=8,pady=8)
        self.stext.pack(fill="x",pady=(0,4)); self.stext.bind("<KeyRelease>",self._wc)
        self.stext.insert("1.0","Write your script here...\n\nEach paragraph becomes a separate section.")
        gf=tk.Frame(self.p_write,bg=BG); gf.pack(fill="x",pady=(0,8))
        for d,w in [("1min","~140w"),("3min","~420w"),("5min","~700w"),("10min","~1400w")]:
            f=tk.Frame(gf,bg=BORDER,padx=6,pady=3); f.pack(side="left",padx=(0,4))
            tk.Label(f,text=d,font=("Segoe UI",8,"bold"),bg=BORDER,fg=ACCENT).pack()
            tk.Label(f,text=w,font=("Segoe UI",7),bg=BORDER,fg=SUBTEXT).pack()

        # Panel: Upload
        self.p_upload=tk.Frame(self.ic,bg=BG)
        tk.Label(self.p_upload,text="Select Script File:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",pady=(0,3))
        fr=tk.Frame(self.p_upload,bg=BG); fr.pack(fill="x",pady=(0,5))
        self.flbl=tk.Label(fr,text="No file selected...",font=("Segoe UI",9),bg=CARD,fg=SUBTEXT,anchor="w",padx=8)
        self.flbl.pack(side="left",fill="x",expand=True,ipady=8)
        tk.Button(fr,text="Browse",font=("Segoe UI",9,"bold"),bg=ACCENT,fg=TEXT,relief="flat",cursor="hand2",padx=12,pady=4,command=self._browse).pack(side="right",padx=(5,0))
        tk.Label(self.p_upload,text="Supported: .txt or .json",font=("Segoe UI",8),bg=BG,fg=SUBTEXT).pack(anchor="w",pady=(0,8))

        self.p_topic.pack(fill="x")

        tk.Frame(L,bg=BORDER,height=1).pack(fill="x",padx=5,pady=8)

        # Video Format
        tk.Label(L,text="Video Format:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",padx=5,pady=(0,4))
        ff=tk.Frame(L,bg=CARD,padx=8,pady=6); ff.pack(fill="x",padx=5,pady=(0,8))
        self.format_var=tk.StringVar(value="landscape")
        tk.Radiobutton(ff,text="Landscape 16:9 (YouTube)",variable=self.format_var,value="landscape",font=("Segoe UI",9),bg=CARD,fg=TEXT,selectcolor=BG,activebackground=CARD,cursor="hand2").pack(side="left",padx=(0,15))
        tk.Radiobutton(ff,text="Portrait 9:16 (Shorts)",variable=self.format_var,value="portrait",font=("Segoe UI",9),bg=CARD,fg=TEXT,selectcolor=BG,activebackground=CARD,cursor="hand2").pack(side="left")

        # Duration
        tk.Label(L,text="Video Duration:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",padx=5,pady=(0,4))
        df=tk.Frame(L,bg=CARD,padx=8,pady=6); df.pack(fill="x",padx=5,pady=(0,8))
        self.dur_var=tk.StringVar(value="auto")
        for lbl,val in [("Auto","auto"),("1 min","1"),("3 min","3"),("5 min","5"),("10 min","10"),("15 min","15")]:
            tk.Radiobutton(df,text=lbl,variable=self.dur_var,value=val,font=("Segoe UI",9),bg=CARD,fg=TEXT,selectcolor=BG,activebackground=CARD,cursor="hand2").pack(side="left",padx=4)

        # Language
        tk.Label(L,text="Language:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",padx=5,pady=(0,4))
        lf=tk.Frame(L,bg=CARD,padx=8,pady=6); lf.pack(fill="x",padx=5,pady=(0,8))
        self.lang_var=tk.StringVar(value="en")
        tk.Radiobutton(lf,text="English",variable=self.lang_var,value="en",font=("Segoe UI",9),bg=CARD,fg=TEXT,selectcolor=BG,activebackground=CARD,cursor="hand2").pack(side="left",padx=8)

        # Voice
        tk.Label(L,text="Voice:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",padx=5,pady=(0,4))
        vf=tk.Frame(L,bg=CARD,padx=8,pady=6); vf.pack(fill="x",padx=5,pady=(0,8))
        tk.Label(vf,text="Male - Christopher Neural",font=("Segoe UI",9),bg=CARD,fg=SUCCESS).pack(side="left",padx=8)

        # Output
        tk.Label(L,text="Output File Name:",font=("Segoe UI",10,"bold"),bg=BG,fg=TEXT).pack(anchor="w",padx=5,pady=(0,4))
        self.out_var=tk.StringVar(value="my_video.mp4")
        tk.Entry(L,textvariable=self.out_var,font=("Segoe UI",10),bg=CARD,fg=TEXT,insertbackground=TEXT,relief="flat",highlightthickness=1,highlightcolor=ACCENT,highlightbackground=BORDER).pack(fill="x",ipady=7,padx=5,pady=(0,12))

        # Buttons
        self.gen_btn=tk.Button(L,text="GENERATE VIDEO",font=("Segoe UI",13,"bold"),bg=ACCENT,fg=TEXT,relief="flat",cursor="hand2",pady=13,command=self._generate)
        self.gen_btn.pack(fill="x",padx=5,pady=(0,6))
        br=tk.Frame(L,bg=BG); br.pack(fill="x",padx=5)
        self.stop_btn=tk.Button(br,text="Stop",font=("Segoe UI",10),bg=BORDER,fg=SUBTEXT,relief="flat",cursor="hand2",pady=7,state="disabled",command=self._stop)
        self.stop_btn.pack(side="left",fill="x",expand=True,padx=(0,4))
        tk.Button(br,text="Output Folder",font=("Segoe UI",10),bg=CARD,fg=SUBTEXT,relief="flat",cursor="hand2",pady=7,command=self._open_out).pack(side="left",fill="x",expand=True)

        # Console
        right=tk.Frame(main,bg=BG); right.pack(side="left",fill="both",expand=True)
        ch=tk.Frame(right,bg=CARD,pady=10,padx=15); ch.pack(fill="x")
        tk.Label(ch,text="Live Progress",font=("Segoe UI",11,"bold"),bg=CARD,fg=TEXT).pack(side="left")
        tk.Button(ch,text="Clear",font=("Segoe UI",9),bg=CARD,fg=SUBTEXT,relief="flat",cursor="hand2",command=self._clear).pack(side="right")
        self.con=scrolledtext.ScrolledText(right,font=("Consolas",10),bg="#0a0a0a",fg="#00ff88",insertbackground=TEXT,relief="flat",pady=10,padx=10,wrap="word",state="disabled")
        self.con.pack(fill="both",expand=True)
        self.con.tag_config("s",foreground=SUCCESS); self.con.tag_config("e",foreground="#ff4444")
        self.con.tag_config("i",foreground=BLUE);    self.con.tag_config("h",foreground=ACCENT)
        self.con.tag_config("n",foreground="#00ff88")

        # Status bar
        sb2=tk.Frame(self.root,bg=CARD,pady=8); sb2.pack(fill="x",side="bottom")
        self.status=tk.StringVar(value="Ready!")
        tk.Label(sb2,textvariable=self.status,font=("Segoe UI",9),bg=CARD,fg=SUBTEXT).pack(side="left",padx=15)
        self.pct_label=tk.Label(sb2,text="",font=("Segoe UI",9,"bold"),bg=CARD,fg=ACCENT)
        self.pct_label.pack(side="right",padx=5)
        self.prog=ttk.Progressbar(sb2,mode="determinate",length=200,maximum=100)
        self.prog.pack(side="right",padx=10)

        self._log("Welcome to AI Video Generator!\n","h")
        self._log("Enter a topic, write a script, or upload a script file!\n","i")
        self._log("-"*50+"\n","n")

    def _tab(self,mode):
        self.mode.set(mode)
        for k,b in [("topic",self.btn_topic),("write",self.btn_write),("upload",self.btn_upload)]:
            b.config(bg=ACCENT if k==mode else CARD, fg=TEXT if k==mode else SUBTEXT)
        for k,p in [("topic",self.p_topic),("write",self.p_write),("upload",self.p_upload)]:
            p.pack(fill="x") if k==mode else p.pack_forget()

    def _wc(self,e=None):
        t=self.stext.get("1.0","end").strip()
        w=len(t.split()) if t else 0
        s=(w/WPM)*60; m,sc=int(s//60),int(s%60)
        self.wc.config(text=str(w),fg="#ff4444" if w>1400 else YELLOW if w>700 else SUCCESS)
        self.dur_lbl.config(text=f"{m}:{sc:02d}")

    def _browse(self):
        p=filedialog.askopenfilename(title="Select script file",filetypes=[("Text/JSON","*.txt *.json"),("All","*.*")])
        if p:
            self.script_path=p
            self.flbl.config(text=os.path.basename(p),fg=SUCCESS)

    def _log(self,text,tag="n"):
        self.con.config(state="normal"); self.con.insert("end",text,tag)
        self.con.see("end"); self.con.config(state="disabled")

    def _clear(self):
        self.con.config(state="normal"); self.con.delete("1.0","end"); self.con.config(state="disabled")

    def _open_out(self):
        d=os.path.join(os.path.dirname(os.path.abspath(__file__)),"output")
        os.makedirs(d,exist_ok=True); os.startfile(d)

    def _generate(self):
        mode=self.mode.get(); tmp=None
        if mode=="topic":
            if not self.topic_var.get().strip():
                messagebox.showwarning("Topic Required!","Please enter a topic first!"); return
        elif mode=="write":
            txt=self.stext.get("1.0","end").strip()
            if not txt or "Write your script" in txt:
                messagebox.showwarning("Script Required!","Please write a script first!"); return
            title=self.write_title.get().strip() or "My Video"
            t=tempfile.NamedTemporaryFile(mode="w",suffix=".txt",delete=False,encoding="utf-8")
            t.write(f"# {title}\n\n{txt}"); t.close(); tmp=t.name
        else:
            if not self.script_path:
                messagebox.showwarning("Script Required!","Please select a file first!"); return

        out=self.out_var.get().strip() or "my_video.mp4"
        if not out.endswith(".mp4"): out+=".mp4"

        self._update_config()

        lang=self.lang_var.get()
        dur=self.dur_var.get()
        dur_m="0" if dur=="auto" else dur

        import sys
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        mp=os.path.join(base_path,"main.py")
        cmd=[sys.executable,"-u",mp,"--output",out,"--duration",dur_m,"--lang",lang,"--gender","male"]

        if mode=="topic":
            cmd+=["--topic",self.topic_var.get().strip()]
        elif mode=="write":
            cmd+=["--script",tmp]
        else:
            cmd+=["--script",self.script_path]

        self.gen_btn.config(state="disabled",text="Generating...",bg=SUBTEXT)
        self.stop_btn.config(state="normal")
        self.prog["value"]=0; self.pct_label.config(text="0%")
        self.status.set("Starting video generation...")
        self._clear()
        threading.Thread(target=self._run,args=(cmd,tmp),daemon=True).start()

    def _update_config(self):
        try:
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.py")
            c=open(path).read()
            fmt=self.format_var.get()
            if fmt=="portrait":
                c=re.sub(r'VIDEO_WIDTH\s*=\s*\d+','VIDEO_WIDTH  = 1080',c)
                c=re.sub(r'VIDEO_HEIGHT\s*=\s*\d+','VIDEO_HEIGHT = 1920',c)
            else:
                c=re.sub(r'VIDEO_WIDTH\s*=\s*\d+','VIDEO_WIDTH  = 1280',c)
                c=re.sub(r'VIDEO_HEIGHT\s*=\s*\d+','VIDEO_HEIGHT = 720',c)
            open(path,"w").write(c)
        except: pass

    def _run(self,cmd,tmp=None):
        steps={"STEP 1":1,"STEP 2":2,"STEP 3":3,"STEP 4":4}
        total=4
        try:
            self.process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                text=True,encoding="utf-8",errors="replace",
                cwd=os.path.dirname(os.path.abspath(__file__)))
            for line in self.process.stdout:
                line=line.rstrip()
                if not line: continue
                tag="n"
                if any(x in line for x in ["done","generated","downloaded","CREATED","VIDEO"]): tag="s"
                elif any(x in line for x in ["Error","error","failed","Failed"]): tag="e"
                elif any(x in line for x in ["STEP","==="]): tag="h"
                self.root.after(0,self._log,line+"\n",tag)
                for sn,sv in steps.items():
                    if sn in line:
                        pct=int((sv/total)*100)
                        self.root.after(0,lambda p=pct,s=sn:self._set_progress(p,s))
            self.process.wait()
            self.root.after(0,self._done,self.process.returncode)
        except Exception as ex:
            self.root.after(0,self._log,f"Error: {ex}\n","e")
            self.root.after(0,self._done,1)
        finally:
            if tmp and os.path.exists(tmp): os.unlink(tmp)

    def _set_progress(self,pct,label=""):
        self.prog["value"]=pct
        self.pct_label.config(text=f"{pct}%")
        self.status.set(f"Processing: {label} ({pct}%)")

    def _done(self,rc):
        self.prog["value"]=100 if rc==0 else self.prog["value"]
        self.pct_label.config(text="100%" if rc==0 else "Error")
        self.gen_btn.config(state="normal",text="GENERATE VIDEO",bg=ACCENT)
        self.stop_btn.config(state="disabled")
        if rc==0:
            self.status.set("Video is ready! Check the output folder.")
            self._log("\nVIDEO CREATED!\n","s")
            messagebox.showinfo("Video Ready!","Video created!\nCheck the output folder.")
        else:
            self.status.set("An error occurred. Check the console.")

    def _stop(self):
        if self.process:
            self.process.terminate()
            self._log("\nStopped.\n","e")
            self.prog["value"]=0; self.pct_label.config(text="0%")
            self.status.set("Stopped.")
            self.gen_btn.config(state="normal",text="GENERATE VIDEO",bg=ACCENT)
            self.stop_btn.config(state="disabled")

def main():
    # Check license
    try:
        from license import check_local_license, run_license_screen
        if not check_local_license():
            valid = run_license_screen()
            if not valid:
                return
    except Exception as e:
        print(f"License error: {e}")

    # Check API keys
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "config.py")
        with open(config_path, "r") as f:
            content = f.read()
        if "YOUR_GROQ_KEY" in content or "YOUR_SERPER_KEY" in content:
            sys.path.insert(0, base_path)
            from setup_keys import run_setup
            run_setup()
    except Exception as e:
        print(f"Setup error: {e}")

    root=tk.Tk()
    style=ttk.Style(); style.theme_use("clam")
    style.configure("Horizontal.TProgressbar",background=ACCENT,troughcolor=CARD)
    App(root); root.mainloop()

if __name__=="__main__":
    main()
