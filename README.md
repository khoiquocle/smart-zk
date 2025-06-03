# SMART-ZK: Enhancing Privacy Preserving and Security in Multi-Party Business Blockchain-Based Process

## Overview
SMART-ZK is a comprehensive zero-knowledge proof system implementation that enables secure, real-time verification of supply chain data. The system uses a multi-authority approach to ensure trust and transparency across the supply chain network.

### System Flow

1. **Initialization Phase**
   ```
   Manufacturer → Database Setup → IPFS Setup → Authority Registration
   ```

2. **Verification Phase**
   ```
   Product Data → Proof Generation → Multi-Authority Verification → Blockchain Recording
   ```

3. **Tracking Phase**
   ```
   Real-time Monitoring → Gas Cost Tracking → Performance Analytics → Report Generation
   ```

### Security Features

1. **Cryptographic Security**
   - Zero-knowledge proofs for data privacy
   - Multi-authority threshold signatures
   - Secure key distribution protocols

2. **Network Security**
   - Encrypted communication channels
   - Distributed authority validation
   - Anti-tampering mechanisms

3. **Data Security**
   - IPFS content addressing
   - Blockchain immutability
   - Secure database access controls


## Quick Start

### 1. Setup Environment
```bash
# Start IPFS daemon
ipfs daemon

# Setup database
sh sh_files/db_and_IPFS.sh
```

### 2. Setup attribute certification
```bash
# Setup certification 
sh certifications.sh --input ../json_files/roles.json
```
### 3. Setup authorities
```bash
bash authorities.sh
```
### 4. Distribute attributes
```python
python3 distribute_attributes.py
```
### 5. Encrypt data 
```bash
sh cipher.sh --sender_name LOGISTIC --input ../input_files/ --policies ../json_files/policies.json
```

### 6. Decrypt data
```bash
sh decipher.sh --message_id last_message_id --slice_id slice1 --requester_name MANUFACTURER --output_folder ../output_files/
```

## Features

### Gas Tracking
- Real-time gas cost monitoring
- Multi-step workflow tracking
- Detailed cost breakdowns
- JSON report generation

### Workflow Steps
1. Database and IPFS Setup
2. Sequential Authority Operations
3. Coordinated Setup
4. Enhanced Deciphering


### Optimization Strategies
1. **Gas Optimization**
   - Batch processing
   - Off-chain computation
   - Gas price monitoring

2. **Storage Optimization**
   - IPFS content deduplication
   - Database indexing
   - Cache management

3. **Network Optimization**
   - Connection pooling
   - Request batching
   - Load balancing


### Common Issues
1. **IPFS Connection Error**
   - Ensure IPFS daemon is running
   - Check IPFS API port (default: 5001)

2. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials

3. **Encoding Issues**
   - Use the latest version of the gas tracker
   - Ensure proper file permissions

## Contact
For support or questions, please open an issue in the repository.
