import json
import os
import hashlib
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ZKSNARKS_DIR = BASE_DIR / "zksnarks"
BUILD_DIR = ZKSNARKS_DIR / "build"

# Circuit paths
ATTRIBUTE_DIR = BUILD_DIR / "attribute"
POLICY_DIR = BUILD_DIR / "policy"
PROCESS_DIR = BUILD_DIR / "process"

def get_circuit_path(circuit_name):
    """Get the path to circuit build directory based on circuit name."""
    if circuit_name == "proof_of_attribute":
        return ATTRIBUTE_DIR
    elif circuit_name == "proof_of_policy":
        return POLICY_DIR
    elif circuit_name == "proof_of_process":
        return PROCESS_DIR
    else:
        raise ValueError(f"Unknown circuit: {circuit_name}")

def compute_pedersen_hash(values):
    """
    Simple hash computation for zkSNARK compatibility.
    Uses basic arithmetic operations that can be easily replicated in circom.
    Returns a single field element that matches the circuit exactly.
    """
    # Convert all values to integers
    int_values = []
    for v in values:
        if isinstance(v, str):
            # Convert string to int using a simple method
            int_val = sum(ord(c) * (256 ** i) for i, c in enumerate(v[:8]))  # Take first 8 chars
        else:
            int_val = int(v)
        int_values.append(int_val)
    
    # Simple hash: sum all values with weights (matching circuit implementation exactly)
    hash_val = 0
    powers_of_31 = [1, 31, 961, 29791, 923521]  # 31^0, 31^1, 31^2, 31^3, 31^4
    
    for i, val in enumerate(int_values):
        if i < len(powers_of_31):
            hash_val += val * powers_of_31[i]
        else:
            hash_val += val * (31 ** i)
    
    # Return the hash value directly (no modulo operation to match circuit)
    return hash_val

def format_proof_for_contract(proof):
    """Format a proof for submission to the smart contract."""
    return {
        "a": proof["pi_a"][:2],  # Remove the 1 at the end
        "b": [
            [proof["pi_b"][0][1], proof["pi_b"][0][0]],  # Swap elements and remove the 1
            [proof["pi_b"][1][1], proof["pi_b"][1][0]]
        ],
        "c": proof["pi_c"][:2]  # Remove the 1 at the end
    }