"""
AWS Lambda Handler for ShipOrSkip AI Agent
Supports Lambda Function URLs and Amazon API Gateway HTTP APIs.
"""

import json
from bedrock_agent import ShipOrSkipAgent

agent = ShipOrSkipAgent()

def lambda_handler(event, context):
    # Handle CORS preflight
    http_method = event.get("requestContext", {}).get("http", {}).get("method", event.get("httpMethod", "GET"))
    
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"status": "ok"})
        }

    path = event.get("rawPath", event.get("path", "/"))

    # Health check route
    if path == "/api/health" or (http_method == "GET" and path == "/"):
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "status": "healthy",
                "agent": "ShipOrSkip AI",
                "bedrock_client_available": agent.client is not None,
                "model_id": agent.model_id,
                "region": agent.region_name
            })
        }

    # Analyze route
    if http_method == "POST":
        try:
            body_str = event.get("body", "{}")
            if event.get("isBase64Encoded", False):
                import base64
                body_str = base64.b64decode(body_str).decode("utf-8")

            body = json.loads(body_str) if isinstance(body_str, str) else body_str

            idea_name = body.get("idea_name", "My Hackathon Project")
            description = body.get("description", "")
            hours_left = body.get("hours_left", 8)
            tech_stack = body.get("tech_stack", "")
            persona = body.get("persona", "architect")

            if not description:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"error": "Please provide an idea description."})
                }

            result = agent.analyze(
                idea_name=idea_name,
                description=description,
                hours_left=int(hours_left),
                tech_stack=tech_stack,
                persona=persona
            )

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(result)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": str(e)})
            }

    return {
        "statusCode": 404,
        "headers": headers,
        "body": json.dumps({"error": "Not Found"})
    }
