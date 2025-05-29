from charm.toolbox.pairinggroup import *
from charm.core.engine.util import bytesToObject
import cryptocode
import block_int
import ipfshttpclient
import json
import os
import base64
import socket # Added for zkSNARK
import ssl    # Added for zkSNARK
from maabe_class import *
from decouple import config
import sqlite3
import argparse
from datetime import datetime # Added for zkSNARK
from authorities_info import authorities_addresses_and_names_separated
import sys
from path_utils import get_reader_db
# --- zkSNARK Imports ---
from zksnark.prover import generate_proof
from zksnark.utils import compute_pedersen_hash
# --- End zkSNARK Imports ---

def merge_dicts(*dict_args):
    """
    Merge dictionaries, with precedence given to latter dictionaries
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def retrieve_data(authority_address, process_instance_id):
    """
    Retrieve Authorities and public parameters for the given process instance
    """
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    return authorities, public_parameters

def generate_public_parameters(process_instance_id):
    """
    Generate and store public parameters if consistent across Authorities
    """
    check_authorities = []
    check_parameters = []
    for authority_address in authorities_addresses:
        data = retrieve_data(authority_address, process_instance_id)
        check_authorities.append(data[0])
        check_parameters.append(data[1])
    
    # FIX: Relaxed coordination check (same fix as data_owner.py)
    if len(set(check_authorities)) == 1 and check_parameters:
        params_link = check_parameters[0]
        getfile = api.cat(params_link)
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (str(process_instance_id), params_link, getfile))
        conn.commit()
        print(f"[INFO] Reader stored parameters from: {params_link}")
    else:
        print(f"[INFO] No consistent parameters found across Authorities for process {process_instance_id}")
        sys.exit(1)

def base64_to_file(encoded_data, output_file_path):
    """
    Decode a Base64 encoded string and save it as a file
    """
    try:
        decoded_data = base64.b64decode(encoded_data.encode("utf-8"))
        with open(output_file_path, "wb") as file:
            file.write(decoded_data)
    except Exception as e:
        print(f"Error decoding Base64 to file: {e}")

def retrieve_public_parameters(process_instance_id):
    """
    Retrieve public parameters for the process instance
    """
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    try:
        public_parameters = result[0][2]
    except IndexError:
        generate_public_parameters(process_instance_id)
        x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
        result = x.fetchall()
        public_parameters = result[0][2]
    return public_parameters

def actual_decryption(remaining, public_parameters, user_sk, output_folder):
    """
    Perform decryption using public parameters and user secret key
    """
    print(f"DEBUG: ========== Starting actual_decryption ==========")
    print(f"DEBUG: User secret key structure: {user_sk}")
    print(f"DEBUG: User GID: {user_sk.get('GID', 'None')}")
    print(f"DEBUG: User keys: {list(user_sk.get('keys', {}).keys()) if 'keys' in user_sk else 'No keys'}")
    
    # Show detailed attribute information
    if 'keys' in user_sk:
        for key_name, key_data in user_sk['keys'].items():
            print(f"DEBUG: Key '{key_name}': {type(key_data)}")
            if hasattr(key_data, 'keys'):
                print(f"DEBUG:   Sub-keys: {list(key_data.keys())}")
    
    test = remaining["CipheredKey"].encode("utf-8")
    ct = bytesToObject(test, groupObj)
    print(f"DEBUG: Ciphertext object type: {type(ct)}")
    print(f"DEBUG: Ciphertext object keys: {list(ct.keys()) if hasattr(ct, 'keys') else 'No keys method'}")
    
    # Try to extract policy from ciphertext if possible
    if hasattr(ct, 'get') and ct.get('policy'):
        print(f"DEBUG: Embedded policy in ciphertext: {ct['policy']}")
    elif hasattr(ct, '__dict__'):
        print(f"DEBUG: Ciphertext attributes: {ct.__dict__}")
    else:
        print(f"DEBUG: Ciphertext object structure: {ct}")
    
    print(f"DEBUG: About to call maabe.decrypt()...")
    print(f"DEBUG: Public parameters keys: {list(public_parameters.keys())}")
    
    try:
        v2 = maabe.decrypt(public_parameters, user_sk, ct)
        print(f"DEBUG: Decryption successful! Result type: {type(v2)}")
        
        # FIX: Extract the symmetric key directly from metadata
        # MA-ABE is now only used for access control
        v2_serialized = groupObj.serialize(v2)
        print(f"DEBUG: Serialized v2 type: {type(v2_serialized)}")
        print(f"DEBUG: Serialized v2 length: {len(v2_serialized)}")
        print(f"DEBUG: Serialized v2 (first 50 bytes): {v2_serialized[:50]}...")
        
        # Check if we have the symmetric key stored directly in metadata
        if 'SymmetricKey' in remaining:
            print(f"DEBUG: Found symmetric key directly in metadata")
            symmetric_key = remaining['SymmetricKey']
            print(f"DEBUG: Retrieved symmetric key: {symmetric_key[:50] if symmetric_key else 'Failed'}...")
        elif 'EncryptedSymmetricKey' in remaining:
            print(f"DEBUG: Found encrypted symmetric key in metadata")
            encrypted_symmetric_key = remaining['EncryptedSymmetricKey']
            
            # Decrypt the symmetric key using the MA-ABE decrypted element
            symmetric_key = cryptocode.decrypt(encrypted_symmetric_key, str(v2_serialized))
            print(f"DEBUG: Decrypted symmetric key: {symmetric_key[:50] if symmetric_key else 'Failed'}...")
            
            if symmetric_key is False:
                print(f"DEBUG: Failed to decrypt symmetric key from metadata")
                raise Exception("Failed to decrypt symmetric key from metadata")
        else:
            print(f"DEBUG: No symmetric key found in metadata, falling back to hash method")
            # Fall back to the old hash method
            import hashlib
            symmetric_key = hashlib.sha256(v2_serialized).hexdigest()
        
        output_folder_path = os.path.abspath(output_folder)
        print(f"DEBUG: About to decrypt file content with symmetric key...")
        
        decryptedFile = cryptocode.decrypt(remaining["EncryptedFile"], symmetric_key)
        print(f"DEBUG: cryptocode.decrypt result type: {type(decryptedFile)}")
        
        if decryptedFile is False:
            print(f"DEBUG: File decryption failed")
            raise Exception("File decryption failed with symmetric key")
        
        print(f"DEBUG: Decryption successful!")
        base64_to_file(decryptedFile, output_folder_path+"/"+remaining["FileName"])
        print(f"DEBUG: ========== Decryption completed successfully ==========")
    except Exception as e:
        print(f"DEBUG: MA-ABE decryption failed with exception: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        print(f"DEBUG: ========== Decryption failed ==========")
        raise

# --- New zkSNARK Function ---
def request_key_with_proof(authority_number, gid, process_instance_id, reader_address, attr_secret, attr_value, attr_type, expiry_date):
    """Request a key from an authority using a zkSNARK proof."""
    # Prepare the circuit inputs
    current_date = int(datetime.now().strftime("%Y%m%d"))

    # Convert attr_value to number for consistent commitment computation
    if isinstance(attr_value, str) and not attr_value.isdigit():
        # Use the SAME method as compute_pedersen_hash in utils.py
        attr_value_numeric = sum(ord(c) * (256 ** i) for i, c in enumerate(attr_value[:8]))
    else:
        attr_value_numeric = int(attr_value) if isinstance(attr_value, str) else attr_value
        
    print(f"DEBUG: Commitment calculation inputs:")
    print(f"  attr_secret: {attr_secret} (type: {type(attr_secret)})")
    print(f"  attr_value: '{attr_value}' -> {attr_value_numeric} (type: {type(attr_value_numeric)})")
    print(f"  authority_number: {authority_number} (type: {type(authority_number)})")
    print(f"  attr_type: {attr_type} (type: {type(attr_type)})")
    print(f"  expiry_date: {expiry_date} (type: {type(expiry_date)})")
        
    commitment = compute_pedersen_hash([attr_secret, attr_value_numeric, authority_number, attr_type, expiry_date])
    print(f"DEBUG: Computed commitment: {commitment}")

    # Prepare the input for the circuit (ensure values are strings for snarkjs)
    # The commitment is now returned as a single integer value
    # Use the same numeric value that was used for commitment computation
    input_data = {
        "attr_secret": str(attr_secret),
        "attr_value": str(attr_value_numeric),  # Use the same numeric value from commitment computation
        "authority_id": str(authority_number),
        "attr_type": str(attr_type),
        "expiry_date": str(expiry_date),
        "attr_commitment": str(commitment),  # Single commitment value
        "current_date": str(current_date),
        "expected_authority_id": str(authority_number),
        "expected_attr_type": str(attr_type)
    }
    
    print(f"DEBUG: Circuit input data: {input_data}")

    # Generate the proof
    # Note: Ensure the proving key (.zkey) is accessible
    proof_data, public_inputs = generate_proof("proof_of_attribute", input_data)
    print(f"DEBUG: Generated proof public inputs: {public_inputs}")

    # Connect to the authority server
    PORT = 5060 + authority_number - 1 # Default port convention from MARTSIA
    SERVER = socket.gethostbyname(socket.gethostname()) # Assuming authority runs locally
    ADDR = (SERVER, PORT)
    FORMAT = "utf-8"
    HEADER = config("HEADER")
    DISCONNECT_MESSAGE = "!DISCONNECT"
    
    # Get the correct hostname for SSL from .env
    SSL_HOSTNAME = config("SERVER_SNI_HOSTNAME")

    # Setup SSL context (ensure cert paths are correct)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="../Keys/server.crt")
    context.load_cert_chain(certfile="../Keys/client.crt", keyfile="../Keys/client.key")

    client = None # Initialize client to None
    try:
        # Connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client = context.wrap_socket(client, server_hostname=SSL_HOSTNAME)  # Use correct hostname for SSL
        client.connect(ADDR)

        # Send the request with proof - FIXED: Use the correct message format that server expects
        # Format: "Auth-X - ZK-Generate your part of my key§GID§process_instance_id§reader_address§proof_data_json§public_inputs_json"
        message = f"Auth-{authority_number} - ZK-Generate your part of my key§{gid}§{process_instance_id}§{reader_address}§{json.dumps(proof_data)}§{json.dumps(public_inputs)}"
        message_bytes = message.encode(FORMAT)
        msg_length = len(message_bytes)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b" " * (int(HEADER) - len(send_length))
        client.send(send_length)
        client.send(message_bytes)

        # Receive the response
        response = client.recv(2048) # Adjust buffer size if needed

        # Parse the response
        if response.startswith(b"Here is my partial key: "):
            return response[len(b"Here is my partial key: "):]
        else:
            raise Exception(f"Failed to get key from authority {authority_number}: {response.decode(FORMAT, errors='ignore')}")

    except ConnectionRefusedError:
        raise Exception(f"Connection refused by authority {authority_number} at {ADDR}. Is the server running?")
    except ssl.SSLError as e:
         raise Exception(f"SSL Error connecting to authority {authority_number}: {e}")
    except Exception as e:
        raise Exception(f"Error communicating with authority {authority_number}: {e}")
    finally:
        # Close the connection if it was opened
        if client:
            try:
                # Send disconnect message politely
                disconnect_msg_bytes = DISCONNECT_MESSAGE.encode(FORMAT)
                disconnect_len = str(len(disconnect_msg_bytes)).encode(FORMAT)
                disconnect_len += b" " * (int(HEADER) - len(disconnect_len))
                client.send(disconnect_len)
                client.send(disconnect_msg_bytes)
            except Exception:
                pass # Ignore errors during disconnect attempt
            finally:
                client.close()
# --- End New zkSNARK Function ---

def start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged):
    """Main decryption workflow with zkSNARK proofs."""
    
    # DEBUG: Show what process instance ID was passed to this function
    print(f"DEBUG: start() function called with process_instance_id: {process_instance_id} (type: {type(process_instance_id)})")
    
    # Retrieve public parameters
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    # Define hash functions H and F for the public parameters
    H = lambda x: groupObj.hash(x, G2)
    F = lambda x: groupObj.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # --- Modified Key Retrieval using zkSNARK --- 
    # Instead of iterating through all authorities, iterate through user's actual attributes
    print("Retrieving user's actual attributes from local database...")
    
    x.execute("""
        SELECT DISTINCT authority_number 
        FROM reader_attributes 
        WHERE process_instance=? AND reader_address=?
    """, (str(process_instance_id), sender_address))
    
    user_authorities = x.fetchall()
    if not user_authorities:
        raise Exception(f"No attributes found for user {sender_address} in process {process_instance_id}")
    
    print(f"Found attributes for authorities: {[auth[0] for auth in user_authorities]}")
    
    for authority_row in user_authorities:
        authority_number = authority_row[0]
        
        print(f"Requesting key from Authority {authority_number}...")

        # Retrieve the reader's attribute secret and details for this authority
        x.execute("""
            SELECT attr_secret, attr_value, attr_type, expiry_date 
            FROM reader_attributes 
            WHERE process_instance=? AND authority_number=? AND reader_address=?
            LIMIT 1 
        """, (str(process_instance_id), authority_number, sender_address))
        
        attr_data = x.fetchone()
        if not attr_data:
            raise Exception(f"Reader attribute data not found locally for authority {authority_number} and process {process_instance_id}")
        
        # Ensure data is converted to correct types (especially integers)
        try:
            attr_secret = int(attr_data[0])
            # FIX: Use raw attr_value string to match certifier's commitment computation
            attr_value = attr_data[1]  # Keep as string, same as certifier does
            attr_type = int(attr_data[2])
            expiry_date = int(attr_data[3])
        except (ValueError, TypeError) as e:
             raise Exception(f"Invalid attribute data format retrieved from local DB for authority {authority_number}: {e}")

        print(f"Requesting key from Authority {authority_number} using zkSNARK proof...")
        # Request key with zkSNARK proof
        user_sk1_bytes = request_key_with_proof(
            authority_number,
            sender_address,  # GID
            process_instance_id,
            sender_address,
            attr_secret,
            attr_value,
            attr_type,
            expiry_date
        )
        
        # Convert received bytes to object
        user_sk1 = bytesToObject(user_sk1_bytes, groupObj)
        merged = merge_dicts(merged, user_sk1)
        print(f"Received partial key from Authority {authority_number}.")
    # --- End Modified Key Retrieval ---

    # Complete the user secret key
    user_sk = {"GID": sender_address, "keys": merged}
    
    print(f"DEBUG: ========== Final User Secret Key ==========")
    print(f"DEBUG: Final user_sk GID: {user_sk['GID']}")
    print(f"DEBUG: Final user_sk keys: {list(user_sk['keys'].keys())}")
    print(f"DEBUG: Merged keys structure: {merged}")
    for key_name, key_data in merged.items():
        print(f"DEBUG: Merged key '{key_name}': {type(key_data)}")
        if hasattr(key_data, 'keys'):
            print(f"DEBUG:   Merged sub-keys: {list(key_data.keys())}")
    print(f"DEBUG: ===============================================")
    
    # Retrieve and decrypt the ciphertext
    print(f"Retrieving ciphertext for message ID: {message_id}")
    response = block_int.retrieve_MessageIPFSLink(message_id)
    ciphertext_link = response[0]
    getfile = api.cat(ciphertext_link)
    ciphertext_dict = json.loads(getfile)
    sender = response[1]
    
    # Verify ciphertext metadata
    print("Verifying ciphertext metadata...")
    correctly_decrypted = False
    if (ciphertext_dict["metadata"]["process_instance_id"] == int(process_instance_id) and
            ciphertext_dict["metadata"]["message_id"] == int(message_id) and
            ciphertext_dict["metadata"]["sender"] == sender):
        
        slice_check = ciphertext_dict["header"]
        print(f"Found {len(slice_check)} slice(s) in ciphertext header.")
        if len(slice_check) == 1:
            print(f"Decrypting single slice...")
            actual_decryption(ciphertext_dict["header"][0], public_parameters, user_sk, output_folder)
            correctly_decrypted = True
        elif len(slice_check) > 1:
            print(f"Searching for slice ID: {slice_id}")
            for remaining in slice_check:
                if remaining["Slice_id"] == slice_id:
                    print(f"Decrypting slice ID: {slice_id}...")
                    actual_decryption(remaining, public_parameters, user_sk, output_folder)
                    correctly_decrypted = True
                    break # Found and decrypted the slice
            if not correctly_decrypted:
                 print(f"Slice ID {slice_id} not found in the ciphertext header.")
    else:
        print("Ciphertext metadata mismatch!")
        print(f"Expected Process ID: {process_instance_id}, Got: {ciphertext_dict['metadata']['process_instance_id']}")
        print(f"Expected Message ID: {message_id}, Got: {ciphertext_dict['metadata']['message_id']}")
        print(f"Expected Sender: {sender}, Got: {ciphertext_dict['metadata']['sender']}")

    if not correctly_decrypted:
        raise RuntimeError("Decryption error: Please check message_id/slice_id or metadata consistency.")
    else:
        print("Decryption successful.")


if __name__ == "__main__":
    authorities_addresses, authorities_names = authorities_addresses_and_names_separated()
    process_instance_id_env = config("PROCESS_INSTANCE_ID")
    
    # DEBUG: Show what was read from .env
    print(f"DEBUG: Raw value from .env PROCESS_INSTANCE_ID: '{process_instance_id_env}'")
    print(f"DEBUG: Type of value from .env: {type(process_instance_id_env)}")
    
    # Connection to SQLite3 reader database - FIXED PATH
    db_path = get_reader_db()
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    conn = sqlite3.connect(db_path)
    x = conn.cursor()
    
    # Create reader_attributes table if it doesn't exist (FIXED PRIMARY KEY)
    x.execute("""
    CREATE TABLE IF NOT EXISTS reader_attributes (
        process_instance TEXT,
        reader_address TEXT,
        authority_number INTEGER,
        attr_secret TEXT,
        attr_value TEXT,
        attr_type INTEGER,
        expiry_date TEXT,
        PRIMARY KEY (process_instance, reader_address, authority_number, attr_type)
    )
    """)
    # Create public_parameters table if it doesn't exist
    x.execute("""
    CREATE TABLE IF NOT EXISTS public_parameters (
        process_instance TEXT PRIMARY KEY,
        ipfs_link TEXT,
        parameters_data BLOB
    )
    """)
    conn.commit()

    groupObj = PairingGroup("SS512")
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001") # Ensure IPFS daemon is running
    
    try:
        process_instance_id = int(process_instance_id_env)
        print(f"DEBUG: Converted process_instance_id to int: {process_instance_id}")
        print(f"DEBUG: Type after conversion: {type(process_instance_id)}")
    except (TypeError, ValueError):
        print(f"Error: Invalid PROCESS_INSTANCE_ID found in .env: '{process_instance_id_env}'. Please ensure it's a valid integer.")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="Reader details",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--message_id", type=int, required=True, help="message id")
    parser.add_argument("-s", "--slice_id", type=int, required=True, help="slice id")
    parser.add_argument("--reader_name", type=str, required=True, help="Name of the requester (e.g., READER)")
    parser.add_argument("-o", "--output_folder", type=str, required=True, help="Path to the output folder")
    args = parser.parse_args()
    
    message_id = args.message_id
    slice_id = args.slice_id
    try:
        sender_address = config(args.reader_name + "_ADDRESS")
    except Exception as e:
        print(f"Error: Could not find address for reader '{args.reader_name}' in .env file. Missing key: {args.reader_name}_ADDRESS")
        sys.exit(1)
        
    output_folder = args.output_folder
    if not os.path.isdir(output_folder):
        print(f"Error: Output folder '{output_folder}' does not exist.")
        sys.exit(1)
        
    merged = {}
    
    try:
        print(f"Starting decryption process for Message ID: {message_id}, Slice ID: {slice_id}")
        start(process_instance_id, message_id, slice_id, sender_address, output_folder, merged)
    except Exception as e:
        print(f"\n--- An error occurred during the decryption process ---")
        print(f"Error: {e}")
        print("---------------------------------------------------------")
        sys.exit(1)
    finally:
        conn.close() # Ensure database connection is closed
