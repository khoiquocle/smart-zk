import json
import subprocess
import tempfile
import os
from pathlib import Path
from .utils import get_circuit_path, format_proof_for_contract

def generate_witness(circuit_name, input_data):
    """Generate a witness for the given circuit and input data."""
    circuit_path = get_circuit_path(circuit_name)
    
    # Create a temporary file for the input
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(input_data, f)
        input_file = f.name
    
    # Generate the witness
    witness_file = tempfile.NamedTemporaryFile(suffix='.wtns', delete=False).name
    
    try:
        # Execute the witness generation
        subprocess.run([
            "node",
            f"{circuit_path}/{circuit_name}_js/generate_witness.js",
            f"{circuit_path}/{circuit_name}_js/{circuit_name}.wasm",
            input_file,
            witness_file
        ], check=True)
        
        return witness_file
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Witness generation failed: {e}")
    finally:
        # Clean up the input file
        os.unlink(input_file)

def generate_proof(circuit_name, input_data):
    """Generate a zkSNARK proof for the given circuit and input data."""
    circuit_path = get_circuit_path(circuit_name)
    zkey_file = f"{circuit_path}/{circuit_name}_0001.zkey"
    
    # Generate the witness
    witness_file = generate_witness(circuit_name, input_data)
    
    # Create a temporary file for the proof
    proof_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name
    public_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name
    
    try:
        # Generate the proof
        subprocess.run([
            "snarkjs",
            "groth16",
            "prove",
            zkey_file,
            witness_file,
            proof_file,
            public_file
        ], check=True)
        
        # Read the proof and public inputs
        with open(proof_file, 'r') as f:
            proof = json.load(f)
        
        with open(public_file, 'r') as f:
            public_inputs = json.load(f)
        
        # Return the raw proof for verification (not formatted for contract)
        # The format_proof_for_contract should only be used for blockchain submission
        return proof, public_inputs
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Proof generation failed: {e}")
    finally:
        # Clean up temporary files
        os.unlink(witness_file)
        os.unlink(proof_file)
        os.unlink(public_file)