# MARTZK System: End-to-End Workflow

This document outlines the step-by-step operational workflow of the MARTZK system after the successful implementation of zkSNARKs, integrating privacy-preserving proofs into the MARTSIA framework.

**Actors:**
*   **System Administrator/Deployer:** Sets up the initial system.
*   **Attribute Certifier:** Defines roles and certifies initial user attributes.
*   **Authorities (Multiple):** Manage MA-ABE keys and verify attribute proofs.
*   **Data Owner:** Encrypts data under an access policy.
*   **Reader:** Requests access and decrypts data.

**Workflow Stages:**

**Phase 1: System Setup**

1.  **zkSNARK Setup:**
    *   The System Administrator runs the `compile_circuits.sh` script to compile all Circom circuits (`proof_of_attribute`, `proof_of_policy`, `proof_of_process`).
    *   The Administrator runs the `setup.sh` script to perform the trusted setup (Powers of Tau + circuit-specific) for each circuit, generating:
        *   Proving Keys (`.zkey` files in `zksnarks/build/`) - Kept secure, distributed to provers (Readers).
        *   Verification Keys (`verification_key.json` in `zksnarks/build/`) - Publicly available for off-chain verification.
        *   Solidity Verifier Contracts (`Verifier_*.sol` in `blockchain/contracts/verifiers/`) - Ready for deployment.

2.  **Smart Contract Deployment:**
    *   The Administrator runs the `deployment.sh` script (or equivalent Truffle commands):
        *   Deploys the generated Verifier contracts (`Verifier_proof_of_attribute.sol`, etc.) to the blockchain.
        *   Deploys the main `MARTZKEth.sol` contract, providing the addresses of the deployed Verifier contracts during construction.

3.  **Authority Setup:**
    *   Each Authority runs its setup process (similar to original MARTSIA, e.g., using `authority_key_generation.py` initially) to generate its MA-ABE master keys.
    *   Authorities publish their public parameters and names to the `MARTZKEth` contract (using functions like `setPublicParameters`, `setAuthoritiesNames`).
    *   Each Authority starts its server (`server_authority.py`), now configured to listen for zkSNARK-based key requests instead of the old handshake.

4.  **Database and IPFS Setup:**
    *   The Administrator runs `db_and_IPFS.sh` to initialize necessary databases (for certifier, authorities, reader) and ensure the IPFS node is running.

**Phase 2: Attribute Certification**

5.  **Role Definition:**
    *   The Attribute Certifier defines roles and associated attributes in a file (e.g., `roles.json`).

6.  **Attribute Certification Process (Enhanced):**
    *   The Certifier runs the modified `attribute_certifier.py` (e.g., via `certifications.sh -i roles.json`):
        *   Assigns attributes to users based on roles.
        *   For each attribute assigned to a user (GID):
            *   Generates a unique, random `attr_secret`.
            *   Determines `attr_value`, `auth_id`, `attr_type`, `expiry_date`.
            *   Computes the `attr_commitment` using the defined hash function (e.g., Pedersen hash of secret, value, IDs, expiry).
            *   Stores the `attr_secret`, `attr_value`, `auth_id`, `attr_type`, `expiry_date`, and `commitment` securely associated with the user GID (e.g., in the certifier's database or encrypted for the user).
            *   Calls the `MARTZKEth.setUserAttributes` function on the blockchain, providing the user's GID, the IPFS hash of general attribute info, and the specific `auth_id`, `attr_type`, and `commitment` for this attribute.
        *   The user (Reader) must securely receive their `attr_secret` for each certified attribute (e.g., via an encrypted channel or secure database lookup).

**Phase 3: Data Encryption**

7.  **Policy Definition:**
    *   The Data Owner defines an access policy (e.g., in `policies.json`) specifying which attributes (identified by type and authority) are required for decryption.

8.  **Data Encryption Process:**
    *   The Data Owner runs the `data_owner.py` script (e.g., via `cipher.sh`):
        *   Encrypts the plaintext data using a symmetric key.
        *   Encrypts the symmetric key using the MA-ABE scheme (`maabe.encrypt`) under the defined access policy, referencing the public parameters retrieved from the blockchain.
        *   Stores the encrypted data and the MA-ABE encrypted symmetric key (CipheredKey) on IPFS.
        *   Calls `MARTZKEth.setIPFSLink` on the blockchain to store the IPFS hash associated with a message ID.
        *   **(Optional MARTZK Enhancement):** The Data Owner might generate a `proof_of_policy` to demonstrate the policy used for encryption is valid or meets certain criteria, storing this proof alongside the ciphertext or on-chain.

**Phase 4: Data Access and Decryption**

9.  **Reader Identifies Data:**
    *   The Reader identifies the `message_id` of the desired data.

10. **Key Request Process (zkSNARK-based):**
    *   The Reader runs the modified `reader.py` (e.g., via `decipher.sh`):
        *   Retrieves the required policy associated with the data (implicitly from the MA-ABE ciphertext or explicitly from metadata).
        *   Determines which attributes (and thus which Authorities) are needed to satisfy the policy.
        *   For *each* required Authority (`authority_number`):
            *   Retrieves the corresponding locally stored `attr_secret`, `attr_value`, `attr_type`, `expiry_date` for the attribute needed from that Authority.
            *   Computes the `attr_commitment` matching the one stored on-chain.
            *   Prepares the input JSON for the `proof_of_attribute.circom` circuit.
            *   Calls the local `zksnark.prover.generate_proof("proof_of_attribute", input_data)` function, using the Proving Key (`.zkey`) for the attribute circuit. This generates the `proof` and `public_inputs`.
            *   Connects securely (SSL) to the target Authority's server (`server_authority.py`).
            *   Sends a "RequestKey" message containing its GID, the proof data, and public inputs.
        *   The Authority Server (`server_authority.py`):
            *   Receives the request.
            *   Calls the local `zksnark.verifier.verify_proof_offchain("proof_of_attribute", proof, public_inputs)` function using the Verification Key (`verification_key.json`).
            *   Checks if the `expected_authority_id` in the public inputs matches its own ID.
            *   If verification succeeds and the authority ID matches, it generates the MA-ABE partial secret key for the Reader (`authority_key_generation.generate_user_key`) and sends it back.
            *   If verification fails, it sends an error message.
        *   The Reader receives the partial key (or error) from the Authority.

11. **Data Decryption:**
    *   After successfully collecting all required partial keys from the relevant Authorities:
        *   The Reader combines the partial keys into the full MA-ABE user secret key (`user_sk`).
        *   Retrieves the encrypted data and MA-ABE ciphertext from IPFS using the link obtained from `MARTZKEth.getIPFSLink`.
        *   Uses the `user_sk` and the public parameters to decrypt the MA-ABE ciphertext (`maabe.decrypt`) to recover the symmetric key.
        *   Uses the symmetric key to decrypt the actual data.

**(Optional) Policy Proof Verification:**
*   If the Data Owner required a policy proof from the Reader before granting access (e.g., revealing the IPFS link), the Reader would first generate a `proof_of_policy` using their attribute secrets and commitments, submit it (on-chain or off-chain) for verification, and only proceed to key requests upon successful policy verification.

This workflow replaces the insecure handshake in MARTSIA with verifiable zkSNARK proofs, ensuring that Readers only receive keys if they can cryptographically prove possession of valid, non-expired attributes from the correct authorities, without revealing the attributes themselves to the Authorities during the key request.