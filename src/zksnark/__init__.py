"""
MARTZK zkSNARK Module

This package provides functionality for generating and verifying zkSNARK proofs
in the MARTZK system, which enhances MARTSIA with zero-knowledge proofs for
attribute management, policy enforcement, and business process compliance.
"""

from .utils import compute_pedersen_hash
from .prover import generate_witness, generate_proof
from .verifier import verify_proof_offchain

__all__ = ['compute_pedersen_hash', 'generate_witness', 'generate_proof', 'verify_proof_offchain']
