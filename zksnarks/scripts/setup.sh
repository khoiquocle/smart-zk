#!/bin/bash
set -e  # Dừng nếu có lỗi

# Đường dẫn thư mục gốc của project
PROJECT_ROOT="/test"
BUILD_DIR="$PROJECT_ROOT/zksnarks/build"
VERIFIER_DIR="$PROJECT_ROOT/blockchain/contracts/verifiers"

# Tạo thư mục cần thiết
mkdir -p "$VERIFIER_DIR"

# === Phase 1: Powers of Tau Ceremony ===
echo "⚙️ Starting Powers of Tau ceremony..."
snarkjs powersoftau new bn128 12 "$BUILD_DIR/pot12_0000.ptau" -v
snarkjs powersoftau contribute "$BUILD_DIR/pot12_0000.ptau" "$BUILD_DIR/pot12_0001.ptau" --name="First contribution" -v -e="random entropy"
snarkjs powersoftau prepare phase2 "$BUILD_DIR/pot12_0001.ptau" "$BUILD_DIR/pot12_final.ptau" -v

# === Phase 2: Setup for each circuit ===
for CIRCUIT in attribute policy process; do
    CIRCUIT_NAME="proof_of_$CIRCUIT"
    CIRCUIT_BUILD_DIR="$BUILD_DIR/$CIRCUIT"

    echo "🔧 Setting up $CIRCUIT_NAME..."
    snarkjs groth16 setup "$CIRCUIT_BUILD_DIR/$CIRCUIT_NAME.r1cs" "$BUILD_DIR/pot12_final.ptau" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey"
    snarkjs zkey contribute "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0000.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" --name="First circuit contribution" -v -e="random entropy for $CIRCUIT"
    snarkjs zkey export verificationkey "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_verification_key.json"
    snarkjs zkey export solidityverifier "$CIRCUIT_BUILD_DIR/${CIRCUIT_NAME}_0001.zkey" "$VERIFIER_DIR/Verifier_${CIRCUIT_NAME}.sol"
done

echo "✅ zkSNARK trusted setup complete."
