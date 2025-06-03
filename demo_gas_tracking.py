#!/usr/bin/env python3
"""
MARTZK Gas Tracking Demonstration
Shows how to use the step-by-step gas tracking system
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

def demo_gas_tracking():
    """Demonstrate the gas tracking functionality"""
    print("MARTZK Gas Tracking Demonstration")
    print("=" * 50)
    
    gas_price_gwei = 25  # Higher gas price for demo
    eth_price_usd = 2500  # Current ETH price
    
    print(f"Gas Price: {gas_price_gwei} Gwei")
    print(f"ETH Price: ${eth_price_usd}")
    
    print("\n📋 Available Commands:")
    print("1. Run simple gas tracker:")
    print("   python3 src/simple_gas_tracker.py --gas-price 25 --eth-price 2500")
    
    print("\n2. Run individual components with gas tracking:")
    print("   python3 src/authority.py -a 1")
    print("   python3 src/attribute_certifier.py -i json_files/roles.json")
    print("   python3 src/data_owner.py -s MANUFACTURER -i input_files/ -p json_files/policies.json")
    
    print("\n3. Run with different workflows:")
    print("   python3 src/simple_gas_tracker.py --workflow setup")
    print("   python3 src/simple_gas_tracker.py --workflow certify")  
    print("   python3 src/simple_gas_tracker.py --workflow encrypt")
    
    print("\n📊 Expected Gas Costs (at 25 Gwei, ETH = $2500):")
    print("   Authority Setup:")
    print("     - Authority Names Registration:    ~75,000 gas (~$4.69)")
    print("     - Initial Parameters Storage:      ~95,000 gas (~$5.94)")
    print("     - Public Key Registration:         ~72,000 gas (~$4.50)")
    
    print("   Attribute Certification:")
    print("     - Per Attribute Commitment:        ~86,000 gas (~$5.38)")
    
    print("   Data Operations:")
    print("     - Message IPFS Link Storage:       ~66,000 gas (~$4.13)")
    print("     - zkSNARK Proof Verification:    ~250,000 gas (~$15.63)")
    
    print("\n🔧 Environment Configuration:")
    print("   Add to src/.env:")
    print("   GAS_PRICE_GWEI=25")
    print("   ETH_PRICE_USD=2500")
    
    print("\n📈 Gas Reports:")
    print("   Reports are automatically saved as JSON files:")
    print("   gas_report_full_YYYYMMDD_HHMMSS.json")
    
    print("\n🎯 Quick Start:")
    print("   1. Ensure your blockchain (Ganache) is running")
    print("   2. Set up your .env file with addresses and keys")
    print("   3. Run: python3 src/simple_gas_tracker.py")
    print("   4. Watch the real-time gas costs!")
    
    print("\n🚀 Ready to track gas costs!")
    print("Run any MARTZK operation to see step-by-step gas tracking in action.")

if __name__ == "__main__":
    demo_gas_tracking() 