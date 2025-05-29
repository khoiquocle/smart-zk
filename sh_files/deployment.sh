#!/bin/bash

# MARTZK Deployment Script
# Deploys Verifier contracts and the main MARTZKEth contract,
# then updates the .env file with their addresses.

# Define the path to the .env file relative to the blockchain directory
ENV_FILE="../src/.env"

# Change directory to the blockchain folder
cd ../blockchain || exit 1 # Exit if cd fails

echo "Running Truffle migrations for MARTZK..."
# Run migrate, capture all output to a variable
# Assumes the migration script '2_deploy_verifiers.js' exists and logs addresses.
migration_output=$(truffle migrate --network development)

# Display migration output to the user
echo "---------------- Migration Output ----------------"
echo "$migration_output"
echo "--------------------------------------------------"

# Check if migration was successful (basic check for common error messages)
if echo "$migration_output" | grep -q -E 'Error:|Compiliation failed|Compilation failed'; then
    echo "Error: Truffle migration failed. Please check the output above." >&2
    exit 1
fi

# Extract contract addresses using grep and awk based on console logs from migration script
# These grep patterns assume the exact logging format from the guide's migration script.
martzketh_address=$(echo "$migration_output" | grep "MARTZKEth deployed to:" | awk '{print $NF}')
attribute_verifier_address=$(echo "$migration_output" | grep "AttributeVerifier deployed to:" | awk '{print $NF}')
policy_verifier_address=$(echo "$migration_output" | grep "PolicyVerifier deployed to:" | awk '{print $NF}')
process_verifier_address=$(echo "$migration_output" | grep "ProcessVerifier deployed to:" | awk '{print $NF}')

# Check if addresses were extracted successfully
if [ -z "$martzketh_address" ] || [ -z "$attribute_verifier_address" ] || [ -z "$policy_verifier_address" ] || [ -z "$process_verifier_address" ]; then
    echo "Error: Could not extract all required contract addresses from migration output." >&2
    echo "Please ensure the migration script logs addresses in the expected format:" >&2
    echo "  MARTZKEth deployed to: <address>" >&2
    echo "  AttributeVerifier deployed to: <address>" >&2
    echo "  PolicyVerifier deployed to: <address>" >&2
    echo "  ProcessVerifier deployed to: <address>" >&2
    exit 1
fi

echo "  Extracted Addresses:"
echo "  MARTZKEth Contract:         $martzketh_address"
echo "  Attribute Verifier Contract: $attribute_verifier_address"
echo "  Policy Verifier Contract:    $policy_verifier_address"
echo "  Process Verifier Contract:   $process_verifier_address"

# Update .env file
echo "Updating $ENV_FILE..."

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE" >&2
    exit 1
fi

# Use sed to replace or add the contract addresses in the .env file
# Create backup .env.bak
sed -i.bak \
    -e "s|^CONTRACT_ADDRESS_MARTZKETH=.*$|CONTRACT_ADDRESS_MARTZKETH=\"$martzketh_address\"|" \
    -e "s|^CONTRACT_ADDRESS_ATTRIBUTE_VERIFIER=.*$|CONTRACT_ADDRESS_ATTRIBUTE_VERIFIER=\"$attribute_verifier_address\"|" \
    -e "s|^CONTRACT_ADDRESS_POLICY_VERIFIER=.*$|CONTRACT_ADDRESS_POLICY_VERIFIER=\"$policy_verifier_address\"|" \
    -e "s|^CONTRACT_ADDRESS_PROCESS_VERIFIER=.*$|CONTRACT_ADDRESS_PROCESS_VERIFIER=\"$process_verifier_address\"|" \
    "$ENV_FILE"

# Check if the variables existed and were replaced. If not, append them.
grep -q "^CONTRACT_ADDRESS_MARTZKETH=" "$ENV_FILE" || echo "CONTRACT_ADDRESS_MARTZKETH=\"$martzketh_address\"" >> "$ENV_FILE"
grep -q "^CONTRACT_ADDRESS_ATTRIBUTE_VERIFIER=" "$ENV_FILE" || echo "CONTRACT_ADDRESS_ATTRIBUTE_VERIFIER=\"$attribute_verifier_address\"" >> "$ENV_FILE"
grep -q "^CONTRACT_ADDRESS_POLICY_VERIFIER=" "$ENV_FILE" || echo "CONTRACT_ADDRESS_POLICY_VERIFIER=\"$policy_verifier_address\"" >> "$ENV_FILE"
grep -q "^CONTRACT_ADDRESS_PROCESS_VERIFIER=" "$ENV_FILE" || echo "CONTRACT_ADDRESS_PROCESS_VERIFIER=\"$process_verifier_address\"" >> "$ENV_FILE"

# Optional: Remove the old MARTSIA address if it exists and is no longer needed
# sed -i.bak '/^CONTRACT_ADDRESS_MARTSIA=/d' "$ENV_FILE"

echo ".env file updated successfully with MARTZK contract addresses."
echo "Deployment script finished."

# Return to the original directory (optional)
# cd -
