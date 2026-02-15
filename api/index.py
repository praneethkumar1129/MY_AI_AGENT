from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import hashlib
from urllib.parse import parse_qs
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL")

client = AsyncIOMotorClient(MONGODB_URL)
db = client.bujji_ai

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/chat':
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "You are Bujji, a friendly AI assistant."},
                            {"role": "user", "content": data['message']}
                        ]
                    },
                    timeout=30
                )
                result = response.json()
                self.wfile.write(json.dumps({"response": result["choices"][0]["message"]["content"]}).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.wfile.write(json.dumps({"error": "Not implemented"}).encode())
