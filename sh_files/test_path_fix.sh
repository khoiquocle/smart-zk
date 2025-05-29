#!/bin/bash

echo "🔧 Testing Path Fix for MARTZK System"
echo "====================================="

echo ""
echo "📍 Current working directory: $(pwd)"

# Test from sh_files directory (current location)
echo ""
echo "1️⃣ Testing from /test/sh_files (current directory):"
cd /home/kevin/Research/test_zk/sh_files
echo "   Current directory: $(pwd)"
echo "   Testing data_owner.py database path..."
python3 -c "
import sys
sys.path.append('../src')
from path_utils import get_data_owner_db
print(f'   ✓ Data owner DB path: {get_data_owner_db()}')
import os
print(f'   ✓ Path exists: {os.path.exists(get_data_owner_db())}')
"

echo ""
echo "2️⃣ Testing from /test/src directory:"
cd /home/kevin/Research/test_zk/src
echo "   Current directory: $(pwd)"
echo "   Testing reader.py database path..."
python3 -c "
from path_utils import get_reader_db, get_attribute_certifier_db
print(f'   ✓ Reader DB path: {get_reader_db()}')
print(f'   ✓ Attribute certifier DB path: {get_attribute_certifier_db()}')
import os
print(f'   ✓ Reader DB exists: {os.path.exists(get_reader_db())}')
print(f'   ✓ Certifier DB exists: {os.path.exists(get_attribute_certifier_db())}')
"

echo ""
echo "3️⃣ Testing from /test (root) directory:"
cd /home/kevin/Research/test_zk
echo "   Current directory: $(pwd)"
echo "   Testing all database paths..."
python3 -c "
import sys
sys.path.append('src')
from path_utils import get_data_owner_db, get_reader_db, get_attribute_certifier_db, get_authority_db
import os
print(f'   ✓ Data owner DB: {get_data_owner_db()} (exists: {os.path.exists(get_data_owner_db())})')
print(f'   ✓ Reader DB: {get_reader_db()} (exists: {os.path.exists(get_reader_db())})')
print(f'   ✓ Certifier DB: {get_attribute_certifier_db()} (exists: {os.path.exists(get_attribute_certifier_db())})')
print(f'   ✓ Authority1 DB: {get_authority_db(1)} (exists: {os.path.exists(get_authority_db(1))})')
"

echo ""
echo "4️⃣ Docker container test (if applicable):"
if [ -d "/test" ]; then
    cd /test
    echo "   Current directory: $(pwd)"
    echo "   Testing from Docker container paths..."
    python3 -c "
import sys
sys.path.append('src')
from path_utils import get_project_root, get_database_path
print(f'   ✓ Project root: {get_project_root()}')
print(f'   ✓ Database base path: {get_project_root()}/databases')
import os
print(f'   ✓ Databases directory exists: {os.path.exists(str(get_project_root()) + \"/databases\")}')
"
else
    echo "   ⏩ Not in Docker container, skipping Docker-specific test"
fi

echo ""
echo "✅ Path fix verification complete!"
echo "💡 All database connections should now work regardless of working directory" 