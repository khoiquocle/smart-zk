# MARTZK System: Step-by-Step Execution Guide

This guide provides the commands to set up and run the complete MARTZK system after implementing the zkSNARK components.

**Assumptions:**
*   You have cloned the `MARTSIA-demo` repository and are in the root directory.
*   You have installed all prerequisites: Python 3.x, Node.js (with npm), Circom, SnarkJS, Truffle, IPFS, Ganache (or another Ethereum test network).
*   You have updated the `.env` file (`src/.env`) with your specific addresses (e.g., Authority addresses, Certifier address, Reader addresses) and private keys.
*   You have replaced the original shell scripts (`deployment.sh`, `certifications.sh`, `decipher.sh`) with the updated MARTZK versions provided previously.
*   You have created the necessary input files (e.g., `json_files/roles.json`, `json_files/policies.json`, `input_files/example.txt`).
*   Your local Ethereum test network (e.g., Ganache) and IPFS daemon are running.

**Execution Steps:**

**1. Initial Setup (If not already done):**

```bash
# Install Node.js dependencies (if needed)
npm install

# Install Python dependencies (if needed)
pip install -r requirements.txt
```

**2. zkSNARK Circuit Compilation and Trusted Setup:**

*   This step compiles the Circom circuits and generates the proving/verification keys. It only needs to be run once unless circuits are modified.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the zkSNARK setup script
./setup_zksnarks.sh 

# Return to the root directory (optional, depends on subsequent script locations)
cd .. 
```
*   **Expected Outcome:** `zksnarks/build/` directory populated with `.r1cs`, `.wasm`, `.sym`, `.zkey`, and `verification_key.json` files. `blockchain/contracts/verifiers/` directory populated with `Verifier_*.sol` files.

**3. Deploy Smart Contracts:**

*   This deploys the Verifier contracts and the main `MARTZKEth` contract to your test network and updates the `.env` file with their addresses.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the deployment script
./deployment.sh

# Return to the root directory
cd .. 
```
*   **Expected Outcome:** Contracts deployed on the test network. `src/.env` file updated with `CONTRACT_ADDRESS_MARTZKETH`, `CONTRACT_ADDRESS_ATTRIBUTE_VERIFIER`, etc.

**4. Setup Databases and IPFS:**

*   Initializes SQLite databases and checks IPFS connection.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the DB and IPFS setup script
./db_and_IPFS.sh

# Return to the root directory
cd .. 
```
*   **Expected Outcome:** Database files created/initialized in the `databases/` directory.

**5. Start Authority Servers:**

*   Starts the MA-ABE Authority servers in the background. These now handle zkSNARK-based key requests.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the authorities script
./authorities.sh

# Return to the root directory
cd .. 
```
*   **Expected Outcome:** Multiple Python processes running, one for each Authority server, listening on their respective ports.

**6. Attribute Certification (MARTZK Enhanced):**

*   Runs the certification process, assigning attributes and generating/storing zkSNARK commitments.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the certifications script with the roles file
# Replace json_files/roles.json with your actual roles file path
./certifications.sh -i ../json_files/roles.json 

# Return to the root directory
cd .. 
```
*   **Expected Outcome:** Attribute data and commitments stored in the certifier database and potentially on the blockchain via `MARTZKEth.setUserAttributes`. Reader secrets stored securely (e.g., in `databases/reader/reader.db` based on the modified `reader.py`). `PROCESS_INSTANCE_ID` updated in `src/.env`.

**7. Data Encryption (Cipher):**

*   Encrypts data using MA-ABE based on a policy.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the cipher script
# Replace paths with your actual input file, output file, and policy file
./cipher.sh -i ../input_files/example.txt -o ../output_files/encrypted_data.json -p ../json_files/policies.json

# Return to the root directory
cd .. 
```
*   **Expected Outcome:** Encrypted data (`encrypted_data.json`) created in the output folder. IPFS link stored on the blockchain.

**8. Data Decryption (Decipher - MARTZK Enhanced):**

*   Initiates decryption. The reader script internally generates zkSNARK proofs to request keys from Authorities.

```bash
# Navigate to the shell scripts directory
cd sh_files

# Run the decipher script
# Replace parameters with your actual message ID, slice ID (if needed),
# reader name (e.g., READER1), and output folder path.
# Example (assuming message ID 1, slice ID 1, reader READER1):
./decipher.sh -m <MESSAGE_ID> -s <SLICE_ID> --requester_name <READER_NAME> -o ../output_files/

# Example for single-slice message:
# ./decipher.sh -m <MESSAGE_ID> --requester_name <READER_NAME> -o ../output_files/

# Return to the root directory
cd .. 
```
*   **Expected Outcome:** The original plaintext file (`example.txt` in the example) should appear in the specified output folder (`../output_files/`). The console output will show communication with Authorities and proof generation/verification steps (if logging is added).

**Stopping Authority Servers:**

*   You will need to manually stop the background Authority server processes when finished.

```bash
# Find the process IDs (PIDs) of the authority servers
pgrep -f "python3 ../src/server_authority.py"

# Kill the processes using their PIDs
# Replace <PID1> <PID2> ... with the actual PIDs found above
kill <PID1> <PID2> ... 
```

This sequence provides a complete run-through of the MARTZK system using the command line.