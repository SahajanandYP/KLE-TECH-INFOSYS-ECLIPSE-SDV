#!/usr/bin/env python3
import http.server
import socketserver
import os
import socket

PORT = 8000
DIRECTORY = "web_app"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    ip = get_ip()
    print(f"=== MOBILE WEB APP SERVER STARTED ===")
    print(f"To open the app on your phone, connect your phone to the same Wi-Fi")
    print(f"and type this exact URL into your phone's browser:")
    print(f"👉  http://{ip}:{PORT}")
    print(f"=====================================")
    httpd.serve_forever()
