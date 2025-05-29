#!/bin/bash
set -e

# Lấy đường dẫn thư mục gốc của project
PROJECT_ROOT="/test"
CIRCOM_DIR="$PROJECT_ROOT/zksnarks/circuits"
BUILD_DIR="$PROJECT_ROOT/zksnarks/build"

# Tạo thư mục output nếu chưa có
mkdir -p "$BUILD_DIR/attribute" "$BUILD_DIR/policy" "$BUILD_DIR/process"

# Compile ProofOfAttribute
echo "Compiling ProofOfAttribute..."
circom "$CIRCOM_DIR/proof_of_attribute.circom" --r1cs --wasm --sym -o "$BUILD_DIR/attribute"

# Compile ProofOfPolicy
echo "Compiling ProofOfPolicy..."
circom "$CIRCOM_DIR/proof_of_policy.circom" --r1cs --wasm --sym -o "$BUILD_DIR/policy"

# Compile ProofOfProcessCompliance
echo "Compiling ProofOfProcessCompliance..."
circom "$CIRCOM_DIR/proof_of_process.circom" --r1cs --wasm --sym -o "$BUILD_DIR/process"

echo "✅ Circuit compilation complete."
