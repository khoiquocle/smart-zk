#!/bin/sh

# MARTZK Certifications Script
# This script handles the initial setup for readers and runs the
# enhanced attribute certification process which includes generating
# zkSNARK commitments.

# Initialize variables
input=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --input|-i)
      input="$2"
      shift # Move to next argument
      shift # Move to next value
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Check if input file argument is provided
if [ -z "$input" ]; then
  echo "Usage: $0 --input <input_roles_file.json> or $0 -i <input_roles_file.json>"
  exit 1
fi

# Check if input file exists
if [ ! -f "$input" ]; then
  echo "Input file 	'$input	' does not exist"
  exit 1
fi

# Check if src directory exists relative to sh_files
if [ ! -d "../src" ]; then
    echo "Error: ../src directory not found. Please run this script from the sh_files directory." >&2
    exit 1
fi

# Check if .env file exists
if [ ! -f "../src/.env" ]; then
    echo "Error: ../src/.env file not found." >&2
    exit 1
fi

# Get reader names (e.g., READER1, READER2) from .env file
# Assumes format like READER1_ADDRESS=...
reader_lines=$(grep '^[^#]*_ADDRESS=' ../src/.env | grep -v "AUTHORITY\|CONTRACT\|SERVER\|CERTIFIER\|TEST_SENDER" | awk -F"_ADDRESS=" '{print $1}')

if [ -z "$reader_lines" ]; then
    echo "Warning: No reader addresses found in ../src/.env (e.g., READER1_ADDRESS=...)"
fi

echo "Processing reader public keys (if applicable for MA-ABE setup)..."
echo "$reader_lines" | while IFS= read -r reader; do
    if [ -z "$reader" ]; then continue; fi
    echo "Processing reader: $reader"
    # Run the reader public key script (assuming it's still needed for MA-ABE)
    if [ -f "../src/reader_public_key.py" ]; then
        python3 ../src/reader_public_key.py --reader "$reader"
        echo "✅ Processed public key setup for $reader"
    else
        echo "Warning: ../src/reader_public_key.py not found. Skipping public key setup for $reader."
    fi
done

echo "Running MARTZK attribute certification process..."
# Run the enhanced attribute certifier script with the input roles file.
# This Python script now handles zkSNARK commitment generation and storage.
if [ -f "../src/attribute_certifier.py" ]; then
    python3 ../src/attribute_certifier.py -i "$input"
    echo "✅ MARTZK Attribute certification process completed."
else
    echo "Error: ../src/attribute_certifier.py not found." >&2
    exit 1
fi
