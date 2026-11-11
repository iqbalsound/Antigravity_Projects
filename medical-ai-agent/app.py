from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, HTTPException

from medical_agent.pipeline import (
    PRIMARY_MODEL,
    REVIEW_MODEL,
    ConfigurationError,
    MedicalAgent,
    MedicalAgentError,
)

load_dotenv()

MAX_SYMPTOM_LENGTH = 4_000

CLINICAL_PRESETS = [
    {
        "id": "tension_headache",
        "tag": "Tension Headache",
        "badge": "Routine",
        "symptoms": (
            "I have had a dull, aching band of tightness around my forehead and back of my head "
            "for the past 2 days after working long hours on a laptop. No fever, no nausea, "
            "and no vision changes."
        ),
    },
    {
        "id": "chest_pain",
        "tag": "Chest Pain (Emergency)",
        "badge": "Emergency",
        "symptoms": (
            "Sudden crushing, heavy pressure in the center of my chest radiating down my left arm "
            "and jaw, accompanied by shortness of breath, dizziness, and cold sweats for 20 minutes."
        ),
    },
    {
        "id": "persistent_cough",
        "tag": "Persistent Cough",
        "badge": "Urgent",
        "symptoms": (
            "Deep, productive cough with greenish phlegm for 7 days, accompanied by a fever "
            "of 101.5°F, mild shortness of breath when climbing stairs, and fatigue."
        ),
    },
    {
        "id": "diabetic_foot",
        "tag": "Diabetic Foot Lesion",
        "badge": "Urgent",
        "symptoms": (
            "I have type 2 diabetes and noticed a small painless blister on the ball of my right foot "
            "3 days ago. The skin around it is now swollen, noticeably warm, and slightly red."
        ),
    },
    {
        "id": "pediatric_fever",
        "tag": "Pediatric Fever & Rash",
        "badge": "Clinical Check",
        "symptoms": (
            "My 3-year-old child had a high fever (102.5°F) for 3 days that broke this morning. "
            "Now a rosy, pink rash has appeared across their chest and back. They are drinking fluids but fussy."
        ),
    },
]


def create_app(agent: MedicalAgent | None = None) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024
    app.config["MEDICAL_AGENT"] = agent or MedicalAgent()

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/health")
    def health() -> tuple[Any, int]:
        if request.args.get("details") == "1":
            gemini_key_present = bool(
                os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            )
            groq_key_present = bool(os.environ.get("GROQ_API_KEY"))
            return (
                jsonify(
                    {
                        "status": "ok",
                        "gemini_configured": gemini_key_present,
                        "groq_configured": groq_key_present,
                        "primary_target": PRIMARY_MODEL,
                        "review_target": REVIEW_MODEL,
                        "port": int(os.environ.get("PORT", "9995")),
                    }
                ),
                200,
            )
        return jsonify({"status": "ok"}), 200

    @app.get("/api/status")
    def system_status() -> tuple[Any, int]:
        gemini_key_present = bool(
            os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        )
        groq_key_present = bool(os.environ.get("GROQ_API_KEY"))
        return (
            jsonify(
                {
                    "status": "ok",
                    "gemini_configured": gemini_key_present,
                    "groq_configured": groq_key_present,
                    "primary_target": PRIMARY_MODEL,
                    "review_target": REVIEW_MODEL,
                    "port": int(os.environ.get("PORT", "9995")),
                }
            ),
            200,
        )

    @app.get("/api/presets")
    def presets() -> tuple[Any, int]:
        return jsonify(CLINICAL_PRESETS), 200

    @app.post("/api/respond")
    def respond() -> tuple[Any, int]:
        if not request.is_json:
            return jsonify({"error": "Send your request as JSON."}), 415

        try:
            payload = request.get_json()
        except BadRequest:
            return jsonify({"error": "The request body must be valid JSON."}), 400

        if not isinstance(payload, dict):
            return jsonify({"error": "The request body must be a JSON object."}), 400

        symptoms = payload.get("symptoms")
        if not isinstance(symptoms, str) or not symptoms.strip():
            return jsonify({"error": "Describe your symptoms before continuing."}), 400
        if len(symptoms) > MAX_SYMPTOM_LENGTH:
            return jsonify(
                {"error": f"Keep your description under {MAX_SYMPTOM_LENGTH} characters."}
            ), 400

        # Optional client-supplied API key overrides (session-level)
        gemini_override = payload.get("gemini_api_key")
        groq_override = payload.get("groq_api_key")

        current_agent = app.config["MEDICAL_AGENT"]
        if gemini_override or groq_override:
            if gemini_override:
                os.environ["GEMINI_API_KEY"] = str(gemini_override).strip()
            if groq_override:
                os.environ["GROQ_API_KEY"] = str(groq_override).strip()
            # If temporary overrides supplied, initialize a clean agent
            current_agent = MedicalAgent()

        try:
            result = current_agent.respond(symptoms.strip())
        except ConfigurationError as exc:
            return jsonify({"error": str(exc)}), 503
        except MedicalAgentError as exc:
            return jsonify({"error": str(exc)}), 502

        return jsonify(result), 200

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> tuple[Any, int]:
        if request.path.startswith("/api/"):
            return jsonify({"error": error.description}), error.code or 500
        return error

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "9995"))
    app.run(host="0.0.0.0", port=port, debug=False)
