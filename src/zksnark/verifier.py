import json
import subprocess
import tempfile
import os
from .utils import get_circuit_path

class ZkSnarkVerifier:
    """zkSNARK Verifier class for MARTZK system"""
    
    def __init__(self):
        """Initialize the zkSNARK verifier"""
        pass
    
    def verify_attribute_proof(self, proof, public_signals):
        """
        Verify a zkSNARK proof of attribute possession
        
        Args:
            proof: The zkSNARK proof (JSON object)
            public_signals: The public signals (list)
            
        Returns:
            bool: True if proof is valid, False otherwise
        """
        try:
            # Use the proof_of_attribute circuit for verification
            return verify_proof_offchain("proof_of_attribute", proof, public_signals)
        except Exception as e:
            print(f"[ERROR] Attribute proof verification failed: {e}")
            return False
    
    def verify_policy_proof(self, proof, public_signals):
        """
        Verify a zkSNARK proof of policy satisfaction
        
        Args:
            proof: The zkSNARK proof (JSON object)
            public_signals: The public signals (list)
            
        Returns:
            bool: True if proof is valid, False otherwise
        """
        try:
            # Use the proof_of_policy circuit for verification
            return verify_proof_offchain("proof_of_policy", proof, public_signals)
        except Exception as e:
            print(f"[ERROR] Policy proof verification failed: {e}")
            return False
    
    def verify_process_proof(self, proof, public_signals):
        """
        Verify a zkSNARK proof of process participation
        
        Args:
            proof: The zkSNARK proof (JSON object)
            public_signals: The public signals (list)
            
        Returns:
            bool: True if proof is valid, False otherwise
        """
        try:
            # Use the proof_of_process circuit for verification
            return verify_proof_offchain("proof_of_process", proof, public_signals)
        except Exception as e:
            print(f"[ERROR] Process proof verification failed: {e}")
            return False

def verify_proof_offchain(circuit_name, proof, public_inputs):
    """Verify a zkSNARK proof off-chain using snarkjs."""
    circuit_path = get_circuit_path(circuit_name)
    vkey_file = f"{circuit_path}/{circuit_name}_verification_key.json"
    
    # Create temporary files for the proof and public inputs
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(proof, f)
        proof_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(public_inputs, f)
        public_file = f.name
    
    try:
        # Verify the proof (Python 3.6 compatible)
        result = subprocess.run([
            "snarkjs",
            "groth16",
            "verify",
            vkey_file,
            public_file,
            proof_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        print(f"DEBUG: snarkjs verification command output:")
        print(f"  stdout: {result.stdout}")
        print(f"  stderr: {result.stderr}")
        print(f"  return code: {result.returncode}")
        
        # Check if verification was successful
        verification_result = "OK" in result.stdout
        print(f"DEBUG: Verification result: {verification_result}")
        return verification_result
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Proof verification failed: {e}")
    finally:
        # Clean up temporary files
        os.unlink(proof_file)
        os.unlink(public_file)