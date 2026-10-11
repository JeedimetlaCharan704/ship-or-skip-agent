"""
Unit and integration tests for ShipOrSkip AI Agent
"""

import unittest
from bedrock_agent import ShipOrSkipAgent, extract_json_from_text
from app import app

class TestShipOrSkipAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ShipOrSkipAgent()

    def test_json_extractor(self):
        raw = '```json\n{"verdict": "SHIP", "feasibility_score": 90}\n```'
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["verdict"], "SHIP")
        self.assertEqual(parsed["feasibility_score"], 90)

    def test_overkill_idea_detection(self):
        # Absurd scope in 4 hours
        result = self.agent.analyze(
            idea_name="CryptoSwarm",
            description="We are building a custom multi-agent LLM trained from scratch, with Stripe payments, smart contracts, and Kubernetes deployment.",
            hours_left=4,
            tech_stack="Kubernetes, Stripe, Custom PyTorch model",
            persona="brutal"
        )
        self.assertIn(result["verdict"], ["TRIM", "SINK"])
        self.assertLessEqual(result["feasibility_score"], 50)
        self.assertTrue(len(result["fatal_rabbit_hole"]) > 5)
        self.assertEqual(len(result["sprint_plan"]), 3)
        self.assertTrue(len(result["features_to_drop"]) > 0)
        print("\n[TEST PASS] Overkill Idea Detected:")
        print(f"  Verdict: {result['verdict']} ({result['feasibility_score']}/100)")
        print(f"  Rabbit Hole: {result['fatal_rabbit_hole']}")

    def test_clean_mvp(self):
        # Realistic scope in 24 hours
        result = self.agent.analyze(
            idea_name="SimpleSplit",
            description="A 1-screen bill splitter that calculates per-person dues from receipt text.",
            hours_left=24,
            tech_stack="Flask, Tailwind",
            persona="mentor"
        )
        self.assertIn(result["verdict"], ["SHIP", "TRIM"])
        self.assertGreaterEqual(result["feasibility_score"], 65)
        print("\n[TEST PASS] Clean MVP Evaluated:")
        print(f"  Verdict: {result['verdict']} ({result['feasibility_score']}/100)")
        print(f"  MVP: {result['one_feature_mvp']}")

    def test_flask_api_endpoint(self):
        client = app.test_client()
        # Test health
        health_res = client.get("/api/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertEqual(health_res.json["status"], "healthy")

        # Test analyze endpoint
        post_res = client.post("/api/analyze", json={
            "idea_name": "TestApp",
            "description": "Simple weather assistant for hikers",
            "hours_left": 12,
            "tech_stack": "Python, Bedrock",
            "persona": "architect"
        })
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("verdict", post_res.json)
        self.assertIn("feasibility_score", post_res.json)
        print("\n[TEST PASS] Flask REST API verified successfully.")

if __name__ == "__main__":
    unittest.main()
