"""
ShipOrSkip AI: The Hackathon Sanity & MVP Scope Agent
Powered by Amazon Bedrock (Nova Micro / Claude 3 Haiku) with deterministic fallback.
"""

import json
import logging
import os
import re
from typing import Dict, Any, Optional

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    boto3 = None
    ClientError = Exception
    BotoCoreError = Exception

logger = logging.getLogger(__name__)

# System prompt defining the persona and scoring rules
SYSTEM_PROMPT = """You are ShipOrSkip, an elite Hackathon Sanity & Scope Coach.
Your mission is to prevent builders from crashing at 3 AM by aggressively trimming scope creep and turning vague, over-engineered ideas into a clean, demo-ready 1-feature MVP.

You evaluate projects against:
1. Time Remaining (hours left)
2. Feasibility in a hackathon setting (demo > perfection)
3. The "Judge Impression Factor" (a working single loop beats 5 broken tabs)

Rules:
- NEVER give generic vague advice. Be specific to the technologies and problem mentioned.
- Identify the exact 'Fatal Rabbit Hole' (auth, custom models, complex payments, websocket syncing, multi-container setups).
- Format your response strictly as valid JSON matching the requested structure.
- Respect the requested Judge Persona:
  * 'mentor': Warm, encouraging senior engineer who guides gently.
  * 'architect': Pragmatic, crisp, focused on clean architecture and timeboxing.
  * 'brutal': Witty, blunt 3 AM hackathon judge who tells hard truths with humor.
"""

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Safely extracts JSON from model response text even if surrounded by markdown code blocks."""
    text = text.strip()
    # Try finding markdown code block
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    
    # Try finding first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start:end+1])
    
    return json.loads(text)

class ShipOrSkipAgent:
    def __init__(self, region_name: str = "us-east-1", model_id: str = "amazon.nova-micro-v1:0"):
        self.region_name = os.environ.get("AWS_DEFAULT_REGION", region_name)
        self.model_id = os.environ.get("BEDROCK_MODEL_ID", model_id)
        self.client = None
        self._init_bedrock_client()

    def _init_bedrock_client(self):
        """Initializes the boto3 bedrock-runtime client if credentials exist."""
        if boto3 is None:
            logger.warning("boto3 not installed; running in local heuristic mode.")
            return

        try:
            # Check if AWS credentials exist or are providable
            self.client = boto3.client("bedrock-runtime", region_name=self.region_name)
        except Exception as e:
            logger.info(f"Bedrock client initialization deferred or offline: {e}")
            self.client = None

    def analyze(self, idea_name: str, description: str, hours_left: int, tech_stack: str, persona: str = "architect") -> Dict[str, Any]:
        """
        Analyzes the hackathon project idea.
        Attempts Bedrock invocation first; falls back smoothly to deterministic heuristic engine.
        """
        idea_name = idea_name.strip() or "My Hackathon Project"
        description = description.strip()
        hours_left = max(1, min(72, int(hours_left)))
        persona = persona if persona in ["mentor", "architect", "brutal"] else "architect"

        # Try Bedrock invocation
        if self.client:
            try:
                result = self._call_bedrock(idea_name, description, hours_left, tech_stack, persona)
                if result:
                    result["source"] = f"Amazon Bedrock ({self.model_id})"
                    return result
            except Exception as e:
                logger.warning(f"Bedrock invocation failed, falling back to rule-based engine: {e}")

        # Fallback to deterministic rule-based analysis
        fallback_result = self._deterministic_fallback(idea_name, description, hours_left, tech_stack, persona)
        fallback_result["source"] = "Deterministic Heuristic Engine (Bedrock Fallback)"
        return fallback_result

    def _call_bedrock(self, idea_name: str, description: str, hours_left: int, tech_stack: str, persona: str) -> Optional[Dict[str, Any]]:
        """Invokes Amazon Bedrock Converse or InvokeModel API."""
        user_prompt = f"""Evaluate this hackathon project:
- Project Name: {idea_name}
- Hours Remaining: {hours_left} hours
- Proposed Tech Stack: {tech_stack or 'Unspecified / standard web stack'}
- Persona: {persona}
- Idea & Scope:
{description}

Return a valid JSON object with the following keys ONLY:
{{
  "verdict": "SHIP" | "TRIM" | "SINK",
  "feasibility_score": integer between 1 and 100,
  "verdict_headline": "Short punchy 1-sentence verdict",
  "fatal_rabbit_hole": "The single most dangerous feature or rabbit hole that will blow the timeline",
  "one_feature_mvp": "The exact single core loop to build that will impress judges",
  "sprint_plan": [
    {{"phase": "Sprint 1 (Hours 0-{hours_left//3})", "goal": "Core logic & mock data"}},
    {{"phase": "Sprint 2 (Hours {hours_left//3}-{hours_left*2//3})", "goal": "Happy-path UI connection"}},
    {{"phase": "Sprint 3 (Hours {hours_left*2//3}-{hours_left})", "goal": "Demo script & video recording"}}
  ],
  "coach_quote": "A 1-2 sentence piece of advice written in the requested persona",
  "features_to_drop": ["List of 2-3 features to immediately drop or fake with mock data"]
}}
"""

        # Prepare payload for Amazon Nova Micro or Claude
        if "nova" in self.model_id.lower():
            body = {
                "system": [{"text": SYSTEM_PROMPT}],
                "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
                "inferenceConfig": {"temperature": 0.2, "max_new_tokens": 800}
            }
        else: # Anthropic Claude schema
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 800,
                "temperature": 0.2,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_prompt}]
            }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        response_body = json.loads(response["body"].read().decode("utf-8"))

        if "nova" in self.model_id.lower():
            text_out = response_body["output"]["message"]["content"][0]["text"]
        else:
            text_out = response_body["content"][0]["text"]

        return extract_json_from_text(text_out)

    def _deterministic_fallback(self, idea_name: str, description: str, hours_left: int, tech_stack: str, persona: str) -> Dict[str, Any]:
        """High-accuracy deterministic fallback engine that guarantees reliable operation."""
        desc_lower = description.lower()
        tech_lower = tech_stack.lower()

        # Danger keywords that usually swallow hackathon time
        danger_signals = []
        if any(w in desc_lower or w in tech_lower for w in ["fine-tune", "train model", "custom llm", "rlhf", "from scratch"]):
            danger_signals.append("Training/fine-tuning a custom model instead of using prompt engineering or standard APIs")
        if any(w in desc_lower or w in tech_lower for w in ["auth", "jwt", "oauth", "login", "signup", "user role"]):
            danger_signals.append("Building full authentication/login forms (Judges never want to sign up; hardcode user state!)")
        if any(w in desc_lower or w in tech_lower for w in ["stripe", "payment", "crypto", "blockchain", "wallet", "smart contract"]):
            danger_signals.append("Integrating real payment/crypto transactions instead of simulating with mocked success receipts")
        if any(w in desc_lower or w in tech_lower for w in ["kubernetes", "docker swarm", "microservices", "kafka", "distributed"]):
            danger_signals.append("Over-engineering infrastructure with multi-service distributed architectures")
        if any(w in desc_lower or w in tech_lower for w in ["mobile app", "react native", "flutter", "ios", "android"]) and hours_left < 15:
            danger_signals.append("Native mobile build & deployment (emulator issues will drain hours; build responsive web)")

        if not danger_signals:
            danger_signals.append("Adding multiple configurable settings tabs instead of focusing on 1 killer end-to-end screen")

        # Calculate heuristic feasibility score
        base_score = 65
        # Time factor
        if hours_left >= 24:
            base_score += 15
        elif hours_left >= 12:
            base_score += 5
        elif hours_left <= 6:
            base_score -= 25
        elif hours_left <= 3:
            base_score -= 40

        # Scope factor (penalize for too many 'and', 'also', commas)
        and_count = desc_lower.count(" and ") + desc_lower.count(" also ") + desc_lower.count("plus ")
        if and_count > 3:
            base_score -= (and_count * 5)
        
        # Danger penalty
        base_score -= (len(danger_signals) * 10)
        feasibility_score = max(15, min(95, base_score))

        if feasibility_score >= 75:
            verdict = "SHIP"
            headline = f"Ready to ship! Your scope aligns cleanly with your {hours_left}h window."
        elif feasibility_score >= 45:
            verdict = "TRIM"
            headline = f"Trim the fluff. You have a great core concept, but your feature list is 2x too large for {hours_left}h."
        else:
            verdict = "SINK"
            headline = f"High 3 AM danger! Scope is severely bloated for a {hours_left}h countdown."

        # Persona-based quotes
        if persona == "brutal":
            quotes = {
                "SHIP": "Not bad. Don't touch any more settings and don't redesign the CSS at 2 AM. Ship the damn demo.",
                "TRIM": f"You've got {hours_left} hours left and you're planning 5 different user journeys. Pick ONE, fake the rest, or enjoy pitching a Figma prototype.",
                "SINK": "If you try to build all of this right now, your laptop will catch fire and you'll be presenting broken slides. Cut 80% immediately."
            }
        elif persona == "mentor":
            quotes = {
                "SHIP": "You're in great shape! Protect your energy, stick to this exact flow, and give yourself 2 full hours to record your pitch video.",
                "TRIM": "Breathe and step back. The judges don't need all these features—they just need to see your 'aha!' moment work once without a hiccup.",
                "SINK": "Don't panic! We can save this build. Drop everything except the single most impactful input and output screen. You can still win."
            }
        else: # architect
            quotes = {
                "SHIP": f"Execution priority: Freeze requirements, build the golden path, and leave {max(1, hours_left//4)}h for presentation rehearsal.",
                "TRIM": f"Scope reduction required. Cut the secondary features down to mock JSON payloads so the core engine stays rock solid.",
                "SINK": "Feasibility critical. Isolate the single API call that delivers customer value. Hardcode all upstream forms."
            }

        sprint_1_end = max(1, hours_left // 3)
        sprint_2_end = max(sprint_1_end + 1, (hours_left * 2) // 3)

        return {
            "verdict": verdict,
            "feasibility_score": feasibility_score,
            "verdict_headline": headline,
            "fatal_rabbit_hole": danger_signals[0],
            "one_feature_mvp": f"The 'Golden Path' Demo: 1 input field, 1 action button, and 1 clean visual output screen showing '{idea_name}' solving the primary pain point.",
            "sprint_plan": [
                {"phase": f"Sprint 1 (Hours 0-{sprint_1_end})", "goal": "Build the core business logic / API integration using hardcoded mock inputs."},
                {"phase": f"Sprint 2 (Hours {sprint_1_end}-{sprint_2_end})", "goal": "Hook up a single-page UI. Validate the end-to-end happy path without errors."},
                {"phase": f"Sprint 3 (Hours {sprint_2_end}-{hours_left})", "goal": "Record the 2-minute demo video and prep the 3-slide pitch. Stop writing code!"}
            ],
            "coach_quote": quotes[verdict],
            "features_to_drop": [
                "User registration & profile management (use demo bypass button)",
                "Settings configuration & dark/light theme toggle",
                "Complex background workers or retry queues (fake with instant state updates)"
            ]
        }
