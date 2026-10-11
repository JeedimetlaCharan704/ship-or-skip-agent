"""
ShipOrSkip AI Web Server & REST API
Built with Python Flask, boto3 Bedrock Runtime, and deterministic fallback.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from bedrock_agent import ShipOrSkipAgent

app = Flask(__name__, static_folder="static")
CORS(app)

agent = ShipOrSkipAgent()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "agent": "ShipOrSkip AI",
        "bedrock_client_available": agent.client is not None,
        "model_id": agent.model_id,
        "region": agent.region_name
    })

@app.route("/api/analyze", methods=["POST"])
def analyze_idea():
    try:
        data = request.get_json(force=True) or {}
        idea_name = data.get("idea_name", "My Hackathon Project")
        description = data.get("description", "")
        hours_left = data.get("hours_left", 8)
        tech_stack = data.get("tech_stack", "")
        persona = data.get("persona", "architect")

        if not description:
            return jsonify({
                "error": "Please provide an idea description."
            }), 400

        result = agent.analyze(
            idea_name=idea_name,
            description=description,
            hours_left=int(hours_left),
            tech_stack=tech_stack,
            persona=persona
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "fallback_available": True
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] ShipOrSkip AI Agent running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
