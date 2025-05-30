#!/usr/bin/env python3
"""
Demo: Enhanced Gas Tracking for MARTZK System
Shows step-by-step gas fee tracking capabilities
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_gas_tracker import MARTZKGasTracker
except ImportError:
    print("Error: enhanced_gas_tracker.py not found")
    print("Please ensure both files are in the same directory")
    sys.exit(1)

def main():
    """Run enhanced gas tracking demonstration"""
    print("=" * 60)
    print("MARTZK ENHANCED GAS TRACKING DEMONSTRATION")
    print("=" * 60)
    
    # Initialize gas tracker with current market rates
    tracker = MARTZKGasTracker(gas_price_gwei=25, eth_price_usd=2500)
    
    print("\n[INFO] Tracking gas costs for complete MARTZK workflows...")
    print("       Gas Price: 25 Gwei | ETH Price: $2,500")
    
    # Demonstrate different workflows
    print("\n1. ENCRYPTION WORKFLOW")
    print("-" * 30)
    encryption_total = tracker.track_encryption_workflow("msg_demo_001", slice_count=4)
    print(f"   Total Encryption Cost: {encryption_total['total_gas']:,} gas (${encryption_total['total_usd']:.2f})")
    
    print("\n2. DECRYPTION WORKFLOW")
    print("-" * 30)
    decryption_total = tracker.track_decryption_workflow("msg_demo_001", "MANUFACTURER", authority_count=3)
    print(f"   Total Decryption Cost: {decryption_total['total_gas']:,} gas (${decryption_total['total_usd']:.2f})")
    
    print("\n3. CERTIFICATION WORKFLOW")
    print("-" * 35)
    certification_total = tracker.track_certification_workflow("proc_demo_001", attribute_count=8)
    print(f"   Total Certification Cost: {certification_total['total_gas']:,} gas (${certification_total['total_usd']:.2f})")
    
    print("\n4. AUTHORITY OPERATIONS")
    print("-" * 30)
    authority_total = tracker.track_authority_operations("auth_demo_001", key_generations=5)
    print(f"   Total Authority Cost: {authority_total['total_gas']:,} gas (${authority_total['total_usd']:.2f})")
    
    # Show comprehensive report
    print("\n" + "=" * 60)
    print("COMPREHENSIVE GAS ANALYSIS")
    print("=" * 60)
    tracker.print_summary()
    
    # Save detailed report
    tracker.save_detailed_report("demo_gas_report.json")
    
    print("\n" + "=" * 60)
    print("STEP-BY-STEP BREAKDOWN EXAMPLES")
    print("=" * 60)
    
    # Show step breakdown for encryption
    enc_breakdown = tracker.get_step_breakdown("encryption_msg_demo_001")
    print("\nEncryption Step Breakdown:")
    for step, data in enc_breakdown.items():
        print(f"  {step}: {data['total_gas']:,} gas (${data['total_usd']:.2f})")
    
    # Show step breakdown for decryption
    dec_breakdown = tracker.get_step_breakdown("decryption_msg_demo_001_MANUFACTURER")
    print("\nDecryption Step Breakdown:")
    for step, data in dec_breakdown.items():
        print(f"  {step}: {data['total_gas']:,} gas (${data['total_usd']:.2f})")
    
    print("\n" + "=" * 60)
    print("COST OPTIMIZATION INSIGHTS")
    print("=" * 60)
    
    # Calculate total system cost
    report = tracker.get_comprehensive_report()
    total_usd = report['summary']['total_usd_cost']
    total_gas = report['summary']['total_gas_used']
    
    print(f"\nTotal Gas Usage: {total_gas:,} gas")
    print(f"Total Cost: ${total_usd:.2f}")
    print(f"Average Cost per Transaction: ${total_usd/report['summary']['total_transactions']:.2f}")
    
    # Most expensive operations
    print(f"\nMost Expensive Steps:")
    for i, step in enumerate(report['most_expensive_steps'][:3], 1):
        print(f"  {i}. {step['step']}: ${step['total_usd_cost']:.2f}")
    
    print(f"\n[SUCCESS] Gas tracking demonstration completed!")
    print(f"[INFO] Detailed report saved to: demo_gas_report.json")

if __name__ == "__main__":
    main() 