"""
Vercel Serverless Function: /api/idea/analyze  (POST)
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from _lib.cors import cors_headers, handle_options
from _lib.services import analyze_idea


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
        headers = cors_headers()
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw)
            result = analyze_idea(payload)
            body = json.dumps(result).encode()
            self.send_response(200)
        except Exception as exc:
            body = json.dumps({"detail": str(exc)}).encode()
            self.send_response(500)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
