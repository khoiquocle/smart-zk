from web3 import Web3
from decouple import config
import json
import base64

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# MARTZK Dual-Function Implementation
# Phase 1: Authority Setup - Use MA-ABE contract for setElementHashed, sendElements, etc.
compiled_contract_path = '../blockchain/build/contracts/MARTSIAEth.json'
deployed_contract_address = config('CONTRACT_ADDRESS_MARTSIA')

# Phase 2+: ZK-SNARK contract for verification operations
ZKSNARK_CONTRACT_PATH = '../blockchain/build/contracts/MARTZKEth.json'
ZKSNARK_CONTRACT_ADDRESS = config('CONTRACT_ADDRESS_MARTZKETH')

verbose = False
chain_id = web3.eth.chain_id

# Dual Contract Support Functions
def get_maabe_contract():
    """Get MA-ABE contract instance for authority setup operations"""
    with open('../blockchain/build/contracts/MARTSIAEth.json') as file:
        contract_json = json.load(file)
        abi = contract_json['abi']
    address = config('CONTRACT_ADDRESS_MARTSIA')
    return web3.eth.contract(address=address, abi=abi)

def get_zksnark_contract():
    """Get ZK-SNARK contract instance for verification and commitment operations"""
    with open('../blockchain/build/contracts/MARTZKEth.json') as file:
        contract_json = json.load(file)
        abi = contract_json['abi']
    address = config('CONTRACT_ADDRESS_MARTZKETH')
    return web3.eth.contract(address=address, abi=abi)

def get_contract_instance():
    """Default contract instance - using MA-ABE for authority operations"""
    return get_maabe_contract()

def get_nonce(ETH_address):
    # Retrieve the transaction count (nonce) for the given address
    return web3.eth.get_transaction_count(ETH_address)

def activate_contract(attribute_certifier_address, private_key):
    # Activate the contract by updating the majority count (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(attribute_certifier_address),
        'gasPrice': web3.eth.gas_price,
        'from': attribute_certifier_address
    }
    message = contract.functions.updateMajorityCount().buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def __send_txt__(signed_transaction_type):
    # Send a signed transaction and handle failures
    try:
        transaction_hash = web3.eth.send_raw_transaction(signed_transaction_type)
        return transaction_hash
    except Exception as e:
        print(e)
        if input("Do you want to try again (y/n)?") == 'y':
            return __send_txt__(signed_transaction_type)
        else:
            raise Exception("Transaction failed")

# MA-ABE Authority Setup Functions
def send_authority_names(authority_address, private_key, process_instance_id, hash_file):
    # Send name of Authority to the contract (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(authority_address),
        'gasPrice': web3.eth.gas_price,
        'from': authority_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setAuthoritiesNames(int(process_instance_id), base64_bytes[:32],
                                                     base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieve_authority_names(authority_address, process_instance_id):
    # Retrieve name of Authority from the contract (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getAuthoritiesNames(authority_address, int(process_instance_id)).call()
    message_bytes = base64.b64decode(message)
    message = message_bytes.decode('ascii')
    return message

def sendHashedElements(authority_address, private_key, process_instance_id, elements):
    # Send hashed elements to the contract (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(authority_address),
        'gasPrice': web3.eth.gas_price,
        'from': authority_address
    }
    hashPart1 = elements[0].encode('utf-8')
    hashPart2 = elements[1].encode('utf-8')
    message = contract.functions.setElementHashed(process_instance_id, hashPart1[:32], hashPart1[32:],
                                                  hashPart2[:32], hashPart2[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieveHashedElements(eth_address, process_instance_id):
    # Retrieve hashed elements from the contract (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getElementHashed(eth_address, process_instance_id).call()
    hashedg11 = message[0].decode('utf-8')
    hashedg21 = message[1].decode('utf-8')
    return hashedg11, hashedg21

def sendElements(authority_address, private_key, process_instance_id, elements):
    # Send elements to the contract (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(authority_address),
        'gasPrice': web3.eth.gas_price,
        'from': authority_address
    }
    hashPart1 = elements[0]
    hashPart2 = elements[1]
    message = contract.functions.setElement(process_instance_id, hashPart1[:32], hashPart1[32:64],
                                            hashPart1[64:] + b'000000', hashPart2[:32], hashPart2[32:64],
                                            hashPart2[64:] + b'000000').buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieveElements(eth_address, process_instance_id):
    # Retrieve elements from the contract (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getElement(eth_address, process_instance_id).call()
    g11 = message[0] + message[1]
    g11 = g11[:90]
    g21 = message[2] + message[3]
    g21 = g21[:90]
    return g11, g21

def send_parameters_link(authority_address, private_key, process_instance_id, hash_file):
    # Send public parameters link (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(authority_address),
        'gasPrice': web3.eth.gas_price,
        'from': authority_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setPublicParameters(int(process_instance_id), base64_bytes[:32],
                                                     base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieve_parameters_link(authority_address, process_instance_id):
    # Retrieve public parameters link (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getPublicParameters(authority_address, int(process_instance_id)).call()
    message_bytes = base64.b64decode(message)
    return message_bytes.decode('ascii')

def send_publicKey_link(authority_address, private_key, process_instance_id, hash_file):
    # Send public key link (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(authority_address),
        'gasPrice': web3.eth.gas_price,
        'from': authority_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setPublicKey(int(process_instance_id), base64_bytes[:32],
                                              base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieve_publicKey_link(eth_address, process_instance_id):
    # Retrieve public key link (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getPublicKey(eth_address, int(process_instance_id)).call()
    message_bytes = base64.b64decode(message)
    return message_bytes.decode('ascii')

# Data Operations (using MA-ABE for compatibility)
def send_MessageIPFSLink(dataOwner_address, private_key, message_id, hash_file):
    # Send message IPFS link (MA-ABE operation for compatibility)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(dataOwner_address),
        'gasPrice': web3.eth.gas_price,
        'from': dataOwner_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setIPFSLink(int(message_id), base64_bytes[:32], base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    print(private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieve_MessageIPFSLink(message_id):
    # Retrieve message IPFS link (MA-ABE operation for compatibility)
    contract = get_maabe_contract()
    message = contract.functions.getIPFSLink(int(message_id)).call()
    sender = message[0]
    message_bytes = base64.b64decode(message[1])
    ipfs_link = message_bytes.decode('ascii')
    return ipfs_link, sender

# Legacy MA-ABE User Attributes (for compatibility)
def send_users_attributes(attribute_certifier_address, private_key, process_instance_id, hash_file):
    # Send user attributes (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(attribute_certifier_address),
        'gasPrice': web3.eth.gas_price,
        'from': attribute_certifier_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setUserAttributes(int(process_instance_id), base64_bytes[:32],
                                                   base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieve_users_attributes(process_instance_id):
    # Retrieve user attributes (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getUserAttributes(int(process_instance_id)).call()
    message_bytes = base64.b64decode(message)
    return message_bytes.decode('ascii')

def send_publicKey_readers(reader_address, private_key, hash_file):
    # Send reader public key (MA-ABE operation)
    contract = get_maabe_contract()
    tx = {
        'nonce': get_nonce(reader_address),
        'gasPrice': web3.eth.gas_price,
        'from': reader_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setPublicKeyReaders(base64_bytes[:32], base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = __send_txt__(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    if verbose:
        print(tx_receipt)

def retrieve_publicKey_readers(reader_address):
    # Retrieve reader public key (MA-ABE operation)
    contract = get_maabe_contract()
    message = contract.functions.getPublicKeyReaders(reader_address).call()
    message_bytes = base64.b64decode(message)
    return message_bytes.decode('ascii')

# ZK-SNARK Enhanced Functions (use ZK-SNARK contract)
def send_users_attributes_with_commitment(certifier_address, private_key, process_instance_id, ipfs_hash, gid, auth_id, attr_type, commitment):
    """Send user attributes with commitment to the ZK-SNARK contract (Phase 2: Attribute Certification)"""
    # Convert IPFS hash to bytes32 parts
    ipfs_hash_bytes = ipfs_hash.encode()
    hash_part1 = Web3.toHex(ipfs_hash_bytes[:32].ljust(32, b'\0'))
    hash_part2 = Web3.toHex(ipfs_hash_bytes[32:].ljust(32, b'\0'))
    
    # Convert commitment to bytes32
    commitment_bytes32 = Web3.toHex(Web3.toBytes(commitment).rjust(32, b'\0'))
    
    # Get ZK-SNARK contract instance
    contract = get_zksnark_contract()
    
    # Build transaction
    nonce = web3.eth.getTransactionCount(certifier_address)
    tx = contract.functions.setUserAttributes(
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
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt

def retrieve_users_attributes_with_zksnark(process_instance_id):
    """Retrieve user attributes from ZK-SNARK contract"""
    contract = get_zksnark_contract()
    # Use the getUserAttributes function (just added to the contract)
    try:
        message = contract.functions.getUserAttributes(int(process_instance_id)).call()
        # The ZK-SNARK contract returns raw bytes, not base64-encoded
        # Convert bytes to string, removing null bytes
        message_string = message.rstrip(b'\x00').decode('ascii')
        return message_string
    except Exception as e:
        print(f"[ERROR] Failed to retrieve user attributes from ZK-SNARK contract: {e}")
        return ""

def get_attribute_commitment(gid, auth_id, attr_type):
    """Get attribute commitment from ZK-SNARK contract"""
    contract = get_zksnark_contract()
    return contract.functions.getAttributeCommitment(gid, auth_id, attr_type).call()

# ZK-SNARK Verification Functions (use ZK-SNARK contract)
def verify_attribute_proof(proof_a, proof_b, proof_c, public_inputs):
    """Verify attribute proof using ZK-SNARK contract"""
    contract = get_zksnark_contract()
    return contract.functions.verifyAttributeProof(proof_a, proof_b, proof_c, public_inputs).call()

def verify_policy_proof(proof_a, proof_b, proof_c, public_inputs):
    """Verify policy proof using ZK-SNARK contract"""
    contract = get_zksnark_contract()
    return contract.functions.verifyPolicyProof(proof_a, proof_b, proof_c, public_inputs).call()

def verify_process_proof(proof_a, proof_b, proof_c, public_inputs):
    """Verify process proof using ZK-SNARK contract"""
    contract = get_zksnark_contract()
    return contract.functions.verifyProcessProof(proof_a, proof_b, proof_c, public_inputs).call()

