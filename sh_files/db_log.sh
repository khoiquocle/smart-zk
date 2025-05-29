#!/bin/bash

echo "=== MARTZK Database Debug Log ==="
echo "Date: $(date)"
echo "Process Instance ID from .env: $(grep PROCESS_INSTANCE_ID ../src/.env)"
echo ""

# Function to show database contents with truncated large fields
show_database() {
    local db_path="$1"
    local db_name="$2"
    
    echo "=== $db_name Database ==="
    echo "Path: $db_path"
    
    if [ ! -f "$db_path" ]; then
        echo "❌ Database file does not exist!"
        echo ""
        return
    fi
    
    echo "📁 Tables in database:"
    sqlite3 "$db_path" ".tables"
    echo ""
    
    # Get all table names and show their contents
    tables=$(sqlite3 "$db_path" ".tables")
    for table in $tables; do
        echo "📋 Table: $table"
        echo "Schema:"
        sqlite3 "$db_path" ".schema $table"
        echo ""
        echo "Contents (truncated):"
        # Use SUBSTR to truncate long fields to first 50 characters
        sqlite3 "$db_path" "
        SELECT 
            CASE 
                WHEN LENGTH(column_data) > 50 
                THEN SUBSTR(column_data, 1, 50) || '...[TRUNCATED]'
                ELSE column_data 
            END as truncated_data
        FROM (
            SELECT GROUP_CONCAT(
                CASE 
                    WHEN LENGTH(CAST(* AS TEXT)) > 100 
                    THEN SUBSTR(CAST(* AS TEXT), 1, 50) || '...[LONG]'
                    ELSE CAST(* AS TEXT)
                END, '|'
            ) as column_data
            FROM $table
        );
        " 2>/dev/null || echo "Error reading table or no data"
        echo ""
        echo "Row count:"
        sqlite3 "$db_path" "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "Cannot count rows"
        echo ""
        echo "----------------------------------------"
    done
}

# Show key databases only
show_database "../databases/attribute_certifier/attribute_certifier.db" "ATTRIBUTE CERTIFIER"
show_database "../databases/reader_database/reader.db" "READER"

# Show just one authority database as example
show_database "../databases/authority1/authority1.db" "AUTHORITY 1 (SAMPLE)"

echo "=== zkSNARK Circuit Build Status ==="
echo "Circuit build time: $(stat -c %y ../zksnarks/build/attribute/proof_of_attribute.r1cs 2>/dev/null || echo 'Not found')"
echo ""

echo "=== Current zkSNARK Hash Function Test ==="
cd ../src
python3 -c "
from zksnark.utils import compute_pedersen_hash
test_values = [12345, 1234567890, 1, 0, 20251225]
result = compute_pedersen_hash(test_values)
print(f'Test hash result: {result}')
print(f'Type: {type(result)}')

# Test with MANUFACTURER string
manufacturer_hash = hash('MANUFACTURER') % (2**32)
print(f'MANUFACTURER hash: {manufacturer_hash}')
" 2>/dev/null || echo "Cannot test hash function"

echo ""
echo "=== Debug Log Complete ===" 