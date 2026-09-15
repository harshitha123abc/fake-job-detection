from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from src.orchestrator import FakeJobDetectorOrchestrator
from src.agent import ResumeJobMatchAgent
import sys

load_dotenv()

app = Flask(__name__)
CORS(app)

print("Initializing orchestrator...", file=sys.stderr, flush=True)
orchestrator = FakeJobDetectorOrchestrator()
print("Orchestrator initialized!", file=sys.stderr, flush=True)

print("Initializing resume matcher...", file=sys.stderr, flush=True)
resume_matcher = ResumeJobMatchAgent()
print("Resume matcher initialized!", file=sys.stderr, flush=True)

API_KEY = os.getenv("API_KEY", "test123")

@app.route('/predict', methods=['POST'])
def predict():
    """Multi-agent fake job detection endpoint with LangGraph orchestration"""
    try:
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401

        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({"error": "Missing 'description' field"}), 400

        job_text = data['description']

        result = orchestrator.detect(job_text)

        response = {
            "prediction": "Fake" if result["risk_level"] == "High" else "Real",
            "confidence": result["final_risk_score"] / 100.0,
            "risk_score": result["final_risk_score"],
            "risk_level": result["risk_level"],
            "reasoning": [result["explanation"]],
            "recommendation": result["recommendation"],
            "agent_breakdown": result["confidence_breakdown"],
            "extracted_info": result["agent_results"]["extractor"],
            "platform_search": result["agent_results"]["search"],
            "company_verification": result["agent_results"]["verification"],
            "scam_analysis": result["agent_results"]["scam_detection"],
            "ml_analysis": result["agent_results"].get("ml_analysis", {}),
            "orchestration_metadata": result.get("_pipeline_metadata", {}),
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/match_resume', methods=['POST'])
def match_resume():
    """Resume-job matching endpoint"""
    try:
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401

        data = request.get_json()
        if not data or 'resume' not in data or 'job_description' not in data:
            return jsonify({"error": "Missing 'resume' or 'job_description' fields"}), 400

        result = resume_matcher.analyze_match(data['resume'], data['job_description'])
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "system": "Multi-Agent Fake Job Detector with LangGraph",
            "components": {
                "orchestrator": "LangGraph ✓",
                "resume_matcher": "Active ✓"
            },
            "features": [
                "Multi-agent orchestration (LangGraph)",
                "Cross-platform job search",
                "Company verification",
                "AI scam detection",
                "ML fake probability",
                "Resume-job matching"
            ]
        })
    except Exception as e:
        return jsonify({"status": "degraded", "error": str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
