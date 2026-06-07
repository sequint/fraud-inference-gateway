import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Architecture Routing (TODO: update with AWS urls)
NANOHD_SERVICE_URL = os.environ.get("NANOHD_SERVICE_URL", "http://localhost:5001/api/predict")
LEGACY_CORE_URL = os.environ.get("LEGACY_CORE_SERVICE_URL", "http://localhost:5002/api/core/queue")
NANOHD_API_KEY = os.environ.get("NANOHD_API_KEY", "secure_edge_handshake_789")

@app.route('/api/transaction', methods=['POST'])
def handle_transaction():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "Malformed request payload"}), 400
        
    # Structural Sanity Check
    required_fields = ["account_id", "amount", "location", "timestamp"]
    if not all(field in payload for field in required_fields):
        return jsonify({"error": "Missing critical transactional parameters"}), 400

    try:
        # Evaluate fraud risk via nanohd prediction engine
        headers = {"X-API-KEY": NANOHD_API_KEY}
        inference_response = requests.post(NANOHD_SERVICE_URL, json=payload, headers=headers, timeout=2.0)
        
        if inference_response.status_code == 200:
            assessment = inference_response.get_json()
            if assessment.get("status") == "1":
                return jsonify({
                    "transaction_status": "REJECTED",
                    "reason": "Real-time vector inference flagged anomalous behavioral characteristics."
                }), 403
        else:
            # Operational edge case if prediction engine fails
            app.logger.warning("Inference engine unreachable or degraded. Defaulting to standard ledger ingestion.")

        # Forward validated payload to the asynchronous Legacy Core queue
        core_response = requests.post(LEGACY_CORE_URL, json=payload, timeout=2.0)
        
        if core_response.status_code == 202:
            return jsonify({
                "transaction_status": "QUEUED_FOR_SETTLEMENT",
                "message": "Transaction safely passed gateway validation and staged for legacy batch processing."
            }), 202
        else:
            return jsonify({"error": "Legacy ledger ingestion node failed to accept payload."}), 502

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Gateway network integration error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)