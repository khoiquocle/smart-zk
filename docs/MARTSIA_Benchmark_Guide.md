# MARTSIA-Compliant MARTZK Benchmark Implementation Guide

## Overview

This guide provides comprehensive consultation on implementing MARTSIA-compliant benchmarks for the MARTZK system. The benchmarks are designed to measure Performance (Time Complexity), Cost (Computational & Blockchain), and Scalability metrics as specified in MARTSIA literature.

## Architecture Overview

### Current vs Enhanced Implementation

**Current Benchmark (`src/benchmark_martzk.py`)**:
- Basic encryption/decryption timing
- High-level resource monitoring
- Multi-user access control testing
- File size impact analysis

**Enhanced MARTSIA Benchmark (`src/benchmark_martzk_enhanced.py`)**:
- Component-level MA-ABE and zkSNARK profiling
- Blockchain gas cost measurement
- Size metrics (proofs, keys, ciphertext)
- Comprehensive scalability testing
- End-to-end latency analysis

## Implementation Strategy

### 1. Performance Metrics (A)

#### MA-ABE Operations
```python
# Example usage for MA-ABE benchmarks
benchmark = MARTSIABenchmark(iterations=50)

# Setup benchmarks with varying parameters
setup_results = benchmark.benchmark_maabe_setup(num_authorities=3, num_attributes=10)

# KeyGen benchmarks for different user types
keygen_results = benchmark.benchmark_maabe_keygen(user_type='MANUFACTURER', num_attributes=5)

# Encryption benchmarks with policy complexity variations
encrypt_results = benchmark.benchmark_maabe_encrypt(message_size='1KB', policy_complexity='medium')

# Decryption benchmarks with attribute satisfaction analysis
decrypt_results = benchmark.benchmark_maabe_decrypt(num_satisfying_attrs=3)
```

**Key Metrics Captured**:
- `Setup_MAABE`: Time for global setup and authority initialization
- `KeyGen_MAABE`: Time to generate user secret keys based on attributes
- `Encrypt_MAABE`: Time to encrypt data under an access policy
- `Decrypt_MAABE`: Time to decrypt data with satisfying attributes

#### zkSNARK Operations
```python
# zkSNARK benchmarks for each circuit type
circuits = ['attribute', 'policy', 'process']

for circuit in circuits:
    setup_result = benchmark.benchmark_zksnark_setup(circuit_type=circuit)
    witness_result = benchmark.benchmark_zksnark_witness_gen(circuit_type=circuit, input_size='small')
    proof_result = benchmark.benchmark_zksnark_proof_gen(circuit_type=circuit)
    verify_offchain = benchmark.benchmark_zksnark_verify_offchain(circuit_type=circuit)
    verify_onchain = benchmark.benchmark_zksnark_verify_onchain(circuit_type=circuit)
```

**Key Metrics Captured**:
- `Setup_ZKP`: Time for trusted setup (Powers of Tau and circuit-specific setup)
- `WitnessGen_ZKP`: Time to generate witness for each circuit type
- `ProofGen_ZKP`: Time to generate zkSNARK proof
- `Verify_ZKP_OffChain`: Time to verify proof off-chain
- `Verify_ZKP_OnChain`: Time for on-chain verification transaction

#### End-to-End Latency
```python
# Comprehensive end-to-end latency measurement
e2e_results = benchmark.benchmark_end_to_end_latency(user_type='MANUFACTURER')

# Includes:
# - Latency_KeyRequest: Time from proof generation to partial key receipt
# - Latency_Decryption: Total time from decryption request to plaintext
```

### 2. Cost Metrics (B)

#### Size Measurements
The enhanced benchmark automatically extracts size metrics from operation outputs:
```python
def extract_size_metrics(self, operation_result):
    """Extract size metrics from operation results"""
    size_metrics = {}
    
    # Pattern matching for different size types
    proof_size_pattern = r'Proof size: ([\d.]+) bytes'
    key_size_pattern = r'Key size: ([\d.]+) bytes'
    ciphertext_size_pattern = r'Ciphertext size: ([\d.]+) bytes'
```

**Key Metrics Captured**:
- `Size_Proof_ZKP`: Size of zkSNARK proofs in bytes
- `Size_Keys_MAABE`: Size of public parameters, master keys, and user secret keys
- `Size_Ciphertext_MAABE`: Size of MA-ABE ciphertext with overhead analysis

#### Blockchain Gas Costs
```python
# Comprehensive blockchain cost analysis
blockchain_costs = benchmark.benchmark_blockchain_costs()

# Includes:
# - Gas_Deploy: Contract deployment costs
# - Gas_SetAttrCommit: setUserAttributes operation costs
# - Gas_VerifyOnChain: Various on-chain verification costs

# Convert to USD for practical analysis
usd_costs = benchmark.calculate_gas_costs_usd(gas_costs)
```

**Key Metrics Captured**:
- `Gas_Deploy`: Contract deployment gas costs
- `Gas_SetAttrCommit`: Attribute commitment storage costs
- `Gas_VerifyOnChain`: On-chain verification function costs
- USD equivalent costs for economic analysis

### 3. Scalability Metrics (C)

#### Authority Scalability
```python
# Test with varying number of authorities
authority_results = benchmark.benchmark_authority_scalability()
# Tests: 1, 2, 3, 4, 5 authorities
# Measures: Setup time, KeyGen time, Encryption time
```

#### User Scalability
```python
# Test with varying user loads
user_results = benchmark.benchmark_user_scalability()
# Tests: 10, 50, 100, 200, 500 concurrent users
# Measures: System response time under load
```

#### Attribute Scalability
```python
# Test with varying attribute counts
attribute_results = benchmark.benchmark_attribute_scalability()
# Tests: 5, 10, 15, 20, 25 attributes
# Measures: Setup time, KeyGen time impact
```

#### Policy Complexity Scalability
```python
# Test with varying policy complexity
policy_results = benchmark.benchmark_policy_complexity_scalability()
# Tests: simple, medium, complex policies
# Measures: Encryption/Decryption time impact
```

## Integration with Existing System

### 1. Database Integration
The benchmark system integrates with existing MARTZK databases:
```python
# Uses existing path utilities
from src.path_utils import get_data_owner_db, get_reader_db, get_attribute_certifier_db

# Accesses real system data for realistic benchmarks
def access_system_state(self):
    reader_db = get_reader_db()
    # Extract actual attribute data, policy information, etc.
```

### 2. Component Integration
The component benchmark (`src/benchmark_components.py`) provides granular operation measurement:
```bash
# Individual operation benchmarks
python3 src/benchmark_components.py --operation maabe_setup --authorities 3 --attributes 10
python3 src/benchmark_components.py --operation zksnark_proof --circuit_type attribute
python3 src/benchmark_components.py --operation blockchain_verify_attr_proof
```

### 3. Real vs Simulated Operations
The current implementation uses simulation for operations not yet implemented:
- **Real Operations**: Database access, file I/O, system resource monitoring
- **Simulated Operations**: zkSNARK circuit operations, blockchain transactions
- **Future Enhancement**: Replace simulations with actual implementations as system matures

## Usage Examples

### Quick Benchmark
```bash
# Run quick benchmark (5 iterations)
python3 src/benchmark_martzk_enhanced.py --quick

# Run specific benchmark types
python3 src/benchmark_martzk_enhanced.py --performance-only
python3 src/benchmark_martzk_enhanced.py --scalability-only
```

### Comprehensive Analysis
```bash
# Full MARTSIA-compliant benchmark (50 iterations)
python3 src/benchmark_martzk_enhanced.py -i 50

# Results saved to:
# - martsia_benchmark_results/martsia_benchmark_TIMESTAMP.json
# - martsia_benchmark_results/martsia_summary_TIMESTAMP.json
# - martsia_benchmark_charts/ (visualization files)
```

### Component-Level Testing
```bash
# Test specific MA-ABE operations
python3 src/benchmark_components.py --operation maabe_encrypt --message_size 10KB --policy complex

# Test zkSNARK operations
python3 src/benchmark_components.py --operation zksnark_witness --circuit_type policy --input_size large

# Test scalability
python3 src/benchmark_components.py --operation scalability_users --user_count 500
```

## Expected Output Metrics

### Performance Report
```
MARTSIA COMPREHENSIVE BENCHMARK ANALYSIS
========================================

A. PERFORMANCE METRICS ANALYSIS
-------------------------------

   MA-ABE Operations:
      Setup: 0.157s ± 0.023s
      Keygen: 0.045s ± 0.008s
      Encrypt: 0.078s ± 0.012s
      Decrypt: 0.054s ± 0.009s

   zkSNARK Operations:
      Attribute Circuit:
         Setup: 0.702s ± 0.045s
         Witness: 0.052s ± 0.007s
         Proof: 0.301s ± 0.028s
         Verify Offchain: 0.011s ± 0.002s
         Verify Onchain: 0.152s ± 0.034s
```

### Cost Analysis
```
B. COST METRICS ANALYSIS
------------------------

   Size Metrics:
      zkSNARK Proof Size: 256 bytes
      MA-ABE Key Size: 576 bytes (5 attributes)
      Ciphertext Overhead: 39.1% (medium policy)

   Blockchain Gas Costs:
      Contract Deployment: 2,456,789 gas ($98.27)
      Set Attribute Commitment: 67,432 gas ($2.70)
      Verify Attribute Proof: 234,567 gas ($9.38)
```

### Scalability Analysis
```
C. SCALABILITY METRICS ANALYSIS
-------------------------------

   Authority Scalability:
      1 authorities: Setup 0.128s
      3 authorities: Setup 0.157s
      5 authorities: Setup 0.207s

   User Scalability:
      100 users: 0.101s
      500 users: 0.487s
```

## Visualization Outputs

The benchmark generates comprehensive charts:
1. **MA-ABE Performance Distribution** (`maabe_performance.png`)
2. **zkSNARK Performance by Circuit** (`zksnark_performance.png`)
3. **Scalability Analysis** (`scalability_analysis.png`)
4. **Cost Analysis Charts** (various cost-related visualizations)

## Integration Requirements

### Dependencies
Add to `requirements.txt`:
```
matplotlib>=3.5.0
seaborn>=0.11.0
numpy>=1.21.0
psutil>=5.8.0
tqdm>=4.62.0
```

### Database Schema Extensions (Optional)
For persistent benchmark storage:
```sql
CREATE TABLE benchmark_results (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    operation_type TEXT,
    duration_seconds REAL,
    memory_mb REAL,
    success BOOLEAN,
    metadata TEXT
);
```

## Future Enhancements

1. **Real zkSNARK Integration**: Replace simulations with actual zkSNARK library calls
2. **Blockchain Integration**: Connect to real Ethereum testnet for gas cost measurement
3. **Distributed Testing**: Multi-node deployment for realistic scalability testing
4. **Continuous Benchmarking**: Integration with CI/CD for performance regression detection
5. **Comparative Analysis**: Benchmarking against other MA-ABE and zkSNARK systems

## Best Practices

1. **Statistical Significance**: Run sufficient iterations (≥30) for meaningful statistics
2. **Environment Consistency**: Use isolated testing environment to minimize variance
3. **Resource Monitoring**: Monitor system resources during benchmarks to identify bottlenecks
4. **Data Persistence**: Save detailed results for trend analysis and comparison
5. **Documentation**: Document test conditions, hardware specifications, and configurations

This MARTSIA-compliant benchmark framework provides the foundation for comprehensive evaluation of the MARTZK system according to academic standards and industry best practices. 