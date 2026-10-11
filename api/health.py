import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bedrock_agent import ShipOrSkipAgent

agent = ShipOrSkipAgent()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            "status": "healthy",
            "agent": "ShipOrSkip AI",
            "bedrock_client_available": agent.client is not None,
            "model_id": agent.model_id,
            "region": agent.region_name
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
