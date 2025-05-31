# SMART-ZK: Enhancing Privacy Preserving and Security in Multi-Party Business Blockchain-Based Process

## Overview
SMART-ZK is a comprehensive zero-knowledge proof system implementation that enables secure, real-time verification of supply chain data. The system uses a multi-authority approach to ensure trust and transparency across the supply chain network.

## System Architecture

### Core Components

#### 1. Multi-Authority System
- **Manufacturer Authority**: Initiates product verification
- **Logistics Authority**: Handles shipping and delivery verification
- **Retailer Authority**: Manages final product verification
- **Coordinated Setup**: Ensures secure key distribution among authorities

#### 2. Zero-Knowledge Proof System
- **Proof Generation**: Creates cryptographic proofs for supply chain events
- **Proof Verification**: Validates proofs without revealing sensitive data
- **Real-time Verification**: Instant proof validation for supply chain operations

#### 3. Blockchain Integration
- **Smart Contracts**: Manages authority interactions and proof verification
- **Gas Optimization**: Efficient transaction handling and cost management
- **Event Logging**: Secure recording of supply chain events

#### 4. Data Storage
- **IPFS Integration**: Decentralized storage for large data objects
- **PostgreSQL Database**: Structured data storage and querying
- **Hybrid Storage**: Combines on-chain and off-chain storage solutions

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

## Technical Specifications

### System Requirements
- **Hardware**
  - CPU: 4+ cores recommended
  - RAM: 8GB minimum
  - Storage: 50GB+ for full node

- **Software**
  - Python 3.x
  - IPFS daemon
  - SQLite
  - Web3.py
  - Node.js (for IPFS)

### Network Configuration
- **IPFS**
  - API Port: 5001
  - Gateway Port: 8080
  - Swarm Port: 4001

- **Database**
  - Port: 5432
  - User Authentication
  - SSL Support

- **Blockchain**
  - Ethereum Network
  - Gas Price Monitoring
  - Transaction Pool Management

## Prerequisites
- Python 3.x
- IPFS daemon
- SQLite database
- Required Python packages (install via pip):
  ```bash
  pip install web3 requests
  ```

## Quick Start

### 1. Setup Environment
```bash
# Start IPFS daemon
ipfs daemon

# Setup database
sh sh_files/db_and_IPFS.sh
```

### 2. Run Gas Tracking
```bash
# Basic gas tracking
python3 src/simple_gas_tracker.py --gas-price 30 --eth-price 2500 --sender MANUFACTURER --requester LOGISTIC

# Enhanced benchmarking
python3 src/benchmark_martzk_enhanced.py --help
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

## Configuration

### Gas Tracker Options
- `--gas-price`: Gas price in Gwei (default: 20)
- `--eth-price`: ETH price in USD (default: 2000)
- `--sender`: Sender role (default: MANUFACTURER)
- `--requester`: Requester role (default: MANUFACTURER)

## Output
The system generates detailed reports including:
- Step-by-step execution logs
- Gas costs per operation
- Total workflow costs
- Success/failure status
- JSON reports for analysis

## Performance Considerations

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

## Troubleshooting

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
