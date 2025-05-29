"""
Path utilities for MARTZK system to resolve database paths consistently
regardless of current working directory
"""
import os
from pathlib import Path

def get_project_root():
    """Get the absolute path to the project root directory (/test)"""
    current_file = Path(__file__).resolve()
    # Go up from src/ to get to /test
    return current_file.parent.parent

def get_database_path(db_type, db_name=None):
    """
    Get absolute path to database files
    
    Args:
        db_type: Type of database ('attribute_certifier', 'data_owner', 'reader', 'authority1', etc.)
        db_name: Optional specific database filename (if None, uses default naming)
    
    Returns:
        str: Absolute path to database file
    """
    project_root = get_project_root()
    
    if db_name is None:
        # Use default naming convention
        if db_type.startswith('authority'):
            db_name = f"{db_type}.db"
        else:
            db_name = f"{db_type}.db"
    
    return str(project_root / "databases" / db_type / db_name)

def get_keys_path():
    """Get absolute path to Keys directory"""
    return str(get_project_root() / "Keys")

def get_input_files_path():
    """Get absolute path to input_files directory"""  
    return str(get_project_root() / "input_files")

def get_output_files_path():
    """Get absolute path to output_files directory"""
    return str(get_project_root() / "output_files")

# Common database paths
def get_attribute_certifier_db():
    """Get path to attribute_certifier database"""
    return get_database_path("attribute_certifier", "attribute_certifier.db")

def get_data_owner_db():
    """Get path to data_owner database"""
    return get_database_path("data_owner", "data_owner.db")

def get_reader_db():
    """Get path to reader database"""
    return get_database_path("reader", "reader.db")

def get_authority_db(authority_num):
    """Get path to specific authority database"""
    return get_database_path(f"authority{authority_num}", f"authority{authority_num}.db") 