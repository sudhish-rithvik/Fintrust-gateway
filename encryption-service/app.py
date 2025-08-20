from flask import Flask, request, jsonify
from flask_cors import CORS
import tenseal as ts
import numpy as np
import base64
import json
import random
from cryptography.fernet import Fernet
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Create encryption context (used only on client for sim)
global_tenseal_context = None
poly_coefficients = [1000, 2, -0.5]

# Create a shared Fernet key for logging (store this securely in production)
server_log_key = Fernet.generate_key()
fernet = Fernet(server_log_key)

# Logging path
LOG_FILE = "logs/encrypted_log.txt"
os.makedirs("logs", exist_ok=True)

# ------------------------------
# Utility: Logging
# ------------------------------

def encrypt_log_entry(log_str):
    return fernet.encrypt(log_str.encode()).decode("utf-8")

def server_log_event(event_data):
    try:
        log_str = json.dumps(event_data)
        encrypted_log = encrypt_log_entry(log_str)
        with open(LOG_FILE, "a") as f:
            f.write(encrypted_log + "\n")
        return encrypted_log
    except Exception as e:
        print(f"[ERROR] Failed to log event: {e}")
        return None

# ------------------------------
# Routes
# ------------------------------

@app.route("/init_context", methods=["POST"])
def init_context():
    global global_tenseal_context
    try:
        data = request.json
        ctx_bytes = base64.b64decode(data["context"])
        global_tenseal_context = ts.context_from(ctx_bytes)
        return jsonify({"status": "TenSEAL context initialized"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/loan/evaluate", methods=["POST"])
def evaluate_loan():
    global global_tenseal_context
    if not global_tenseal_context:
        return jsonify({"error": "Context not initialized"}), 400
    try:
        data = request.json
        encrypted_input_b64 = data["encrypted_payload"]
        encrypted_input_bytes = base64.b64decode(encrypted_input_b64)

        # Load encrypted input
        enc_vec = ts.ckks_vector_from(global_tenseal_context, encrypted_input_bytes)

        # Evaluate polynomial: ax^2 + bx + c
        result = ts.ckks_vector(global_tenseal_context, [poly_coefficients[0]] * len(enc_vec.decrypt()))
        x_power = enc_vec
        for i in range(1, len(poly_coefficients)):
            result += x_power * poly_coefficients[i]
            if i < len(poly_coefficients) - 1:
                x_power = x_power * enc_vec

        encrypted_result = result.serialize()

        # Log securely
        server_log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "loan_evaluation",
            "status": "encrypted_evaluated",
            "input_hash": hash(encrypted_input_b64)
        })

        return jsonify({
            "encrypted_loan_result": base64.b64encode(encrypted_result).decode()
        }), 200

    except Exception as e:
        return jsonify({"error": f"Loan evaluation failed: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Encryption service healthy"}), 200

if __name__ == "__main__":
    print(f"[INFO] HE log key (store securely!): {server_log_key.decode()}")
    app.run(host="0.0.0.0", port=5000)
