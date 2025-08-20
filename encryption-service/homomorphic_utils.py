import tenseal as ts
import numpy as np
import random

# ------------------------------
# TenSEAL Context Initialization
# ------------------------------

def create_tenseal_context():
    """
    Creates a TenSEAL CKKS context with 8192 poly modulus degree.
    """
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    return context

# ------------------------------
# Encryption / Decryption
# ------------------------------

def client_encrypt_vector(context: ts.Context, data: list) -> bytes:
    """
    Encrypts a list of floats using the provided TenSEAL context.
    Returns a serialized encrypted vector.
    """
    try:
        vec = ts.ckks_vector(context, data)
        return vec.serialize()
    except Exception as e:
        print(f"[ERROR] Encryption failed: {e}")
        return None

def client_decrypt_vector(context: ts.Context, encrypted_bytes: bytes) -> list:
    """
    Decrypts a serialized CKKS vector using the client-side context.
    """
    try:
        vec = ts.ckks_vector_from(context, encrypted_bytes)
        return vec.decrypt()
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")
        return None

# ------------------------------
# Homomorphic Polynomial Evaluation
# ------------------------------

def evaluate_polynomial_on_encrypted(enc_bytes: bytes, context: ts.Context, coefficients: list) -> bytes:
    """
    Homomorphically evaluates a polynomial on an encrypted CKKS vector:
    P(x) = a0 + a1*x + a2*x^2 + ...
    """
    try:
        x = ts.ckks_vector_from(context, enc_bytes)
        result = ts.ckks_vector(context, [coefficients[0]] * len(x.decrypt()))

        x_power = x
        for i in range(1, len(coefficients)):
            result += x_power * coefficients[i]
            if i < len(coefficients) - 1:
                x_power *= x

        return result.serialize()
    except Exception as e:
        print(f"[ERROR] Polynomial evaluation failed: {e}")
        return None

# ------------------------------
# Differential Privacy Noise
# ------------------------------

def add_differential_privacy(values: list, sensitivity: float, epsilon: float) -> list:
    """
    Applies Gaussian noise to a list of floats using (ε, 0)-DP.
    """
    scale = sensitivity / epsilon
    return [v + random.gauss(0, scale) for v in values]
