"""
Vercel Serverless Function: /api/predict
Handles POST requests for ML startup success prediction.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Add parent directory to path so we can import shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from _lib.predictor import predict_startup, get_feature_importance, get_metrics
from _lib.cors import cors_headers, handle_options


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        # Route GET /api/predict to feature importance or metrics based on path
        path = self.path.split("?")[0]
        headers = cors_headers()
        if path == "/api/model-metrics":
            body = json.dumps(get_metrics()).encode()
        elif path == "/api/feature-importance":
            body = json.dumps({"features": get_feature_importance()}).encode()
        else:
            body = json.dumps({"name": "FounderFlow ML API", "status": "online", "version": "7.0.0"}).encode()
        self.send_response(200)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        headers = cors_headers()
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw)
            result = predict_startup(payload)
            body = json.dumps(result).encode()
            self.send_response(200)
        except Exception as exc:
            body = json.dumps({"detail": f"Prediction failed: {exc}"}).encode()
            self.send_response(500)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
