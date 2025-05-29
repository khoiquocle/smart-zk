#!/usr/bin/env python3
"""
MARTZK Attribute Distribution Script
This script reads the attribute secrets from the certifier database
and distributes them to the appropriate reader databases.
"""

import sqlite3
import json
import sys
import os
from decouple import config
from path_utils import get_attribute_certifier_db, get_reader_db

def distribute_attributes():
    """Distribute attribute secrets from certifier to readers"""
    
    # Get the current process instance ID
    process_instance_id = config('PROCESS_INSTANCE_ID')
    
    print(f"[INFO] Distributing attributes for process instance: {process_instance_id}")
    
    # Connect to certifier database
    certifier_db_path = get_attribute_certifier_db()
    if not os.path.exists(certifier_db_path):
        print(f"[ERROR] Certifier database not found at {certifier_db_path}")
        return False
    
    certifier_conn = sqlite3.connect(certifier_db_path)
    certifier_cursor = certifier_conn.cursor()
    
    # Get all user attributes from certifier (using correct column names)
    certifier_cursor.execute("""
        SELECT address, auth_id, attr_type, secret, value, expiry, commitment
        FROM attribute_commitments 
        WHERE process_instance = ?
    """, (process_instance_id,))
    
    attributes = certifier_cursor.fetchall()
    
    if not attributes:
        print(f"[ERROR] No attributes found for process instance {process_instance_id}")
        return False
    
    print(f"[INFO] Found {len(attributes)} attribute records to distribute")
    
    # Connect to reader database
    reader_db_path = get_reader_db()
    if not os.path.exists(os.path.dirname(reader_db_path)):
        os.makedirs(os.path.dirname(reader_db_path))
    
    reader_conn = sqlite3.connect(reader_db_path)
    reader_cursor = reader_conn.cursor()
    
    # Ensure reader_attributes table exists
    reader_cursor.execute("""
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
    
    # Insert attributes into reader database
    distributed_count = 0
    for attr in attributes:
        reader_address, authority_id, attr_type, attr_secret, attr_value, expiry_date, commitment = attr
        
        try:
            reader_cursor.execute("""
                INSERT OR REPLACE INTO reader_attributes 
                (process_instance, reader_address, authority_number, attr_secret, attr_value, attr_type, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (process_instance_id, reader_address, authority_id, str(attr_secret), str(attr_value), attr_type, str(expiry_date)))
            
            distributed_count += 1
            print(f"[SUCCESS] Distributed attribute for {reader_address} - Authority {authority_id}, Type {attr_type}")
            
        except Exception as e:
            print(f"[ERROR] Error distributing attribute for {reader_address}: {e}")
    
    # Commit changes
    reader_conn.commit()
    
    # Close connections
    certifier_conn.close()
    reader_conn.close()
    
    print(f"[SUCCESS] Successfully distributed {distributed_count} attributes to readers")
    return True

if __name__ == "__main__":
    if distribute_attributes():
        print("[SUCCESS] Attribute distribution completed successfully")
    else:
        print("[ERROR] Attribute distribution failed")
        sys.exit(1)
