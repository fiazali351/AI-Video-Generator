# -*- coding: utf-8 -*-
"""
setup_keys.py — First time API key setup
"""
import tkinter as tk
from tkinter import messagebox
import os
import re

BG="#0d0d0d"; CARD="#1a1a1a"; ACCENT="#ff4444"; TEXT="#ffffff"
SUBTEXT="#888888"; SUCCESS="#00cc66"; BORDER="#2a2a2a"

class KeySetup:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Video Generator - Setup")
        self.root.geometry("600x580")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._ui()

    def _ui(self):
        # Header
        tk.Label(self.root, text="AI Video Generator",
                font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT).pack(pady=(20,5))
        tk.Label(self.root, text="First Time Setup — Enter Your API Keys",
                font=("Segoe UI", 10), bg=BG, fg=SUBTEXT).pack(pady=(0,20))

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30)

        frame = tk.Frame(self.root, bg=BG, padx=30)
        frame.pack(fill="both", expand=True, pady=20)

        # Groq Key
        self._add_key(frame, "Groq API Key (For AI Script)",
                     "Get free key: console.groq.com",
                     "https://console.groq.com/keys",
                     "groq_key")

        # Pexels Key
        self._add_key(frame, "Pexels API Key (For Images)",
                     "Get free key: pexels.com/api",
                     "https://www.pexels.com/api/",
                     "pexels_key")

        # Serper Key
        self._add_key(frame, "Serper API Key (For Google Images)",
                     "Get free key: serper.dev (2500/month free)",
                     "https://serper.dev",
                     "serper_key")

        # Save button
        tk.Button(self.root, text="SAVE & START",
                 font=("Segoe UI", 13, "bold"),
                 bg=ACCENT, fg=TEXT, relief="flat",
                 cursor="hand2", pady=12,
                 command=self._save).pack(fill="x", padx=30, pady=(0,10))
        tk.Button(self.root, text="Skip (Use existing keys)",
                 font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT, relief="flat",
                 cursor="hand2", pady=6,
                 command=self.root.destroy).pack(fill="x", padx=30, pady=(0,10))

        tk.Label(self.root, text="Created by Fiaz Shah",
                font=("Segoe UI", 8, "italic"), bg=BG, fg=SUBTEXT).pack()

    def _add_key(self, parent, title, hint, url, var_name):
        tk.Label(parent, text=title,
                font=("Segoe UI", 10, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(10,3))

        entry_frame = tk.Frame(parent, bg=BG)
        entry_frame.pack(fill="x", pady=(0,3))

        var = tk.StringVar()
        setattr(self, var_name, var)

        entry = tk.Entry(entry_frame, textvariable=var,
                        font=("Segoe UI", 10), bg=CARD, fg=TEXT,
                        insertbackground=TEXT, relief="flat",
                        highlightthickness=1, highlightcolor=ACCENT,
                        highlightbackground=BORDER, show="*")
        entry.pack(side="left", fill="x", expand=True, ipady=8)

        # Show/Hide button
        def toggle(e=entry, s="*"):
            e.config(show="" if e.cget("show") == "*" else "*")

        tk.Button(entry_frame, text="Show", font=("Segoe UI", 8),
                 bg=CARD, fg=SUBTEXT, relief="flat", cursor="hand2",
                 command=toggle).pack(side="right", padx=(5,0), pady=2)

        hint_frame = tk.Frame(parent, bg=BG)
        hint_frame.pack(fill="x")
        tk.Label(hint_frame, text=hint,
                font=("Segoe UI", 8), bg=BG, fg=SUBTEXT).pack(side="left")
        tk.Button(hint_frame, text="Get Key →",
                 font=("Segoe UI", 8), bg=BG, fg=ACCENT,
                 relief="flat", cursor="hand2",
                 command=lambda u=url: __import__('webbrowser').open(u)).pack(side="right")

    def _save(self):
        groq   = self.groq_key.get().strip()
        pexels = self.pexels_key.get().strip()
        serper = self.serper_key.get().strip()

        if not groq or not pexels or not serper:
            messagebox.showwarning("Missing Keys!", "Please enter all 3 API keys!")
            return

        # Update config.py
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
            with open(config_path, 'r') as f:
                c = f.read()

            c = re.sub(r'OPENAI_API_KEY\s*=.*', f'OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "{groq}")', c)
            c = re.sub(r'PEXELS_API_KEY\s*=.*', f'PEXELS_API_KEY    = os.getenv("PEXELS_API_KEY", "{pexels}")', c)
            c = re.sub(r'SERPER_API_KEY\s*=.*', f'SERPER_API_KEY    = "{serper}"', c)

            with open(config_path, 'w') as f:
                f.write(c)

            messagebox.showinfo("Success!", "API Keys saved!\nSoftware is ready to use!")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Could not save keys: {e}")


def check_keys_set():
    """Check if keys are already configured"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
        with open(config_path, 'r') as f:
            c = f.read()
        if "YOUR_" in c or "gsk_" not in c:
            return False
        return True
    except:
        return False


def run_setup():
    root = tk.Tk()
    KeySetup(root)
    root.mainloop()


if __name__ == "__main__":
    run_setup()
