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
import json
from decouple import config
import argparse
from authorities_info import authorities_names
# Import the zkSNARK verifier
from zksnark.verifier import ZkSnarkVerifier

"""
Class representing the Authority
Handles key generation, message signing, secure client-server communication,
and zkSNARK proof verification
"""
class AuthorityServer:
    def __init__(self, authority_number):
        self.authority_number = authority_number
        # Initialize zkSNARK verifier
        try:
            self.zk_verifier = ZkSnarkVerifier()
            self.zk_enabled = True
            print(f"[INFO] zkSNARK verification enabled for Authority {authority_number}")
        except Exception as e:
            self.zk_enabled = False
            print(f"[WARNING] zkSNARK verification disabled: {e}")

    # Generates the Authority key for a specific reader
    def generate_key_auth(self, gid, process_instance_id, reader_address):
        return authority_key_generation.generate_user_key(self.authority_number, gid, process_instance_id, reader_address)

    # Generates a unique number for secure handshake
    def generate_number_to_sign(self, process_instance_id, reader_address):
        connection = sqlite3.connect('../databases/authority'+str(self.authority_number)+'/authority'+str(self.authority_number)+'.db')
        x = connection.cursor()
        now = int(datetime.now().strftime("%Y%m%d%H%M%S%f"))
        random.seed(now)
        number_to_sign = random.randint(1, 2 ** 64)
        x.execute("INSERT OR IGNORE INTO handshake_numbers VALUES (?,?,?)",
                  (process_instance_id, reader_address, str(number_to_sign)))
        connection.commit()
        return number_to_sign

    # Verifies the handshake using the Reader's signature and IPFS-stored public key
    def check_handshake(self, process_instance_id, reader_address, signature):
        connection = sqlite3.connect('../databases/authority'+str(self.authority_number)+'/authority'+str(self.authority_number)+'.db')
        x = connection.cursor()
        x.execute("SELECT * FROM handshake_numbers WHERE process_instance=? AND reader_address=?",
                  (process_instance_id, reader_address))
        result = x.fetchall()
        number_to_sign = result[0][2]
        msg = str(number_to_sign).encode()
        public_key_ipfs_link = block_int.retrieve_publicKey_readers(reader_address)
        api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
        getfile = api.cat(public_key_ipfs_link).split(b'###')
        public_key_n = int(getfile[1].decode('utf-8'))
        public_key_e = int(getfile[2].decode('utf-8').rstrip('"'))
        if getfile[0].split(b': ')[1].decode('utf-8') == reader_address:
            hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
            hashFromSignature = pow(int(signature), public_key_e, public_key_n)
            print("Signature valid:", hash == hashFromSignature)
            return hash == hashFromSignature

    # Verifies a zkSNARK proof of attribute possession
    def verify_attribute_proof(self, process_instance_id, reader_address, proof, public_signals):
        """
        Verify a zkSNARK proof claiming possession of an attribute from this authority
        """
        if not self.zk_enabled:
            print("[WARNING] zkSNARK verification requested but not enabled")
            return False
            
        try:
            # Log the verification attempt
            connection = sqlite3.connect('../databases/authority'+str(self.authority_number)+'/authority'+str(self.authority_number)+'.db')
            x = connection.cursor()
            
            # Extract authority ID from public signals to ensure it matches this authority
            authority_id = public_signals[-2]  # expected_authority_id is the second-to-last signal
            
            # Ensure the proof is for an attribute from this authority
            # The circuit sends numeric authority IDs (1, 2, 3, 4), not "Auth1", "Auth2" format
            if int(authority_id) != self.authority_number:
                print(f"[ERROR] Proof is for authority {authority_id}, but this is authority {self.authority_number}")
                return False
                
            # Verify the proof using the zkSNARK verifier
            verification_result = self.zk_verifier.verify_attribute_proof(proof, public_signals)
            
            # Log the verification result
            x.execute("INSERT OR REPLACE INTO proof_verifications VALUES (?,?,?,?,?)",
                     (str(process_instance_id), reader_address, json.dumps(proof), 
                      json.dumps(public_signals), verification_result))
            connection.commit()
            
            print(f"[INFO] zkSNARK proof verification for {reader_address}: {verification_result}")
            return verification_result
            
        except Exception as e:
            print(f"[ERROR] zkSNARK verification failed: {e}")
            return False

    # Manages client connections, processing handshake requests and key generation
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
                if message[0] == "Auth-" + str(self.authority_number) + " - Start handshake":
                    number_to_sign = self.generate_number_to_sign(message[1], message[2])
                    conn.send(b'Number to sign: ' + str(number_to_sign).encode())
                if message[0] == "Auth-" + str(self.authority_number) + " - Generate your part of my key":
                    if self.check_handshake(message[2], message[3], message[4]):
                        user_sk1 = self.generate_key_auth(message[1], message[2], message[3])
                        conn.send(b'Here is my partial key: ' + user_sk1)
                        
                # New message type for zkSNARK-based key generation
                if message[0] == "Auth-" + str(self.authority_number) + " - ZK-Generate your part of my key":
                    # Format: [command, gid, process_instance_id, reader_address, proof_json, public_signals_json]
                    if len(message) >= 6:
                        # Parse the proof and public signals
                        try:
                            proof = json.loads(message[4])
                            public_signals = json.loads(message[5])
                            
                            # Verify the zkSNARK proof
                            if self.verify_attribute_proof(message[2], message[3], proof, public_signals):
                                # Generate the key if proof is valid
                                user_sk1 = self.generate_key_auth(message[1], message[2], message[3])
                                conn.send(b'Here is my partial key: ' + user_sk1)
                            else:
                                conn.send(b'Error: Invalid zkSNARK proof')
                        except json.JSONDecodeError:
                            conn.send(b'Error: Invalid JSON in proof or public signals')
                    else:
                        conn.send(b'Error: Missing required parameters for ZK key generation')
        conn.close()

    # Starts the listening for incoming client connections
    def start(self):
        # Ensure the database has the necessary table for proof verifications
        connection = sqlite3.connect('../databases/authority'+str(self.authority_number)+'/authority'+str(self.authority_number)+'.db')
        x = connection.cursor()
        x.execute('''
        CREATE TABLE IF NOT EXISTS proof_verifications (
            process_instance TEXT,
            reader_address TEXT,
            proof TEXT,
            public_signals TEXT,
            verification_result BOOLEAN,
            PRIMARY KEY (process_instance, reader_address)
        )
        ''')
        connection.commit()
        
        bindsocket.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            newsocket, fromaddr = bindsocket.accept()
            conn = context.wrap_socket(newsocket, server_side=True)
            thread = threading.Thread(target=self.handle_client, args=(conn, fromaddr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    authorities_names = authorities_names()
    number_of_authorities = len(authorities_names)
    print("[STARTING] server is starting...")
    parser = argparse.ArgumentParser(description='Authority')
    parser.add_argument('-a', '--authority', type=int, help='Authority number')
    parser.add_argument('--disable-zk', action='store_true', help='Disable zkSNARK verification')
    args = parser.parse_args()
    if args.authority < 1 or args.authority > number_of_authorities:
        print("Invalid authority number")
        exit()
    HEADER = config('HEADER')
    PORT = 5060 + args.authority - 1
    server_cert = '../Keys/server.crt'
    server_key = '../Keys/server.key'
    client_certs = '../Keys/client.crt'
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"
    
    # Secure channel setup with SSL
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=client_certs)
    bindsocket = socket.socket()
    bindsocket.bind(ADDR)
    bindsocket.listen(5)
    
    # Initialize the Authority with the specified Authority number
    authority_number = args.authority
    authority_server = AuthorityServer(args.authority)
    if args.disable_zk:
        authority_server.zk_enabled = False
        print(f"[INFO] zkSNARK verification disabled by command line argument")
    authority_server.start()

