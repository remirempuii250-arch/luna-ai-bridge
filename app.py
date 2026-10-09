
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL = "gemini-3.8-flash"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Luna bridge is running")

    def do_POST(self):
        if self.path != "/ask":
            self.send_error(404)
            return

        try:
            size = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(size))
            message = str(data.get("message", ""))[:1000]
            key = os.environ.get("GEMINI_API_KEY")

            if not key:
                raise ValueError("API key not configured")

            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                + MODEL + ":generateContent?key=" + key
            )
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "You are Luna, a friendly Minecraft princess. "
                        "Reply naturally and briefly. Player says: " + message
                    }]
                }]
            }
            request = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read())

            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            output = json.dumps({"reply": reply}).encode()
            self.send_response(200)

        except Exception:
            output = json.dumps(
                {"error": "Bridge request failed"}
            ).encode()
            self.send_response(500)

        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(output)

server = HTTPServer(
    ("0.0.0.0", int(os.environ.get("PORT", "10000"))), Handler
)
print("Luna bridge started")
server.serve_forever()
