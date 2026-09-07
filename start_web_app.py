#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import os

PORT = 8000
DIRECTORY = "web_app"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            try:
                req = urllib.request.Request(f"http://localhost:5000{self.path}")
                with urllib.request.urlopen(req) as res:
                    self.send_response(res.status)
                    self.send_header('Content-Type', res.getheader('Content-Type', 'application/json'))
                    self.end_headers()
                    self.wfile.write(res.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                req = urllib.request.Request(f"http://localhost:5000{self.path}", data=post_data, method="POST")
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req) as res:
                    self.send_response(res.status)
                    self.send_header('Content-Type', res.getheader('Content-Type', 'application/json'))
                    self.end_headers()
                    self.wfile.write(res.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    print(f"=== SDV CLOUD WEB APP PROXY RUNNING ON PORT {PORT} ===")
    httpd.serve_forever()
