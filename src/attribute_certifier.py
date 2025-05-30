import json
from datetime import datetime
import random
import block_int
from decouple import config
import io
import sqlite3
import ipfshttpclient
import argparse
from authorities_info import authorities_names
from zksnark.utils import compute_pedersen_hash  # assumes you have Poseidon or placeholder
import os
import hashlib

# Save generated process ID to .env
def store_process_id_to_env(value):
    name = 'PROCESS_INSTANCE_ID'
    with open('../src/.env', 'r', encoding='utf-8') as file:
        data = file.readlines()
    # Remove existing line
    data = [line for line in data if not line.startswith(name)]
    # Add new one
    data.append(f"{name}={value}\n")
    with open('../src/.env', 'w', encoding='utf-8') as file:
        file.writelines(data)

# Main logic: assign attributes, generate commitments, upload to IPFS, log to blockchain & SQLite
def generate_attributes(roles_file):
    # Try to read existing process instance ID from .env first
    try:
        process_instance_id = int(config('PROCESS_INSTANCE_ID'))
        print(f'Using existing process instance ID from .env: {process_instance_id}')
    except:
        # Only generate new ID if none exists
    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    process_instance_id = random.randint(10**19, 2**64 - 1)
        print(f'Generated new process instance ID: {process_instance_id}')
        # Save the new ID to .env
        store_process_id_to_env(str(process_instance_id))

    # Load role-to-user mapping from input JSON
    with open(roles_file, 'r') as file:
        roles_data = json.load(file)
    roles = {k: v if isinstance(v, list) else [v] for k, v in roles_data.items()}
    print(f"DEBUG: Loaded roles: {roles}")

    authorities = authorities_names()
    dict_users = {}
    attribute_commitments = {}

    for role, attributes in roles.items():
        address = config(f'{role}_ADDRESS')
        dict_users[address] = [f'{process_instance_id}@{auth}' for auth in authorities] + attributes
        attribute_commitments[address] = {}
        print(f"DEBUG: Processing role {role} with address {address}")

        for attr in attributes:
            parts = attr.split('@')
            attr_value = parts[0]
            auth_name = parts[1] if len(parts) > 1 else authorities[0]
            auth_id = authorities.index(auth_name) + 1

            # Determine attribute type
            attr_type = 1 if "role" in attr_value.lower() else 2 if "department" in attr_value.lower() else 0

            # Generate secrets + expiry + commitment
            attr_secret = random.randint(1, 2**64)
            expiry_date = int((datetime.now().replace(year=datetime.now().year + 1)).strftime("%Y%m%d"))
            
            # Convert attr_value to number for consistent commitment computation with circuit
            if isinstance(attr_value, str) and not attr_value.isdigit():
                # Use the SAME method as compute_pedersen_hash in utils.py
                attr_value_numeric = sum(ord(c) * (256 ** i) for i, c in enumerate(attr_value[:8]))
            else:
                attr_value_numeric = int(attr_value) if isinstance(attr_value, str) else attr_value
            
            commitment_inputs = [attr_secret, attr_value_numeric, auth_id, attr_type, expiry_date]
            commitment = compute_pedersen_hash(commitment_inputs)
            
            # commitment is now a single integer value
            commitment_str = str(commitment)  # Store as string

            if auth_id not in attribute_commitments[address]:
                attribute_commitments[address][auth_id] = {}
            attribute_commitments[address][auth_id][attr_type] = {
                "commitment": commitment,
                "secret": attr_secret,
                "value": attr_value,
                "expiry": expiry_date
            }

    # IPFS: Upload process metadata
    f = io.StringIO()
    dict_users_dumped = json.dumps(dict_users)
    f.write('"process_instance_id": ' + str(process_instance_id) + '####')
    f.write(dict_users_dumped)
    f.seek(0)
    file_to_str = f.read()

    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    hash_file = api.add_json(file_to_str)
    print(f'IPFS hash: {hash_file}')

    # Send attributes + commitments to blockchain
    certifier_address = config('CERTIFIER_ADDRESS')
    private_key = config('CERTIFIER_PRIVATEKEY')

    for address, auth_attrs in attribute_commitments.items():
        for auth_id, type_attrs in auth_attrs.items():
            for attr_type, attr_data in type_attrs.items():
                # Use the commitment value directly
                commitment_for_blockchain = attr_data["commitment"]
                block_int.send_users_attributes_with_commitment(
                    certifier_address,
                    private_key,
                    process_instance_id,
                    hash_file,
                    address,
                    auth_id,
                    attr_type,
                    commitment_for_blockchain
                )

    # Save all info into SQLite
    conn = sqlite3.connect('../databases/attribute_certifier/attribute_certifier.db')
    x = conn.cursor()

    try:
    # Save user<->IPFS basic mapping
        print("DEBUG: Inserting into user_attributes table...")
    x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
        print("DEBUG: user_attributes insert successful")

    # Create commitment table if missing
        print("DEBUG: Creating attribute_commitments table...")
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
        print("DEBUG: attribute_commitments table created successfully")

    # Save detailed commitment info
        print("DEBUG: Inserting commitment data...")
        insert_count = 0
    for address, auth_attrs in attribute_commitments.items():
        for auth_id, type_attrs in auth_attrs.items():
            for attr_type, attr_data in type_attrs.items():
                    # Store commitment as comma-separated string
                    commitment_str = f"{attr_data['commitment']}"
                x.execute(
                    "INSERT OR REPLACE INTO attribute_commitments VALUES (?,?,?,?,?,?,?,?)",
                    (
                        str(process_instance_id),
                        address,
                        auth_id,
                        attr_type,
                            commitment_str,
                        str(attr_data["secret"]),
                        attr_data["value"],
                        str(attr_data["expiry"])
                    )
                )
                    insert_count += 1
                    print(f"DEBUG: Inserted commitment for {address}, auth {auth_id}, type {attr_type}")

        print(f"DEBUG: About to save to database, dict_users has {len(dict_users)} entries")
        print(f"DEBUG: attribute_commitments has {len(attribute_commitments)} entries")
        print(f"DEBUG: Inserted {insert_count} commitment records")

        print("DEBUG: Committing database changes...")
    conn.commit()
        print("DEBUG: Database commit successful")
        
    except Exception as e:
        print(f"ERROR: Database operation failed: {e}")
        conn.rollback()
        raise e
    finally:
    conn.close()
        print("DEBUG: Database connection closed")

# CLI Interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Certifier configuration')
    parser.add_argument('-i', '--input', type=str, help='Specify the path of the roles.json file')
    args = parser.parse_args()
    if args.input:
        generate_attributes(args.input)
    else:
        parser.print_help()
