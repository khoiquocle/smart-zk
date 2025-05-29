# MARTZK: Detailed Implementation Guide

This guide provides specific, step-by-step instructions for implementing zkSNARKs into the MARTSIA system, transforming it into MARTZK. The implementation follows the directory structure outlined in the architectural blueprint and incorporates the technical details from the zkSNARK integration guide.

## 1. Project Setup and Directory Structure

### 1.1. Clone the MARTSIA Repository
```bash
git clone https://github.com/apwbs/MARTSIA-demo.git
cd MARTSIA-demo
```

### 1.2. Create the MARTZK Directory Structure
```bash
# Create main directories
mkdir -p zksnarks/circuits/helpers
mkdir -p zksnarks/build/{attribute,policy,process}
mkdir -p zksnarks/scripts
mkdir -p zksnarks/test
mkdir -p blockchain/contracts/verifiers
mkdir -p blockchain/contracts/interfaces
mkdir -p src/zksnark
mkdir -p src/models
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/diagrams
```

### 1.3. Install Required Dependencies
```bash
# Install Node.js dependencies
npm init -y
npm install --save-dev circomlib snarkjs

# Install Circom (if not already installed)
git clone https://github.com/iden3/circom.git
cd circom
cargo build --release
cargo install --path circom
cd ..

# Install Python dependencies
pip install -r requirements.txt
```

## 2. Circuit Development

### 2.1. Create the Attribute Proof Circuit

Create the file `zksnarks/circuits/proof_of_attribute.circom`:

```circom
pragma circom 2.0.0;

include "node_modules/circomlib/circuits/pedersen.circom";
include "node_modules/circomlib/circuits/comparators.circom";

template ProofOfAttribute() {
    // Private Inputs
    signal private input attr_secret; // Secret associated with the attribute
    signal private input attr_value;  // Actual attribute value
    signal private input authority_id; // Issuing authority ID
    signal private input attr_type;    // Attribute type ID
    signal private input expiry_date;  // Expiry date (YYYYMMDD format)

    // Public Inputs
    signal public input attr_commitment; // Commitment to the attribute
    signal public input current_date;    // Current date for expiry check
    signal public input expected_authority_id; // Authority constraint
    signal public input expected_attr_type;   // Attribute type constraint

    // Hash calculation for commitment
    component hasher = Pedersen(5);
    hasher.in[0] <== attr_secret;
    hasher.in[1] <== attr_value;
    hasher.in[2] <== authority_id;
    hasher.in[3] <== attr_type;
    hasher.in[4] <== expiry_date;

    // Verify the commitment matches
    attr_commitment === hasher.out[0];

    // Verify attribute is not expired
    component lessThan = LessThan(64);
    lessThan.in[0] <== current_date;
    lessThan.in[1] <== expiry_date;
    lessThan.out === 1; // current_date < expiry_date

    // Verify authority and attribute type match expectations
    authority_id === expected_authority_id;
    attr_type === expected_attr_type;
}

component main {public [attr_commitment, current_date, expected_authority_id, expected_attr_type]} = ProofOfAttribute();
```

### 2.2. Create the Policy Proof Circuit

Create the file `zksnarks/circuits/proof_of_policy.circom`:

```circom
pragma circom 2.0.0;

include "./proof_of_attribute.circom";

// Example for policy: (AttrType1@Auth1 AND AttrType2@Auth2)
template ProofOfPolicy() {
    // Public Inputs
    signal public input commitment1;
    signal public input commitment2;
    signal public input current_date;
    signal public input policy_id;

    // Private Inputs
    signal private input secret1;
    signal private input value1;
    signal private input auth_id1;
    signal private input type1;
    signal private input expiry1;
    
    signal private input secret2;
    signal private input value2;
    signal private input auth_id2;
    signal private input type2;
    signal private input expiry2;

    // Instantiate attribute proof circuits
    component attr_proof1 = ProofOfAttribute();
    component attr_proof2 = ProofOfAttribute();

    // Wire inputs for first attribute proof
    attr_proof1.attr_secret <== secret1;
    attr_proof1.attr_value <== value1;
    attr_proof1.authority_id <== auth_id1;
    attr_proof1.attr_type <== type1;
    attr_proof1.expiry_date <== expiry1;
    attr_proof1.attr_commitment <== commitment1;
    attr_proof1.current_date <== current_date;
    attr_proof1.expected_authority_id <== 1; // Auth1 ID
    attr_proof1.expected_attr_type <== 1;    // Type1 ID

    // Wire inputs for second attribute proof
    attr_proof2.attr_secret <== secret2;
    attr_proof2.attr_value <== value2;
    attr_proof2.authority_id <== auth_id2;
    attr_proof2.attr_type <== type2;
    attr_proof2.expiry_date <== expiry2;
    attr_proof2.attr_commitment <== commitment2;
    attr_proof2.current_date <== current_date;
    attr_proof2.expected_authority_id <== 2; // Auth2 ID
    attr_proof2.expected_attr_type <== 2;    // Type2 ID
}

component main {public [commitment1, commitment2, current_date, policy_id]} = ProofOfPolicy();
```

### 2.3. Create the Process Compliance Circuit

Create the file `zksnarks/circuits/proof_of_process.circom`:

```circom
pragma circom 2.0.0;

include "node_modules/circomlib/circuits/pedersen.circom";

template ProofOfProcessCompliance() {
    // Private Inputs
    signal private input secret_for_stepA_attestation;
    signal private input stepA_details;

    // Public Inputs
    signal public input commitment_to_stepA_attestation;
    signal public input current_process_id;
    signal public input claimed_current_step_id;
    signal public input expected_previous_step_id;

    // Hash calculation for step attestation
    component hasher = Pedersen(2);
    hasher.in[0] <== stepA_details;
    hasher.in[1] <== secret_for_stepA_attestation;

    // Verify the commitment matches
    commitment_to_stepA_attestation === hasher.out[0];

    // Verify process flow (current step follows previous step)
    claimed_current_step_id === expected_previous_step_id + 1;
}

component main {public [commitment_to_stepA_attestation, current_process_id, claimed_current_step_id, expected_previous_step_id]} = ProofOfProcessCompliance();
```

### 2.4. Compile the Circuits

Create the file `zksnarks/scripts/compile_circuits.sh`:

```bash
#!/bin/bash
CIRCOM_DIR="zksnarks/circuits"
BUILD_DIR="zksnarks/build"

# Compile ProofOfAttribute
echo "Compiling ProofOfAttribute..."
circom "$CIRCOM_DIR/proof_of_attribute.circom" --r1cs --wasm --sym -o "$BUILD_DIR/attribute"

# Compile ProofOfPolicy
echo "Compiling ProofOfPolicy..."
circom "$CIRCOM_DIR/proof_of_policy.circom" --r1cs --wasm --sym -o "$BUILD_DIR/policy"

# Compile ProofOfProcessCompliance
echo "Compiling ProofOfProcessCompliance..."
circom "$CIRCOM_DIR/proof_of_process.circom" --r1cs --wasm --sym -o "$BUILD_DIR/process"

echo "Circuit compilation complete."
```

Make the script executable and run it:

```bash
chmod +x zksnarks/scripts/compile_circuits.sh
./zksnarks/scripts/compile_circuits.sh
```

## 3. Trusted Setup and Key Generation

### 3.1. Create the Setup Script 

Create the file `zksnarks/scripts/setup.sh`:

```bash
#!/bin/bash
BUILD_DIR="zksnarks/build"

# Phase 1: Powers of Tau
echo "Starting Powers of Tau ceremony..."
snarkjs powersoftau new bn128 12 "$BUILD_DIR/pot12_0000.ptau" -v
snarkjs powersoftau contribute "$BUILD_DIR/pot12_0000.ptau" "$BUILD_DIR/pot12_0001.ptau" --name="First contribution" -v -e="random entropy"
snarkjs powersoftau prepare phase2 "$BUILD_DIR/pot12_0001.ptau" "$BUILD_DIR/pot12_final.ptau" -v

# Phase 2: Circuit-specific setup for ProofOfAttribute
CIRCUIT_NAME="proof_of_attribute"
CIRCUIT_BUILD_DIR="$BUILD_DIR/attribute"
echo "Setting up $CIRCUIT_NAME..."
snarkjs groth16 setup "$CIRCUIT_BUILD_DIR/$CIRCUIT_NAME.r1cs" "$BUILD_DIR/pot12_final.ptau" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey"
snarkjs zkey contribute "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" --name="First circuit contribution" -v -e="more random entropy"
snarkjs zkey export verificationkey "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_verification_key.json"
snarkjs zkey export solidityverifier "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "blockchain/contracts/verifiers/Verifier_${CIRCUIT_NAME}.sol"

# Phase 2: Circuit-specific setup for ProofOfPolicy
CIRCUIT_NAME="proof_of_policy"
CIRCUIT_BUILD_DIR="$BUILD_DIR/policy"
echo "Setting up $CIRCUIT_NAME..."
snarkjs groth16 setup "$CIRCUIT_BUILD_DIR/$CIRCUIT_NAME.r1cs" "$BUILD_DIR/pot12_final.ptau" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey"
snarkjs zkey contribute "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" --name="First circuit contribution" -v -e="different random entropy"
snarkjs zkey export verificationkey "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_verification_key.json"
snarkjs zkey export solidityverifier "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "blockchain/contracts/verifiers/Verifier_${CIRCUIT_NAME}.sol"

# Phase 2: Circuit-specific setup for ProofOfProcessCompliance
CIRCUIT_NAME="proof_of_process"
CIRCUIT_BUILD_DIR="$BUILD_DIR/process"
echo "Setting up $CIRCUIT_NAME..."
snarkjs groth16 setup "$CIRCUIT_BUILD_DIR/$CIRCUIT_NAME.r1cs" "$BUILD_DIR/pot12_final.ptau" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey"
snarkjs zkey contribute "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" --name="First circuit contribution" -v -e="another random entropy"
snarkjs zkey export verificationkey "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_verification_key.json"
snarkjs zkey export solidityverifier "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "blockchain/contracts/verifiers/Verifier_${CIRCUIT_NAME}.sol"

echo "Setup complete."
```

Make the script executable and run it:

```bash
chmod +x zksnarks/scripts/setup.sh
./zksnarks/scripts/setup.sh
```

## 4. Smart Contract Development

### 4.1. Create the Verifier Interface

Create the file `blockchain/contracts/interfaces/IVerifier.sol`:

```solidity
// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >= 0.5.0 < 0.9.0;

interface IVerifier {
    function verifyProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[] memory input
    ) external view returns (bool);
}
```

### 4.2. Modify the Main Contract

Create the file `blockchain/contracts/MARTZKEth.sol`:

```solidity
// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >= 0.5.0 < 0.9.0;

import "./interfaces/IVerifier.sol";

contract MARTZKEth {
    // Original MARTSIAEth structs and mappings
    struct authoritiesNames {
        bytes32 hashPart1;
        bytes32 hashPart2;
    }
    mapping (uint64 => mapping (address => authoritiesNames)) authoritiesName;

    // ... (keep all other original structs and mappings)

    // New zkSNARK-related mappings
    mapping(string => mapping(uint => mapping(uint => bytes32))) public attributeCommitments;
    
    // Verifier contract references
    IVerifier public attributeVerifier;
    IVerifier public policyVerifier;
    IVerifier public processVerifier;
    
    // Events for verification results
    event AttributeProofVerified(address indexed prover, uint indexed authorityId, uint indexed attributeType, bytes32 commitment);
    event PolicyProofVerified(address indexed prover, uint indexed policyId);
    event ProcessProofVerified(address indexed prover, uint indexed processId, uint currentStep, uint previousStep);

    // Constructor with verifier addresses
    constructor(address _attributeVerifier, address _policyVerifier, address _processVerifier) {
        attributeVerifier = IVerifier(_attributeVerifier);
        policyVerifier = IVerifier(_policyVerifier);
        processVerifier = IVerifier(_processVerifier);
    }

    // Original MARTSIAEth functions
    function setAuthoritiesNames(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public {
        authoritiesName[_instanceID][msg.sender].hashPart1 = _hash1;
        authoritiesName[_instanceID][msg.sender].hashPart2 = _hash2;
    }

    // ... (keep all other original functions)

    // Modified function to store attribute commitment
    function setUserAttributes(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2, string memory _gid, uint _authId, uint _attrType, bytes32 _commitment) public {
        // Original logic to store IPFS hash
        allUsers[_instanceID].hashPart1 = _hash1;
        allUsers[_instanceID].hashPart2 = _hash2;
        
        // Store the commitment associated with the attribute
        attributeCommitments[_gid][_authId][_attrType] = _commitment;
    }

    // Function to retrieve a specific commitment
    function getAttributeCommitment(string memory _gid, uint _authId, uint _attrType) public view returns (bytes32) {
        return attributeCommitments[_gid][_authId][_attrType];
    }

    // New zkSNARK verification functions
    function verifyAttributeProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[4] memory input // [commitment, current_date, expected_auth_id, expected_attr_type]
    ) public returns (bool) {
        uint[] memory inputArray = new uint[](4);
        for (uint i = 0; i < 4; i++) {
            inputArray[i] = input[i];
        }
        
        bool success = attributeVerifier.verifyProof(a, b, c, inputArray);
        require(success, "Attribute proof verification failed");
        
        emit AttributeProofVerified(msg.sender, input[2], input[3], bytes32(input[0]));
        return true;
    }

    function verifyPolicyProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[] memory input // [commitment1, commitment2, current_date, policy_id]
    ) public returns (bool) {
        bool success = policyVerifier.verifyProof(a, b, c, input);
        require(success, "Policy proof verification failed");
        
        emit PolicyProofVerified(msg.sender, input[input.length - 1]);
        return true;
    }

    function verifyProcessProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[] memory input // [commitment, process_id, current_step, previous_step]
    ) public returns (bool) {
        bool success = processVerifier.verifyProof(a, b, c, input);
        require(success, "Process proof verification failed");
        
        emit ProcessProofVerified(msg.sender, input[1], input[2], input[3]);
        return true;
    }
}
```

### 4.3. Update the Truffle Migration

Create the file `blockchain/migrations/2_deploy_verifiers.js`:

```javascript
const AttributeVerifier = artifacts.require("Verifier_proof_of_attribute");
const PolicyVerifier = artifacts.require("Verifier_proof_of_policy");
const ProcessVerifier = artifacts.require("Verifier_proof_of_process");
const MARTZKEth = artifacts.require("MARTZKEth");

module.exports = async function (deployer) {
  // Deploy verifiers
  await deployer.deploy(AttributeVerifier);
  await deployer.deploy(PolicyVerifier);
  await deployer.deploy(ProcessVerifier);
  
  // Deploy main contract with verifier addresses
  await deployer.deploy(
    MARTZKEth, 
    AttributeVerifier.address, 
    PolicyVerifier.address, 
    ProcessVerifier.address
  );
  
  console.log("MARTZKEth deployed to:", MARTZKEth.address);
  console.log("AttributeVerifier deployed to:", AttributeVerifier.address);
  console.log("PolicyVerifier deployed to:", PolicyVerifier.address);
  console.log("ProcessVerifier deployed to:", ProcessVerifier.address);
};
```

## 5. Python Backend Integration

### 5.1. Create the zkSNARK Utilities

Create the file `src/zksnark/__init__.py`:

```python
# Package initialization
```

Create the file `src/zksnark/utils.py`:

```python
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
    Placeholder for Pedersen hash computation.
    In a real implementation, this would use a proper Pedersen hash library.
    For simplicity, we use SHA-256 here.
    """
    # Convert all values to strings and concatenate
    combined = "".join(str(v) for v in values)
    # Use SHA-256 as a placeholder
    return int(hashlib.sha256(combined.encode()).hexdigest(), 16) % (2**253)

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
```

Create the file `src/zksnark/prover.py`:

```python
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
        
        # Format the proof for contract submission
        formatted_proof = format_proof_for_contract(proof)
        
        return formatted_proof, public_inputs
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Proof generation failed: {e}")
    finally:
        # Clean up temporary files
        os.unlink(witness_file)
        os.unlink(proof_file)
        os.unlink(public_file)
```

Create the file `src/zksnark/verifier.py`:

```python
import json
import subprocess
import tempfile
import os
from .utils import get_circuit_path

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
        # Verify the proof
        result = subprocess.run([
            "snarkjs",
            "groth16",
            "verify",
            vkey_file,
            public_file,
            proof_file
        ], capture_output=True, text=True)
        
        # Check if verification was successful
        return "OK" in result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Proof verification failed: {e}")
    finally:
        # Clean up temporary files
        os.unlink(proof_file)
        os.unlink(public_file)
```

### 5.2. Modify the Attribute Certifier

Not doing this yet


Modify the file `src/attribute_certifier.py`:

```python
import json
from datetime import datetime
import random
import block_int
from decouple import config
import io
import sqlite3
import ipfshttpclient
import argparse
import os
from authorities_info import authorities_names
from zksnark.utils import compute_pedersen_hash

# ... (keep existing functions)

def generate_attributes(roles_file):
    # ... (keep existing code until attribute assignment)
    
    # Generate a unique process instance ID
    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    process_instance_id = random.randint(10_000_000_000_000_000_000, 18_446_744_073_709_551_615)
    print(f'process instance id: {process_instance_id}')
    
    # Load roles data from JSON input
    with open(roles_file, 'r') as file:
        roles_data = json.load(file)
    roles = {key: [value] if not isinstance(value, list) else value for key, value in roles_data.items()}
    
    # Assign Authorities to each role and prepare user attributes
    authorities = authorities_names()
    dict_users = {}
    
    # For storing attribute commitments
    attribute_commitments = {}
    
    for role, attributes in roles.items():
        address = config(f'{role}_ADDRESS')
        dict_users[address] = [f'{process_instance_id}@{auth}' for auth in authorities] + attributes
        
        # Generate attribute commitments
        attribute_commitments[address] = {}
        
        for attr in attributes:
            # Parse attribute to extract authority and type
            # Assuming format like "attr_type@authority"
            parts = attr.split('@')
            attr_value = parts[0]
            auth_name = parts[1] if len(parts) > 1 else authorities[0]
            
            # Map authority name to ID (simplified)
            auth_id = authorities.index(auth_name) + 1
            
            # Determine attribute type (simplified)
            attr_type = 1  # Default type
            if "role" in attr_value.lower():
                attr_type = 1
            elif "department" in attr_value.lower():
                attr_type = 2
            # Add more type mappings as needed
            
            # Generate a random secret for this attribute
            attr_secret = random.randint(1, 2**64)
            
            # Calculate expiry date (e.g., 1 year from now)
            expiry_date = int((datetime.now().replace(year=datetime.now().year + 1)).strftime("%Y%m%d"))
            
            # Compute the commitment
            commitment_inputs = [attr_secret, attr_value, auth_id, attr_type, expiry_date]
            commitment = compute_pedersen_hash(commitment_inputs)
            
            # Store the commitment
            if auth_id not in attribute_commitments[address]:
                attribute_commitments[address][auth_id] = {}
            attribute_commitments[address][auth_id][attr_type] = {
                "commitment": commitment,
                "secret": attr_secret,
                "value": attr_value,
                "expiry": expiry_date
            }
    
    # Prepare JSON to be uploaded to IPFS
    f = io.StringIO()
    dict_users_dumped = json.dumps(dict_users)
    f.write('"process_instance_id": ' + str(process_instance_id) + '####')
    f.write(dict_users_dumped)
    f.seek(0)
    file_to_str = f.read()
    
    # Upload user data to IPFS and get the file hash
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    
    # Send attributes to the blockchain
    attribute_certifier_address = config('CERTIFIER_ADDRESS')
    private_key = config('CERTIFIER_PRIVATEKEY')
    
    # Modified to include commitment information
    for address, auth_attrs in attribute_commitments.items():
        for auth_id, type_attrs in auth_attrs.items():
            for attr_type, attr_data in type_attrs.items():
                # Send the attribute with its commitment to the blockchain
                block_int.send_users_attributes_with_commitment(
                    attribute_certifier_address,
                    private_key,
                    process_instance_id,
                    hash_file,
                    address,  # GID
                    auth_id,
                    attr_type,
                    attr_data["commitment"]
                )
    
    # Save process instance data to SQLite3 database
    conn = sqlite3.connect('../databases/attribute_certifier/attribute_certifier.db')
    x = conn.cursor()
    
    # Store the basic process data
    x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    
    # Store the attribute commitments and secrets
    # Create table if it doesn't exist
    x.execute('''
    CREATE TABLE IF NOT EXISTS attribute_commitments (
        process_instance TEXT,
        address TEXT,
        auth_id INTEGER,
        attr_type INTEGER,
        commitment TEXT,
        secret TEXT,
        value TEXT,
        expiry TEXT,
        PRIMARY KEY (process_instance, address, auth_id, attr_type)
    )
    ''')
    
    for address, auth_attrs in attribute_commitments.items():
        for auth_id, type_attrs in auth_attrs.items():
            for attr_type, attr_data in type_attrs.items():
                x.execute(
                    "INSERT OR REPLACE INTO attribute_commitments VALUES (?,?,?,?,?,?,?,?)",
                    (
                        str(process_instance_id),
                        address,
                        auth_id,
                        attr_type,
                        str(attr_data["commitment"]),
                        str(attr_data["secret"]),
                        attr_data["value"],
                        str(attr_data["expiry"])
                    )
                )
    
    conn.commit()
    
    # Store the process ID in .env
    store_process_id_to_env(str(process_instance_id))
```

### 5.3. Modify the Block Interface

Modify the file `src/block_int.py` to add the following function:

```python
def send_users_attributes_with_commitment(certifier_address, private_key, process_instance_id, ipfs_hash, gid, auth_id, attr_type, commitment):
    """Send user attributes with commitment to the blockchain."""
    # Convert IPFS hash to bytes32 parts
    ipfs_hash_bytes = ipfs_hash.encode()
    hash_part1 = Web3.toHex(ipfs_hash_bytes[:32].ljust(32, b'\0'))
    hash_part2 = Web3.toHex(ipfs_hash_bytes[32:].ljust(32, b'\0'))
    
    # Convert commitment to bytes32
    commitment_bytes32 = Web3.toHex(Web3.toBytes(commitment).rjust(32, b'\0'))
    
    # Get contract instance
    contract_instance = get_contract_instance()
    
    # Build transaction
    nonce = w3.eth.getTransactionCount(certifier_address)
    tx = contract_instance.functions.setUserAttributes(
        process_instance_id,
        hash_part1,
        hash_part2,
        gid,
        auth_id,
        attr_type,
        commitment_bytes32
    ).buildTransaction({
        'chainId': chain_id,
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei'),
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_tx = w3.eth.account.signTransaction(tx, private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt

def get_attribute_commitment(gid, auth_id, attr_type):
    """Retrieve an attribute commitment from the blockchain."""
    contract_instance = get_contract_instance()
    commitment = contract_instance.functions.getAttributeCommitment(gid, auth_id, attr_type).call()
    return commitment

def verify_attribute_proof_onchain(proof_a, proof_b, proof_c, public_inputs, sender_address):
    """Submit an attribute proof for on-chain verification."""
    contract_instance = get_contract_instance()
    
    # Build transaction
    nonce = w3.eth.getTransactionCount(sender_address)
    tx = contract_instance.functions.verifyAttributeProof(
        proof_a,
        proof_b,
        proof_c,
        public_inputs
    ).buildTransaction({
        'chainId': chain_id,
        'gas': 3000000,
        'gasPrice': w3.toWei('50', 'gwei'),
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_tx = w3.eth.account.signTransaction(tx, private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt

def verify_policy_proof_onchain(proof_a, proof_b, proof_c, public_inputs, sender_address):
    """Submit a policy proof for on-chain verification."""
    contract_instance = get_contract_instance()
    
    # Build transaction
    nonce = w3.eth.getTransactionCount(sender_address)
    tx = contract_instance.functions.verifyPolicyProof(
        proof_a,
        proof_b,
        proof_c,
        public_inputs
    ).buildTransaction({
        'chainId': chain_id,
        'gas': 3000000,
        'gasPrice': w3.toWei('50', 'gwei'),
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_tx = w3.eth.account.signTransaction(tx, private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt
```

### 5.4. Modify the Server Authority


Not doing this yet


Modify the file `src/server_authority.py`:

```python
import socket
import ssl
import threading
import random
from datetime import datetime
from hashlib import sha512
import block_int
import authority_key_generation
import ipfshttpclient
import sqlite3
from decouple import config
import argparse
import json
from authorities_info import authorities_names
from zksnark.verifier import verify_proof_offchain

class AuthorityServer:
    def __init__(self, authority_number):
        self.authority_number = authority_number

    # Generates the Authority key for a specific reader
    def generate_key_auth(self, gid, process_instance_id, reader_address):
        return authority_key_generation.generate_user_key(self.authority_number, gid, process_instance_id, reader_address)

    # Verify attribute proof instead of handshake
    def verify_attribute_proof(self, proof_data, public_inputs):
        # Verify the proof matches the expected authority
        if int(public_inputs[2]) != self.authority_number:
            print(f"Authority mismatch: expected {self.authority_number}, got {public_inputs[2]}")
            return False
        
        # Verify the proof off-chain
        return verify_proof_offchain("proof_of_attribute", proof_data, public_inputs)

    # Manages client connections, processing proof verification and key generation
    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")
        connected = True
        while connected:
            msg_length = conn.recv(int(HEADER)).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                
                message = msg.split('§')
                
                # Handle key request with zkSNARK proof
                if message[0] == f"Auth-{self.authority_number} - RequestKey":
                    # Parse the message
                    # Format: "Auth-X - RequestKey§GID§process_instance_id§reader_address§proof_data§public_inputs"
                    gid = message[1]
                    process_instance_id = message[2]
                    reader_address = message[3]
                    proof_data = json.loads(message[4])
                    public_inputs = json.loads(message[5])
                    
                    # Verify the attribute proof
                    if self.verify_attribute_proof(proof_data, public_inputs):
                        # Generate the key if proof is valid
                        user_sk1 = self.generate_key_auth(gid, process_instance_id, reader_address)
                        conn.send(b'Here is my partial key: ' + user_sk1)
                    else:
                        conn.send(b'Proof verification failed')
        
        conn.close()

    # Starts the listening for incoming client connections
    def start(self):
        bindsocket.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            newsocket, fromaddr = bindsocket.accept()
            conn = context.wrap_socket(newsocket, server_side=True)
            thread = threading.Thread(target=self.handle_client, args=(conn, fromaddr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
```

### 5.5. Modify the Reader

Not doing this yet

Modify the file `src/reader.py`:

```python
from charm.toolbox.pairinggroup import *
from charm.core.engine.util import bytesToObject
import cryptocode
import block_int
import ipfshttpclient
import json
import os
import base64
import socket
import ssl
from maabe_class import *
from decouple import config
import sqlite3
import argparse
from datetime import datetime
from authorities_info import authorities_addresses_and_names_separated
from zksnark.prover import generate_proof
from zksnark.utils import compute_pedersen_hash

# ... (keep existing helper functions)

def request_key_with_proof(authority_number, gid, process_instance_id, reader_address, attr_secret, attr_value, attr_type, expiry_date):
    """Request a key from an authority using a zkSNARK proof."""
    # Prepare the circuit inputs
    current_date = int(datetime.now().strftime("%Y%m%d"))
    
    # Compute the commitment
    commitment = compute_pedersen_hash([attr_secret, attr_value, authority_number, attr_type, expiry_date])
    
    # Prepare the input for the circuit
    input_data = {
        "attr_secret": attr_secret,
        "attr_value": attr_value,
        "authority_id": authority_number,
        "attr_type": attr_type,
        "expiry_date": expiry_date,
        "attr_commitment": commitment,
        "current_date": current_date,
        "expected_authority_id": authority_number,
        "expected_attr_type": attr_type
    }
    
    # Generate the proof
    proof_data, public_inputs = generate_proof("proof_of_attribute", input_data)
    
    # Connect to the authority server
    PORT = 5060 + authority_number - 1
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    HEADER = config('HEADER')
    DISCONNECT_MESSAGE = "!DISCONNECT"
    
    # Setup SSL context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile='../Keys/server.crt')
    context.load_cert_chain(certfile='../Keys/client.crt', keyfile='../Keys/client.key')
    
    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = context.wrap_socket(client, server_hostname=SERVER)
    client.connect(ADDR)
    
    # Send the request with proof
    message = f"Auth-{authority_number} - RequestKey§{gid}§{process_instance_id}§{reader_address}§{json.dumps(proof_data)}§{json.dumps(public_inputs)}"
    message = message.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (int(HEADER) - len(send_length))
    client.send(send_length)
    client.send(message)
    
    # Receive the response
    response = client.recv(2048)
    
    # Close the connection
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    
    # Parse the response
    if response.startswith(b'Here is my partial key: '):
        return response[len(b'Here is my partial key: '):]
    else:
        raise Exception(f"Failed to get key from authority {authority_number}: {response.decode()}")

def start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged):
    """Main decryption workflow with zkSNARK proofs."""
    # Retrieve attribute data from the database
    conn = sqlite3.connect('../databases/reader/reader.db')
    x = conn.cursor()
    
    # Retrieve public parameters
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    
    # For each authority, generate a proof and request a key
    for authority_name in authorities_names:
        # Get authority number
        f = authority_name[0].upper() + authority_name[1:].lower()
        prefix = ''.join(filter(str.isalpha, f))
        number = ''.join(filter(str.isdigit, f))
        transformed_string = f"{prefix}-{number}"
        authority_number = int(number)
        
        # Retrieve attribute data for this authority
        x.execute("""
            SELECT attr_secret, attr_value, attr_type, expiry_date 
            FROM reader_attributes 
            WHERE process_instance=? AND authority_number=? AND reader_address=?
        """, (str(process_instance_id), authority_number, sender_address))
        
        attr_data = x.fetchone()
        if not attr_data:
            raise Exception(f"No attribute data found for authority {authority_number}")
        
        attr_secret, attr_value, attr_type, expiry_date = attr_data
        
        # Request key with zkSNARK proof
        user_sk1 = request_key_with_proof(
            authority_number,
            sender_address,  # GID
            process_instance_id,
            sender_address,
            int(attr_secret),
            int(attr_value),
            int(attr_type),
            int(expiry_date)
        )
        
        # Convert to object
        user_sk1 = bytesToObject(user_sk1, groupObj)
        merged = merge_dicts(merged, user_sk1)
    
    # Complete the user secret key
    user_sk = {'GID': sender_address, 'keys': merged}
    
    # Retrieve and decrypt the ciphertext
    response = block_int.retrieve_MessageIPFSLink(message_id)
    ciphertext_link = response[0]
    getfile = api.cat(ciphertext_link)
    ciphertext_dict = json.loads(getfile)
    sender = response[1]
    
    # Verify ciphertext metadata
    correctly_decrypted = False
    if (ciphertext_dict['metadata']['process_instance_id'] == int(process_instance_id) and
            ciphertext_dict['metadata']['message_id'] == int(message_id) and
            ciphertext_dict['metadata']['sender'] == sender):
        
        slice_check = ciphertext_dict['header']
        if len(slice_check) == 1:
            actual_decryption(ciphertext_dict['header'][0], public_parameters, user_sk, output_folder)
            correctly_decrypted = True
        elif len(slice_check) > 1:
            for remaining in slice_check:
                if remaining['Slice_id'] == slice_id:
                    actual_decryption(remaining, public_parameters, user_sk, output_folder)
                    correctly_decrypted = True
    
    if not correctly_decrypted:
        raise RuntimeError("Decryption error: Please check that the message_id and slice_id are specified correctly.")
```

## 6. Update Shell Scripts

### 6.1. Create the zkSNARK Setup Script

Create the file `sh_files/setup_zksnarks.sh`:

```bash
#!/bin/bash

# Run the circuit compilation script
echo "Compiling zkSNARK circuits..."
./zksnarks/scripts/compile_circuits.sh

# Run the trusted setup script
echo "Performing trusted setup..."
./zksnarks/scripts/setup.sh

echo "zkSNARK setup complete."
```

Make the script executable:

```bash
chmod +x sh_files/setup_zksnarks.sh
```

### 6.2. Modify the Deployment Script

Modify the file `sh_files/deployment.sh` to deploy the verifier contracts and the enhanced MARTZKEth contract.

### 6.3. Modify the Certification Script

Modify the file `sh_files/certifications.sh` to use the enhanced attribute certification process with commitments.

### 6.4. Modify the Decipher Script

Modify the file `sh_files/decipher.sh` to use the zkSNARK-based key request process.

## 7. Testing

### 7.1. Test the Attribute Proof Circuit

Create the file `zksnarks/test/test_attribute_circuit.js`:

```javascript
const { expect } = require("chai");
const path = require("path");
const wasm_tester = require("circom_tester").wasm;

describe("ProofOfAttribute Circuit", function() {
    let circuit;

    before(async function() {
        circuit = await wasm_tester(path.join(__dirname, "../circuits/proof_of_attribute.circom"));
    });

    it("should generate a valid witness for valid inputs", async function() {
        const input = {
            attr_secret: 12345,
            attr_value: 67890,
            authority_id: 1,
            attr_type: 2,
            expiry_date: 20301231, // December 31, 2030
            attr_commitment: 0, // Will be calculated by the test
            current_date: 20250522, // May 22, 2025
            expected_authority_id: 1,
            expected_attr_type: 2
        };

        // Calculate the commitment (this should match the circuit's calculation)
        // For testing, we'll use a simplified approach
        const commitment = calculateCommitment(
            input.attr_secret,
            input.attr_value,
            input.authority_id,
            input.attr_type,
            input.expiry_date
        );
        input.attr_commitment = commitment;

        const witness = await circuit.calculateWitness(input);
        await circuit.checkConstraints(witness);
    });

    it("should fail if the commitment doesn't match", async function() {
        const input = {
            attr_secret: 12345,
            attr_value: 67890,
            authority_id: 1,
            attr_type: 2,
            expiry_date: 20301231,
            attr_commitment: 999999, // Incorrect commitment
            current_date: 20250522,
            expected_authority_id: 1,
            expected_attr_type: 2
        };

        try {
            await circuit.calculateWitness(input);
            expect.fail("Circuit should have failed with incorrect commitment");
        } catch (error) {
            // Expected to fail
        }
    });

    it("should fail if the attribute is expired", async function() {
        const input = {
            attr_secret: 12345,
            attr_value: 67890,
            authority_id: 1,
            attr_type: 2,
            expiry_date: 20200101, // January 1, 2020 (expired)
            attr_commitment: 0, // Will be calculated
            current_date: 20250522, // May 22, 2025
            expected_authority_id: 1,
            expected_attr_type: 2
        };

        // Calculate the commitment
        const commitment = calculateCommitment(
            input.attr_secret,
            input.attr_value,
            input.authority_id,
            input.attr_type,
            input.expiry_date
        );
        input.attr_commitment = commitment;

        try {
            await circuit.calculateWitness(input);
            expect.fail("Circuit should have failed with expired attribute");
        } catch (error) {
            // Expected to fail
        }
    });

    // Helper function to calculate commitment (simplified for testing)
    function calculateCommitment(secret, value, authId, attrType, expiry) {
        // This is a simplified hash function for testing
        // In the real circuit, this would be a proper cryptographic hash
        return (secret + value + authId + attrType + expiry) % (2**32);
    }
});
```

### 7.2. Test the Python zkSNARK Integration

Create the file `tests/unit/test_zksnark_integration.py`:

```python
import unittest
import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from zksnark.utils import compute_pedersen_hash
from zksnark.prover import generate_proof
from zksnark.verifier import verify_proof_offchain

class TestZkSnarkIntegration(unittest.TestCase):
    def setUp(self):
        # Prepare test data
        self.attr_secret = 12345
        self.attr_value = 67890
        self.authority_id = 1
        self.attr_type = 2
        self.expiry_date = int((datetime.now().replace(year=datetime.now().year + 1)).strftime("%Y%m%d"))
        self.current_date = int(datetime.now().strftime("%Y%m%d"))
        
        # Compute the commitment
        self.commitment = compute_pedersen_hash([
            self.attr_secret,
            self.attr_value,
            self.authority_id,
            self.attr_type,
            self.expiry_date
        ])
    
    def test_proof_generation_and_verification(self):
        # Prepare circuit input
        input_data = {
            "attr_secret": self.attr_secret,
            "attr_value": self.attr_value,
            "authority_id": self.authority_id,
            "attr_type": self.attr_type,
            "expiry_date": self.expiry_date,
            "attr_commitment": self.commitment,
            "current_date": self.current_date,
            "expected_authority_id": self.authority_id,
            "expected_attr_type": self.attr_type
        }
        
        # Generate proof
        proof, public_inputs = generate_proof("proof_of_attribute", input_data)
        
        # Verify proof
        is_valid = verify_proof_offchain("proof_of_attribute", proof, public_inputs)
        
        # Assert
        self.assertTrue(is_valid, "Proof verification should succeed")
    
    def test_invalid_proof_verification(self):
        # Prepare circuit input with wrong commitment
        input_data = {
            "attr_secret": self.attr_secret,
            "attr_value": self.attr_value,
            "authority_id": self.authority_id,
            "attr_type": self.attr_type,
            "expiry_date": self.expiry_date,
            "**attr_commitment**": self.commitment + 1,  # Wrong commitment
            "current_date": self.current_date,
            "expected_authority_id": self.authority_id,
            "expected_attr_type": self.attr_type
        }
        
        # This should fail during proof generation
        with self.assertRaises(Exception):
            proof, public_inputs = generate_proof("proof_of_attribute", input_data)

if __name__ == '__main__':
    unittest.main()
```

## 8. End-to-End Integration

### 8.1. Run the Complete Setup

```bash
# Setup zkSNARKs
./sh_files/setup_zksnarks.sh

# Deploy contracts
./sh_files/deployment.sh

# Setup databases and IPFS
./sh_files/db_and_IPFS.sh

# Start authority servers
./sh_files/authorities.sh

# Run attribute certification
./sh_files/certifications.sh -i json_files/roles.json

# Encrypt data with policy
./sh_files/cipher.sh -i input_files/example.txt -o output_files/encrypted.json -p json_files/policies.json

# Decrypt data with zkSNARK proofs
./sh_files/decipher.sh -m 1 -s 1 --reader_name READER -o output_files/
```

## 9. Conclusion

This implementation guide provides detailed, step-by-step instructions for integrating zkSNARKs into the MARTSIA system. By following these steps, you can transform MARTSIA into MARTZK, enhancing privacy and verifiability in attribute management, policy enforcement, and business process compliance.

The key components of the implementation include:
1. Circuit development for attribute proofs, policy proofs, and process compliance proofs
2. Trusted setup and key generation for the zkSNARK schemes
3. Smart contract modifications to support on-chain verification
4. Python backend integration for proof generation and verification
5. Updates to the existing MARTSIA components to use zkSNARK proofs

This implementation maintains the core functionality of MARTSIA while adding the privacy and verifiability benefits of zkSNARKs, creating a more secure and privacy-preserving system for the EV supply chain scenario.