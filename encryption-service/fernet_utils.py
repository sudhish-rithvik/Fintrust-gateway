from cryptography.fernet import Fernet
from datetime import datetime

# For production, store this key securely (e.g., in a vault or .env)
FERNET_KEY = Fernet.generate_key()
fernet = Fernet(FERNET_KEY)

LOG_FILE = "logs/encrypted_log.txt"

def log_encrypted(message: str):
    """
    Encrypts and logs a message with timestamp.
    """
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"[{timestamp}] {message}"
    
    encrypted = fernet.encrypt(log_entry.encode()).decode()

    with open(LOG_FILE, "a") as f:
        f.write(encrypted + "\n")
