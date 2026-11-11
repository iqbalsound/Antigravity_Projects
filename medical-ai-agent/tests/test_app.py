from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from app import create_app
from medical_agent.pipeline import ConfigurationError, MedicalAgent, MedicalAgentError


class FakeAgent:
    def __init__(self) -> None:
        self.received_symptoms: str | None = None

    def respond(self, symptoms: str) -> dict[str, object]:
        self.received_symptoms = symptoms
        return {
            "response": "## Next steps\nTalk with a clinician.",
            "draft": "## Initial Draft\nRest and hydrate.",
            "safety_score": 94,
            "accuracy_score": 91,
            "concerns": [],
            "primary_model": "gemini-2.5-flash",
            "review_model": "llama-3.3-70b-versatile",
            "emergency_detected": False,
            "triage_category": "Routine / Self-Care",
        }


class AppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = FakeAgent()
        self.client = create_app(self.agent).test_client()

    def test_homepage_and_health_endpoint(self) -> None:
        self.assertEqual(self.client.get("/").status_code, 200)
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json(), {"status": "ok"})

    def test_status_and_presets_endpoints(self) -> None:
        status_res = self.client.get("/api/status")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.get_json()
        self.assertEqual(status_data["status"], "ok")
        self.assertEqual(status_data["port"], 9995)

        presets_res = self.client.get("/api/presets")
        self.assertEqual(presets_res.status_code, 200)
        presets_data = presets_res.get_json()
        self.assertIsInstance(presets_data, list)
        self.assertGreater(len(presets_data), 0)

    def test_rejects_missing_or_invalid_symptoms(self) -> None:
        for value in ("", "   ", 42, None):
            with self.subTest(value=value):
                response = self.client.post(
                    "/api/respond",
                    json={"symptoms": value},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_rejects_oversized_symptoms(self) -> None:
        response = self.client.post(
            "/api/respond",
            json={"symptoms": "x" * 4_001},
        )
        self.assertEqual(response.status_code, 400)

    def test_respond_returns_refined_output_and_strips_whitespace(self) -> None:
        response = self.client.post(
            "/api/respond",
            json={"symptoms": "  A mild headache for two days.  "},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.agent.received_symptoms, "A mild headache for two days.")
        res_json = response.get_json()
        self.assertEqual(res_json["safety_score"], 94)
        self.assertEqual(res_json["response"], "## Next steps\nTalk with a clinician.")
        self.assertEqual(res_json["draft"], "## Initial Draft\nRest and hydrate.")
        self.assertFalse(res_json["emergency_detected"])

    def test_provider_errors_are_returned_as_json(self) -> None:
        class ErrorAgent:
            def respond(self, symptoms: str) -> dict[str, object]:
                raise ConfigurationError("Set GOOGLE_API_KEY to enable Gemini.")

        response = create_app(ErrorAgent()).test_client().post(
            "/api/respond",
            json={"symptoms": "A headache."},
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("GOOGLE_API_KEY", response.get_json()["error"])

    def test_provider_failure_does_not_return_a_success_shaped_response(self) -> None:
        class ErrorAgent:
            def respond(self, symptoms: str) -> dict[str, object]:
                raise MedicalAgentError("The safety-review model is temporarily unavailable.")

        response = create_app(ErrorAgent()).test_client().post(
            "/api/respond",
            json={"symptoms": "A headache."},
        )
        self.assertEqual(response.status_code, 502)
        self.assertIn("safety-review", response.get_json()["error"])


class PipelineTests(unittest.TestCase):
    def test_runs_gemini_then_validates_groq_review(self) -> None:
        gemini = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=lambda **kwargs: SimpleNamespace(
                    text="## Possible next steps\nGet rest and monitor symptoms."
                )
            )
        )
        review_data = {
            "safety_score": 95,
            "accuracy_score": 89,
            "concerns": [],
            "refined_response": "## Next steps\nRest and monitor symptoms.",
        }
        groq = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content=json.dumps(review_data))
                            )
                        ]
                    )
                )
            )
        )

        result = MedicalAgent(gemini, groq).respond("A mild headache.")
        self.assertEqual(result["response"], review_data["refined_response"])
        self.assertEqual(result["draft"], "## Possible next steps\nGet rest and monitor symptoms.")
        self.assertEqual(result["safety_score"], 95)
        self.assertEqual(result["accuracy_score"], 89)

    def test_rejects_invalid_review_scores(self) -> None:
        gemini = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=lambda **kwargs: SimpleNamespace(text="Draft")
            )
        )
        groq = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(
                                    content=json.dumps(
                                        {
                                            "safety_score": True,
                                            "accuracy_score": 90,
                                            "concerns": [],
                                            "refined_response": "Reviewed.",
                                        }
                                    )
                                )
                            )
                        ]
                    )
                )
            )
        )
        with self.assertRaises(MedicalAgentError):
            MedicalAgent(gemini, groq).respond("A mild headache.")


if __name__ == "__main__":
    unittest.main()
