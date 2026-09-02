#!/usr/bin/env python3
"""
Native Desktop GUI App for Jetson Hub Fleet Manager.
Runs as a standalone desktop application window (No web browser required).
"""
import tkinter as tk
from tkinter import ttk
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

    def refresh_table(self, data):
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data
        for v_id, v in data.items():
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
