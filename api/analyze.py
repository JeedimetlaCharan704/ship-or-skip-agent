import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bedrock_agent import ShipOrSkipAgent

agent = ShipOrSkipAgent()

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            idea_name = data.get("idea_name", "My Hackathon Project")
            description = data.get("description", "")
            hours_left = data.get("hours_left", 8)
            tech_stack = data.get("tech_stack", "")
            persona = data.get("persona", "architect")

            result = agent.analyze(
                idea_name=idea_name,
                description=description,
                hours_left=int(hours_left),
                tech_stack=tech_stack,
                persona=persona
            )

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
