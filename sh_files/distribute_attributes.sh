#!/bin/bash

# MARTZK Attribute Distribution Script
# This script distributes attribute secrets from the certifier to readers

echo "[INFO] MARTZK Attribute Distribution Process"
echo "========================================"

# Check if src directory exists
if [ ! -d "../src" ]; then
    echo "Error: ../src directory not found. Please run this script from the sh_files directory." >&2
    exit 1
fi

# Check if the attribute distribution script exists
if [ ! -f "../src/distribute_attributes.py" ]; then
    echo "Error: ../src/distribute_attributes.py not found. Creating it now..."
    
    # Create the distribution script
    cat > "../src/distribute_attributes.py" << 'EOF'
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
    
    print(f"📋 Distributing attributes for process instance: {process_instance_id}")
    
    # Connect to certifier database
    certifier_db_path = get_attribute_certifier_db()
    if not os.path.exists(certifier_db_path):
        print(f"❌ Error: Certifier database not found at {certifier_db_path}")
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
        print(f"❌ No attributes found for process instance {process_instance_id}")
        return False
    
    print(f"📊 Found {len(attributes)} attribute records to distribute")
    
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
            print(f"✅ Distributed attribute for {reader_address} - Authority {authority_id}, Type {attr_type}")
            
        except Exception as e:
            print(f"❌ Error distributing attribute for {reader_address}: {e}")
    
    # Commit changes
    reader_conn.commit()
    
    # Close connections
    certifier_conn.close()
    reader_conn.close()
    
    print(f"🎉 Successfully distributed {distributed_count} attributes to readers")
    return True

if __name__ == "__main__":
    if distribute_attributes():
        print("✅ Attribute distribution completed successfully")
    else:
        print("❌ Attribute distribution failed")
        sys.exit(1)
EOF

    echo "✅ Created distribute_attributes.py"
fi

echo "[INFO] Running attribute distribution..."
python3 ../src/distribute_attributes.py

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Attribute distribution completed successfully"
else
    echo "[ERROR] Attribute distribution failed"
    exit 1
fi 