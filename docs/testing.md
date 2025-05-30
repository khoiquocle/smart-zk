# Testing the MARTZK zkSNARK Module Components

This guide provides specific instructions and examples for testing the core components of the zkSNARK module within the MARTZK implementation separately.

**Prerequisites:**
*   Completed zkSNARK setup (circuits compiled, keys generated via `compile_circuits.sh` and `setup.sh`).
*   Python environment set up with necessary libraries (`pytest` recommended: `pip install pytest`).
*   Deployed Verifier contracts and the main `MARTZKEth.sol` contract on a local test network (e.g., Ganache).
*   Updated `.env` file with contract addresses from the test network deployment.
*   Configured `src/block_int.py` to connect to your test network.

## 1. Testing Proof Generation (`src/zksnark/prover.py`)

**Goal:** Verify that `generate_witness` and `generate_proof` functions work correctly for valid and invalid inputs.

**Method:** Use `pytest` to create test cases.

**Example Test File (`tests/unit/test_prover.py`):**

```python
import pytest
import os
import sys
import json
from datetime import datetime

# Add src directory to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from zksnark.prover import generate_witness, generate_proof
from zksnark.utils import compute_pedersen_hash # Assuming this is your hash function

# --- Test Data Setup ---
def get_valid_attribute_input():
    """Provides valid input data for the attribute proof circuit."""
    attr_secret = 1234567890123456789
    attr_value = 9876543210987654321
    authority_id = 1
    attr_type = 2
    expiry_date = int((datetime.now().replace(year=datetime.now().year + 1)).strftime("%Y%m%d"))
    current_date = int(datetime.now().strftime("%Y%m%d"))
    commitment = compute_pedersen_hash([
        attr_secret, attr_value, authority_id, attr_type, expiry_date
    ])
    return {
        "attr_secret": str(attr_secret), # Inputs often need to be strings for snarkjs
        "attr_value": str(attr_value),
        "authority_id": str(authority_id),
        "attr_type": str(attr_type),
        "expiry_date": str(expiry_date),
        "attr_commitment": str(commitment),
        "current_date": str(current_date),
        "expected_authority_id": str(authority_id),
        "expected_attr_type": str(attr_type)
    }

def get_invalid_attribute_input_bad_commit():
    """Provides invalid input (bad commitment) for the attribute proof circuit."""
    data = get_valid_attribute_input()
    data["attr_commitment"] = str(int(data["attr_commitment"]) + 1) # Make commitment invalid
    return data

def get_invalid_attribute_input_expired():
    """Provides invalid input (expired) for the attribute proof circuit."""
    data = get_valid_attribute_input()
    data["expiry_date"] = "20200101" # Set expiry in the past
    # Recalculate commitment for the expired date to isolate the expiry check
    commitment = compute_pedersen_hash([
        int(data["attr_secret"]), int(data["attr_value"]), int(data["authority_id"]),
        int(data["attr_type"]), int(data["expiry_date"])
    ])
    data["attr_commitment"] = str(commitment)
    return data

# --- Pytest Tests ---

@pytest.mark.parametrize("circuit_name", ["proof_of_attribute"]) # Add other circuits like "proof_of_policy"
def test_witness_generation_valid(circuit_name):
    """Test witness generation with valid inputs."""
    input_data = get_valid_attribute_input() # Modify to get inputs for other circuits
    witness_file = None
    try:
        witness_file = generate_witness(circuit_name, input_data)
        assert os.path.exists(witness_file)
        # Optional: Add checks on witness file content/size if possible
    finally:
        if witness_file and os.path.exists(witness_file):
            os.unlink(witness_file)

@pytest.mark.parametrize("circuit_name, invalid_input_func", [
    ("proof_of_attribute", get_invalid_attribute_input_bad_commit),
    ("proof_of_attribute", get_invalid_attribute_input_expired),
    # Add tests for other circuits and invalid conditions
])
def test_witness_generation_invalid(circuit_name, invalid_input_func):
    """Test witness generation fails for invalid inputs."""
    input_data = invalid_input_func()
    with pytest.raises(RuntimeError, match="Witness generation failed"): # Check for specific error
        generate_witness(circuit_name, input_data)

@pytest.mark.parametrize("circuit_name", ["proof_of_attribute"]) # Add other circuits
def test_proof_generation_valid(circuit_name):
    """Test proof generation with valid inputs."""
    input_data = get_valid_attribute_input() # Modify for other circuits
    proof, public_inputs = generate_proof(circuit_name, input_data)
    
    # Check proof structure
    assert "pi_a" in proof
    assert "pi_b" in proof
    assert "pi_c" in proof
    assert "protocol" in proof and proof["protocol"] == "groth16"
    assert isinstance(public_inputs, list)
    # Check public inputs match the public part of input_data (order matters!)
    expected_public = [
        input_data["attr_commitment"],
        input_data["current_date"],
        input_data["expected_authority_id"],
        input_data["expected_attr_type"]
    ]
    assert public_inputs == expected_public

```

**Running the Tests:**
```bash
cd /path/to/your/project # Navigate to the root directory (e.g., MARTSIA-demo)
pytest tests/unit/test_prover.py
```

## 2. Testing Off-Chain Verification (`src/zksnark/verifier.py`)

**Goal:** Verify that `verify_proof_offchain` correctly validates or rejects proofs.

**Method:** Extend the `pytest` file or create a new one (`tests/unit/test_verifier.py`).

**Example Test File (`tests/unit/test_verifier.py`):**

```python
import pytest
import os
import sys
import json

# Add src directory to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from zksnark.prover import generate_proof
from zksnark.verifier import verify_proof_offchain
from .test_prover import get_valid_attribute_input # Reuse input generation

@pytest.mark.parametrize("circuit_name", ["proof_of_attribute"]) # Add other circuits
def test_offchain_verification_valid(circuit_name):
    """Test off-chain verification with a valid proof."""
    input_data = get_valid_attribute_input() # Modify for other circuits
    proof, public_inputs = generate_proof(circuit_name, input_data)
    
    is_valid = verify_proof_offchain(circuit_name, proof, public_inputs)
    assert is_valid is True

@pytest.mark.parametrize("circuit_name", ["proof_of_attribute"]) # Add other circuits
def test_offchain_verification_invalid_proof(circuit_name):
    """Test off-chain verification with an invalid (tampered) proof."""
    input_data = get_valid_attribute_input() # Modify for other circuits
    proof, public_inputs = generate_proof(circuit_name, input_data)
    
    # Tamper with the proof (example: modify pi_a)
    original_pi_a_0 = proof["pi_a"][0]
    proof["pi_a"][0] = str(int(original_pi_a_0) + 1) 
    
    is_valid = verify_proof_offchain(circuit_name, proof, public_inputs)
    assert is_valid is False
    
    # Restore original proof if needed for other tests
    proof["pi_a"][0] = original_pi_a_0 

@pytest.mark.parametrize("circuit_name", ["proof_of_attribute"]) # Add other circuits
def test_offchain_verification_invalid_public_inputs(circuit_name):
    """Test off-chain verification with valid proof but incorrect public inputs."""
    input_data = get_valid_attribute_input() # Modify for other circuits
    proof, public_inputs = generate_proof(circuit_name, input_data)
    
    # Tamper with public inputs (example: modify commitment)
    public_inputs[0] = str(int(public_inputs[0]) + 1)
    
    is_valid = verify_proof_offchain(circuit_name, proof, public_inputs)
    assert is_valid is False

```

**Running the Tests:**
```bash
cd /path/to/your/project
pytest tests/unit/test_verifier.py
```

## 3. Testing On-Chain Verification (`src/block_int.py` & Contracts)

**Goal:** Verify that proofs can be submitted to the blockchain and correctly verified by the deployed smart contracts.

**Method:** Use `pytest` along with `web3.py` interactions targeting a test network (e.g., Ganache).

**Prerequisites for these tests:**
*   Ganache (or other test network) running.
*   Contracts deployed to Ganache, addresses updated in `.env`.
*   `src/block_int.py` configured to connect to Ganache.

**Example Test File (`tests/integration/test_onchain_verification.py`):**

```python
import pytest
import os
import sys
import json
from web3 import Web3 # Make sure web3 is installed

# Add src directory to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from zksnark.prover import generate_proof
from zksnark.utils import format_proof_for_contract # Use the formatting util
import block_int # Import your blockchain interface module
from decouple import config # To get sender address/key

# --- Test Setup ---
# Ensure block_int is configured for the test network (e.g., Ganache)
# You might need to load test accounts from Ganache
SENDER_ADDRESS = config('TEST_SENDER_ADDRESS') # Add a test account address to .env
SENDER_PRIVATE_KEY = config('TEST_SENDER_PRIVATE_KEY') # Add its private key to .env

# --- Helper to get valid proof data ---
def get_valid_proof_and_inputs(circuit_name):
    # Reuse input generation from test_prover
    from tests.unit.test_prover import get_valid_attribute_input 
    input_data = get_valid_attribute_input() # Modify for other circuits
    formatted_proof, public_inputs = generate_proof(circuit_name, input_data)
    # Convert public inputs to integers as expected by the contract usually
    public_inputs_int = [int(p) for p in public_inputs]
    return formatted_proof, public_inputs_int

# --- Pytest Tests ---

@pytest.mark.parametrize("circuit_name, verification_function", [
    ("proof_of_attribute", block_int.verify_attribute_proof_onchain),
    # Add ("proof_of_policy", block_int.verify_policy_proof_onchain), etc.
])
def test_onchain_verification_valid(circuit_name, verification_function):
    """Test submitting a valid proof for on-chain verification."""
    proof_data, public_inputs = get_valid_proof_and_inputs(circuit_name)
    
    # Submit proof to the blockchain via block_int function
    try:
        tx_receipt = verification_function(
            proof_data['a'], 
            proof_data['b'], 
            proof_data['c'], 
            public_inputs, 
            SENDER_ADDRESS, 
            SENDER_PRIVATE_KEY # Pass private key if needed by block_int
        )
        # Check receipt status
        assert tx_receipt['status'] == 1, f"Transaction failed: {tx_receipt}"
        # Optional: Check for emitted events (requires ABI and event parsing)
        # logs = block_int.get_contract_instance().events.AttributeProofVerified().processReceipt(tx_receipt)
        # assert len(logs) > 0
    except Exception as e:
        pytest.fail(f"On-chain verification failed unexpectedly: {e}")

@pytest.mark.parametrize("circuit_name, verification_function", [
    ("proof_of_attribute", block_int.verify_attribute_proof_onchain),
    # Add other circuits
])
def test_onchain_verification_invalid_proof(circuit_name, verification_function):
    """Test submitting an invalid proof for on-chain verification (should revert)."""
    proof_data, public_inputs = get_valid_proof_and_inputs(circuit_name)
    
    # Tamper with the proof
    original_pi_a_0 = proof_data['a'][0]
    proof_data['a'][0] = proof_data['a'][0] + 1 # Tamper proof
    
    # Expect the transaction to revert (e.g., due to require(success, ...))
    with pytest.raises(Exception): # Catch broader exceptions from web3/contract interaction
         verification_function(
            proof_data['a'], 
            proof_data['b'], 
            proof_data['c'], 
            public_inputs, 
            SENDER_ADDRESS, 
            SENDER_PRIVATE_KEY
        )
    # More specific error checking based on web3.py exceptions is better if possible

```

**Running the Tests:**
1.  Start Ganache.
2.  Deploy contracts: `truffle migrate --network ganache` (assuming a 'ganache' network in `truffle-config.js`).
3.  Update `.env` with deployed addresses and a Ganache account/private key.
4.  Run pytest: `pytest tests/integration/test_onchain_verification.py`

By following these steps, you can thoroughly test each part of your zkSNARK module, ensuring proof generation, off-chain verification, and on-chain verification work as expected before integrating them fully into the MARTZK application flow.