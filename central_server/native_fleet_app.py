#!/usr/bin/env python3
"""
Native Desktop GUI App for Jetson Hub Fleet Manager.
Runs as a standalone desktop application window (No web browser required).
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import urllib.request
import urllib.request
import json
import threading
import time

class FleetManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eclipse SDV - Fleet Manager (Native App)")
        self.root.geometry("800x400")
        self.root.configure(bg="#2E3440")
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#3B4252", foreground="white", fieldbackground="#3B4252", rowheight=30)
        style.configure("Treeview.Heading", background="#4C566A", foreground="white", font=('Arial', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#5E81AC')])

        # Header
        header = tk.Label(root, text="🌐 SDV Fleet Command Center", font=("Arial", 18, "bold"), bg="#2E3440", fg="#88C0D0")
        header.pack(pady=15)

        # Table (Treeview)
        columns = ("Status", "Vehicle ID", "Model", "Speed", "Battery", "Software")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        # Action Panel
        action_frame = tk.Frame(root, bg="#2E3440")
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        btn_ota = tk.Button(action_frame, text="🚀 PUSH OTA UPDATE TO SELECTED VEHICLE", 
                           bg="#5E81AC", fg="white", font=("Arial", 11, "bold"), 
                           command=self.push_ota_to_selected, relief=tk.FLAT, padx=15, pady=5)
        btn_ota.pack(side=tk.RIGHT)
        
        btn_diag = tk.Button(action_frame, text="🚨 RUN REMOTE DIAGNOSTICS (OpenSOVD)", 
                           bg="#BF616A", fg="white", font=("Arial", 11, "bold"), 
                           command=self.run_diagnostics, relief=tk.FLAT, padx=15, pady=5)
        btn_diag.pack(side=tk.RIGHT, padx=10)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Auto-refresh loop
        self.running = True
        self.update_thread = threading.Thread(target=self.poll_api, daemon=True)
        self.update_thread.start()

    def poll_api(self):
        while self.running:
            try:
                req = urllib.request.Request("http://localhost:8080/api/v1/vehicles")
                with urllib.request.urlopen(req, timeout=1.0) as response:
                    data = json.loads(response.read().decode())
                    self.root.after(0, self.refresh_table, data)
            except Exception as e:
                pass
            time.sleep(2)

    def run_diagnostics(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a vehicle first.")
            return
            
        item = self.tree.item(selected[0])
        vehicle_id = item['values'][1]
        
        ip = simpledialog.askstring("Remote Diagnostics", f"Enter Wi-Fi IP for {vehicle_id} to pull OpenSOVD Data:")
        if not ip: return
        
        try:
            req = urllib.request.Request(f"http://{ip.strip()}:5000/api/diagnostics/dtc")
            with urllib.request.urlopen(req, timeout=3.0) as res:
                import json
                data = json.loads(res.read().decode())
                
                report = f"📋 OpenSOVD Diagnostic Report\n"
                report += f"Vehicle: {data.get('vehicle_id')}\n"
                report += f"Service Required: {'YES ⚠️' if data.get('service_required') else 'NO ✅'}\n\n"
                report += "Active Diagnostic Trouble Codes (DTCs):\n"
                
                for dtc in data.get("codes", []):
                    report += f"• [{dtc['code']}] {dtc['module']} - {dtc['description']}\n"
                    
                messagebox.showerror("Diagnostics Alert", report)
        except Exception as e:
            messagebox.showerror("Network Error", f"Could not reach OpenSOVD API: {e}")

    def push_ota_to_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a vehicle from the table first.")
            return
            
        item = self.tree.item(selected[0])
        vehicle_id = item['values'][1]  # Vehicle ID is the second column
        
        import subprocess
        import os
        try:
            # We call the external python script so we don't have to import zenoh globally if it's missing on the UI thread
            repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script = os.path.join(repo_dir, "central_server", "push_ota.py")
            subprocess.Popen([sys.executable, script, vehicle_id])
            messagebox.showinfo("Zenoh OTA Broadcast", f"OTA signal securely broadcasted to the cloud topic for {vehicle_id} (No IP required!).\n\nThe vehicle will pick it up automatically.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run Zenoh broadcast: {e}")

    def refresh_table(self, data):
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Extract vehicle list from API response
        vehicles = data.get("vehicles", [])
        
        # Insert new data
        for v in vehicles:
            v_id = v.get("vehicle_id", "Unknown")
            status = "🟢 ONLINE" if v.get("status") == "ONLINE" else "🔴 OFFLINE"
            speed = f"{v.get('current_state_snapshot', {}).get('speed_kmh', 0)} km/h"
            battery = f"{v.get('current_state_snapshot', {}).get('battery_soc_percent', 0)}%"
            software = v.get("software_inventory", {}).get("sdv_platform_version", "Unknown")
            model = v.get("name", "Unknown")
            
            self.tree.insert("", tk.END, values=(status, v_id, model, speed, battery, software))

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FleetManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
