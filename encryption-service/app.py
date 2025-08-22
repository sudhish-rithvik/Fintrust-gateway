"""
Simplified Encryption Service for FinTrust Gateway
Works without TenSEAL for local development
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import base64
from datetime import datetime
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
CORS(app)

# Generate a key for this session (in production, use a persistent key)
SERVER_KEY = Fernet.generate_key()
fernet = Fernet(SERVER_KEY)

# Simple polynomial coefficients for loan evaluation
LOAN_COEFFICIENTS = [1000, 2, -0.5]  # ax^2 + bx + c

# Logging
LOG_FILE = "encryption_logs.json"

def log_event(event_data):
    """Log events to file"""
    try:
        event_data["timestamp"] = datetime.utcnow().isoformat()

        # Read existing logs
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)

        # Add new log
        logs.append(event_data)

        # Keep only last 100 logs
        logs = logs[-100:]

        # Write back
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

    except Exception as e:
        print(f"Logging error: {e}")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "FinTrust Encryption Service",
        "version": "1.0.0-dev"
    })

@app.route("/encrypt", methods=["POST"])
def encrypt_data():
    """Encrypt data using Fernet (symmetric encryption)"""
    try:
        data = request.json
        plaintext = data.get("plaintext")

        if not plaintext:
            return jsonify({"error": "Missing plaintext"}), 400

        # Convert to bytes if string
        if isinstance(plaintext, str):
            plaintext_bytes = plaintext.encode()
        else:
            plaintext_bytes = json.dumps(plaintext).encode()

        # Encrypt
        encrypted = fernet.encrypt(plaintext_bytes)
        encrypted_b64 = base64.b64encode(encrypted).decode()

        # Log event
        log_event({
            "action": "encrypt",
            "status": "success",
            "data_length": len(plaintext_bytes)
        })

        return jsonify({
            "encrypted_data": encrypted_b64,
            "algorithm": "Fernet",
            "key_id": "dev-session-key"
        })

    except Exception as e:
        log_event({
            "action": "encrypt",
            "status": "error",
            "error": str(e)
        })
        return jsonify({"error": f"Encryption failed: {str(e)}"}), 500

@app.route("/decrypt", methods=["POST"])
def decrypt_data():
    """Decrypt data using Fernet"""
    try:
        data = request.json
        encrypted_b64 = data.get("encrypted_data")

        if not encrypted_b64:
            return jsonify({"error": "Missing encrypted_data"}), 400

        # Decrypt
        encrypted = base64.b64decode(encrypted_b64)
        decrypted_bytes = fernet.decrypt(encrypted)

        # Try to parse as JSON, fallback to string
        try:
            decrypted_data = json.loads(decrypted_bytes.decode())
        except json.JSONDecodeError:
            decrypted_data = decrypted_bytes.decode()

        # Log event
        log_event({
            "action": "decrypt",
            "status": "success"
        })

        return jsonify({
            "decrypted_data": decrypted_data
        })

    except Exception as e:
        log_event({
            "action": "decrypt",
            "status": "error",
            "error": str(e)
        })
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 500

@app.route("/loan/evaluate", methods=["POST"])
def evaluate_loan():
    """
    Simplified loan evaluation without homomorphic encryption
    In production, this would use TenSEAL for privacy-preserving computation
    """
    try:
        data = request.json

        # For development, accept either encrypted or plain data
        if "encrypted_payload" in data:
            # Try to decrypt if encrypted
            try:
                encrypted = base64.b64decode(data["encrypted_payload"])
                decrypted_bytes = fernet.decrypt(encrypted)
                loan_data = json.loads(decrypted_bytes.decode())
            except:
                return jsonify({"error": "Could not decrypt loan data"}), 400
        else:
            # Accept plain data for development
            loan_data = data

        # Extract loan parameters
        income = float(loan_data.get("income", 50000))
        credit_score = float(loan_data.get("credit_score", 700))
        loan_amount = float(loan_data.get("loan_amount", 10000))

        # Simple loan evaluation formula
        # Score = a + b*income/1000 + c*credit_score + d*loan_amount/1000
        score = (
            LOAN_COEFFICIENTS[0] +
            LOAN_COEFFICIENTS[1] * (income / 1000) +
            LOAN_COEFFICIENTS[2] * credit_score +
            (-0.1) * (loan_amount / 1000)
        )

        # Determine approval
        approved = score > 750
        interest_rate = max(3.5, min(15.0, (800 - credit_score) / 10))

        result = {
            "approved": approved,
            "score": round(score, 2),
            "interest_rate": round(interest_rate, 2),
            "max_loan_amount": round(income * 4, 2),
            "evaluation_id": f"eval_{random.randint(100000, 999999)}"
        }

        # Encrypt result for consistency
        result_encrypted = fernet.encrypt(json.dumps(result).encode())
        result_b64 = base64.b64encode(result_encrypted).decode()

        # Log event
        log_event({
            "action": "loan_evaluation",
            "status": "completed",
            "approved": approved,
            "score": score
        })

        return jsonify({
            "encrypted_loan_result": result_b64,
            "plain_result": result  # Include plain result for development
        })

    except Exception as e:
        log_event({
            "action": "loan_evaluation",
            "status": "error",
            "error": str(e)
        })
        return jsonify({"error": f"Loan evaluation failed: {str(e)}"}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    """Get encryption service logs (development only)"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
            return jsonify({"logs": logs[-20:]})  # Return last 20 logs
        else:
            return jsonify({"logs": []})
    except Exception as e:
        return jsonify({"error": f"Could not retrieve logs: {str(e)}"}), 500

@app.route("/key", methods=["GET"])
def get_key_info():
    """Get information about the current encryption key (development only)"""
    return jsonify({
        "key_algorithm": "Fernet",
        "key_id": "dev-session-key",
        "key_b64": base64.b64encode(SERVER_KEY).decode(),
        "warning": "This key is for development only!"
    })

if __name__ == "__main__":
    print("🔐 Starting FinTrust Encryption Service...")
    print(f"🔑 Session key: {base64.b64encode(SERVER_KEY).decode()[:20]}...")
    print("📊 Logs will be saved to: encryption_logs.json")
    print("⚠️  This is a development version - NOT for production!")

    app.run(host="0.0.0.0", port=5000, debug=True)
