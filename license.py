# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import hashlib, os, json, requests, uuid
from datetime import datetime

BG="#0d0d0d"; CARD="#1a1a1a"; ACCENT="#ff4444"; TEXT="#ffffff"
SUBTEXT="#888888"; SUCCESS="#00cc66"; BORDER="#2a2a2a"

SECRET   = "FiazShah_AI_Video_2024_Secret"
SHEET_ID = "16_eYV25DKWqBZdS7gdmtyuU_8CAWp9ZWZVR9x32QWF4"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxR7u12DpVVRIMrVXyA82P7MGi9tzz1KUJHBpC8L72wZfrUnrFqmhxgyRUO9AeD5Dj8/exec"

def get_hardware_id():
    try:
        mac = uuid.getnode()
        return hashlib.md5(str(mac).encode()).hexdigest()[:12].upper()
    except:
        return "UNKNOWN"

def get_sheet_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            rows = []
            lines = r.text.strip().split('\n')
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    name   = parts[0].strip().strip('"')
                    key    = parts[1].strip().strip('"').upper().replace("-","").replace(" ","")
                    hwid   = parts[2].strip().strip('"') if len(parts) >= 3 else ""
                    expiry = parts[3].strip().strip('"') if len(parts) >= 4 else ""
                    rows.append({"name": name, "key": key, "hwid": hwid, "expiry": expiry})
            return rows
    except Exception as e:
        print(f"Sheet error: {e}")
    return []

def save_hwid_to_sheet(key, hwid):
    try:
        r = requests.post(APPS_SCRIPT_URL,
            json={"key": key, "hwid": hwid},
            timeout=10)
        print(f"HWID saved: {r.status_code} {r.text}")
        return r.text
    except Exception as e:
        print(f"HWID save error: {e}")
        return ""

def check_expiry(expiry_str):
    """Check if license is expired"""
    if not expiry_str or expiry_str.strip() == "":
        return True  # No expiry set — allow
    try:
        expiry_date = datetime.strptime(expiry_str.strip(), "%Y-%m-%d")
        return datetime.now() <= expiry_date
    except:
        return True

def validate_license(key):
    clean_key = key.strip().upper().replace("-","").replace(" ","")
    if not clean_key:
        return False, "", False, ""

    my_hwid = get_hardware_id()
    rows = get_sheet_data()

    if rows:
        for row in rows:
            if row["key"] == clean_key:
                stored_hwid = row["hwid"].strip()
                expiry      = row["expiry"].strip()

                # Check expiry first
                if not check_expiry(expiry):
                    return False, row["name"], False, "expired"

                if stored_hwid == "" or stored_hwid == "PENDING":
                    # First time — save HWID + expiry auto set by Apps Script
                    save_hwid_to_sheet(key, my_hwid)
                    return True, row["name"], True, "ok"
                elif stored_hwid == my_hwid:
                    return True, row["name"], True, "ok"
                else:
                    return False, row["name"], False, "wrong_pc"

    # Fallback local
    try:
        lf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "licenses.json")
        if os.path.exists(lf):
            with open(lf, 'r') as f:
                licenses = json.load(f)
            for name, sk in licenses.items():
                if sk.strip().upper().replace("-","").replace(" ","") == clean_key:
                    return True, name, True, "ok"
    except: pass
    return False, "", False, "invalid"

def save_license_locally(key):
    my_hwid = get_hardware_id()
    lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".license")
    with open(lp, 'w') as f:
        f.write(f"{key.strip()}|{my_hwid}")

def check_local_license():
    lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".license")
    if os.path.exists(lp):
        with open(lp, 'r') as f:
            data = f.read().strip()
        if "|" in data:
            key, saved_hwid = data.split("|", 1)
            if saved_hwid != get_hardware_id():
                os.remove(lp)
                return False
        else:
            key = data
        if len(key) < 10:
            return False
        try:
            valid, name, hwid_ok, status = validate_license(key)
            if status == "expired":
                return False
            return valid and hwid_ok
        except:
            return len(key) > 10
    return False

def check_and_setup_keys():
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "config.py")
        if not os.path.exists(config_path):
            return
        with open(config_path, "r") as f:
            content = f.read()
        if "YOUR_GROQ_KEY" in content or "YOUR_SERPER_KEY" in content:
            import sys
            sys.path.insert(0, base_path)
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "setup_keys", os.path.join(base_path, "setup_keys.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.run_setup()
    except Exception as e:
        print(f"Key setup error: {e}")

def generate_license(name, days=365):
    data = f"{name}_{days}_{SECRET}"
    hash_val = hashlib.sha256(data.encode()).hexdigest()[:24].upper()
    return "-".join([hash_val[i:i+4] for i in range(0, 24, 4)])


class LicenseScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Video Generator - License")
        self.root.geometry("500x420")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.validated = False
        self._ui()

    def _ui(self):
        tk.Label(self.root, text="AI Video Generator",
                font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT).pack(pady=(30,5))
        tk.Label(self.root, text="Please enter your license key to continue",
                font=("Segoe UI", 10), bg=BG, fg=SUBTEXT).pack(pady=(0,10))
        hw_id = get_hardware_id()
        tk.Label(self.root, text=f"Your PC ID: {hw_id}",
                font=("Segoe UI", 9), bg=BG, fg=SUBTEXT).pack(pady=(0,15))
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30)
        frame = tk.Frame(self.root, bg=BG, padx=40)
        frame.pack(fill="both", expand=True, pady=20)
        tk.Label(frame, text="License Key:",
                font=("Segoe UI", 10, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(10,5))
        self.key_var = tk.StringVar()
        key_entry = tk.Entry(frame, textvariable=self.key_var,
                            font=("Segoe UI", 12), bg=CARD, fg=TEXT,
                            insertbackground=TEXT, relief="flat",
                            highlightthickness=1, highlightcolor=ACCENT,
                            highlightbackground=BORDER)
        key_entry.pack(fill="x", ipady=10, pady=(0,5))
        key_entry.focus()
        tk.Label(frame, text="Format: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX",
                font=("Segoe UI", 8), bg=BG, fg=SUBTEXT).pack(anchor="w")
        self.status_lbl = tk.Label(frame, text="",
                font=("Segoe UI", 9), bg=BG, fg=SUBTEXT)
        self.status_lbl.pack(pady=(5,0))
        tk.Button(frame, text="ACTIVATE",
                 font=("Segoe UI", 12, "bold"),
                 bg=ACCENT, fg=TEXT, relief="flat",
                 cursor="hand2", pady=10,
                 command=self._activate).pack(fill="x", pady=(15,10))
        tk.Label(frame, text="Contact Fiaz Shah to get your license key",
                font=("Segoe UI", 9), bg=BG, fg=SUBTEXT).pack()
        tk.Label(self.root, text="Created by Fiaz Shah",
                font=("Segoe UI", 8, "italic"), bg=BG, fg=SUBTEXT).pack(pady=10)

    def _activate(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("Error", "Please enter your license key!")
            return
        self.status_lbl.config(text="Validating...", fg="#ffcc00")
        self.root.update()
        valid, name, hwid_ok, status = validate_license(key)
        if valid and hwid_ok:
            save_license_locally(key)
            self.validated = True
            messagebox.showinfo("Success!", f"License activated!\nWelcome {name}!")
            self.root.destroy()
        elif status == "expired":
            self.status_lbl.config(text="License expired!", fg="#ff4444")
            messagebox.showerror("Expired!", "Your license has expired!\nContact Fiaz Shah to renew.")
        elif status == "wrong_pc":
            self.status_lbl.config(text="Already used on another PC!", fg="#ff4444")
            messagebox.showerror("License Used",
                "This key is already activated on another PC!\nContact Fiaz Shah for help.")
        else:
            self.status_lbl.config(text="Invalid key!", fg="#ff4444")
            messagebox.showerror("Invalid Key",
                "License key is invalid!\nContact Fiaz Shah for a valid key.")


class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel - Fiaz Shah")
        self.root.geometry("650x450")
        self.root.configure(bg=BG)
        self._ui()

    def _ui(self):
        tk.Label(self.root, text="License Admin Panel",
                font=("Segoe UI", 16, "bold"), bg=BG, fg=ACCENT).pack(pady=20)
        frame = tk.Frame(self.root, bg=BG, padx=30)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Generate License Key:",
                font=("Segoe UI", 10, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,5))
        name_frame = tk.Frame(frame, bg=BG)
        name_frame.pack(fill="x", pady=(0,5))
        tk.Label(name_frame, text="User Name:", font=("Segoe UI",9), bg=BG, fg=SUBTEXT).pack(side="left")
        self.name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.name_var,
                font=("Segoe UI",10), bg=CARD, fg=TEXT,
                insertbackground=TEXT, relief="flat",
                highlightthickness=1, highlightcolor=ACCENT,
                highlightbackground=BORDER).pack(side="left", fill="x", expand=True, padx=(10,0), ipady=6)
        tk.Button(frame, text="Generate Key",
                 font=("Segoe UI",10,"bold"), bg=ACCENT, fg=TEXT,
                 relief="flat", cursor="hand2", pady=8,
                 command=self._generate).pack(fill="x", pady=10)
        self.result_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.result_var,
                font=("Segoe UI",12,"bold"), bg=CARD, fg=SUCCESS,
                relief="flat", state="readonly",
                highlightthickness=1, highlightbackground=BORDER).pack(fill="x", ipady=10, pady=(0,5))
        tk.Button(frame, text="Copy Key",
                 font=("Segoe UI",9), bg=CARD, fg=SUBTEXT,
                 relief="flat", cursor="hand2",
                 command=self._copy).pack(anchor="e", pady=(0,10))
        tk.Button(frame, text="Open Google Sheet",
                 font=("Segoe UI",9,"bold"), bg=CARD, fg=ACCENT,
                 relief="flat", cursor="hand2",
                 command=lambda: __import__('webbrowser').open(
                     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
                 )).pack()
        tk.Label(frame, text="Note: Expiry date auto-sets when user activates (30 days)",
                font=("Segoe UI",8), bg=BG, fg="#ffcc00").pack(pady=10)

    def _generate(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Error", "Enter user name!")
            return
        key = generate_license(name)
        self.result_var.set(key)
        messagebox.showinfo("Generated!",
            f"License for {name}:\n{key}\n\nAdd to Google Sheet!\nExpiry will auto-set when user activates.")

    def _copy(self):
        key = self.result_var.get()
        if key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            messagebox.showinfo("Copied!", "Key copied!")


def run_license_screen():
    root = tk.Tk()
    screen = LicenseScreen(root)
    root.mainloop()
    return screen.validated

def run_admin():
    root = tk.Tk()
    AdminPanel(root)
    root.mainloop()

if __name__ == "__main__":
    run_admin()
