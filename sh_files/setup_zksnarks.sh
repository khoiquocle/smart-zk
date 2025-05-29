#!/bin/bash

# Get the project root directory
PROJECT_ROOT="$(dirname "$(dirname "$(realpath "$0")")")"
echo "Compiling zkSNARK circuits..."
bash "$PROJECT_ROOT/zksnarks/scripts/compile_circuits.sh"
echo "Performing trusted setup..."
bash "$PROJECT_ROOT/zksnarks/scripts/setup.sh"
echo "zkSNARK setup complete."
