#!/usr/bin/env python3
"""
MARTZK System Enhanced Performance Benchmark
MARTSIA-Compliant Comprehensive Evaluation
Measures MA-ABE Operations, zkSNARK Operations, Blockchain Costs, and Scalability
"""

import os
import sys
import time
import json
import psutil
import statistics
import subprocess
import re
import sqlite3
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import numpy as np

# Import the enhanced gas tracker
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from enhanced_gas_tracker import MARTZKGasTracker
except ImportError:
    print("[WARNING] Enhanced gas tracker not available. Using basic gas tracking.")
    MARTZKGasTracker = None

class MARTSIABenchmark:
    def __init__(self, iterations=100, enable_enhanced_gas_tracking=True):
        self.iterations = iterations
        self.results = defaultdict(list)
        self.charts_dir = "martsia_benchmark_charts"
        self.results_dir = "martsia_benchmark_results"
        os.makedirs(self.charts_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Blockchain Configuration
        self.blockchain_config = {
            'gas_price_gwei': 20,
            'eth_price_usd': 2000,  # For cost calculation
        }
        
        # Enhanced gas tracking
        self.enable_enhanced_gas_tracking = enable_enhanced_gas_tracking and MARTZKGasTracker is not None
        if self.enable_enhanced_gas_tracking:
            self.gas_tracker = MARTZKGasTracker(
                gas_price_gwei=self.blockchain_config.get('gas_price_gwei', 20),
                eth_price_usd=self.blockchain_config.get('eth_price_usd', 2000)
            )
            print("[INFO] Enhanced step-by-step gas tracking enabled")
        else:
            self.gas_tracker = None
            print("[INFO] Using basic gas tracking")
        
        # MARTSIA Test Parameters
        self.users = ['MANUFACTURER', 'LOGISTIC', 'CUSTOMS', 'SUPPLIER', 'RETAILER']
        self.authorities = [1, 2, 3, 4, 5]  # Scalability test
        self.attribute_counts = [5, 10, 15, 20, 25]  # Scalability test
        self.policy_complexities = ['simple', 'medium', 'complex']  # Policy complexity levels
        
        # Setup plotting with fallback for older matplotlib versions
        self._setup_plotting()
        self.colors = plt.cm.Set3(np.linspace(0, 1, 12))
    
    def _setup_plotting(self):
        """Setup matplotlib plotting with version compatibility"""
        styles_to_try = [
            'seaborn-v0_8',      # Modern seaborn style
            'seaborn',           # Older seaborn style
            'seaborn-whitegrid', # Even older seaborn style
            'ggplot',            # Alternative nice style
            'default'            # Fallback
        ]
        
        for style in styles_to_try:
            try:
                plt.style.use(style)
                print(f"Using matplotlib style: {style}")
                return
            except OSError:
                continue
        
        # If all else fails, just use matplotlib defaults
        print("Warning: Could not find any preferred styles, using matplotlib defaults")
        
        # Print available styles for debugging
        try:
            available_styles = plt.style.available
            print(f"Available matplotlib styles: {available_styles[:5]}...")  # Show first 5
        except Exception:
            print("Could not retrieve available matplotlib styles")
    
    def run_command_with_profiling(self, command, operation_type="general"):
        """Enhanced command execution with detailed profiling"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        cpu_start = psutil.cpu_percent(interval=None)
        
        # Detailed profiling for different operation types
        profiling_data = {
            'operation_type': operation_type,
            'start_time': start_time,
            'stdout': '',
            'stderr': '',
            'success': False,
            'detailed_timing': {}
        }
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            profiling_data['stdout'] = stdout
            profiling_data['stderr'] = stderr
            profiling_data['success'] = process.returncode == 0
            
            # Extract timing information from output if available
            profiling_data['detailed_timing'] = self.extract_timing_from_output(stdout, stderr, operation_type)
            
        except Exception as e:
            profiling_data['error'] = str(e)
            
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        cpu_end = psutil.cpu_percent(interval=None)
        
        profiling_data.update({
            'total_time': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'cpu_usage': cpu_end - cpu_start,
            'peak_memory': max(start_memory, end_memory)
        })
        
        return profiling_data
    
    def extract_timing_from_output(self, stdout, stderr, operation_type):
        """Extract detailed timing information from command output"""
        timing_data = {}
        
        # MA-ABE timing patterns
        maabe_patterns = {
            'setup_time': r'MA-ABE Setup completed in ([\d.]+)s',
            'keygen_time': r'KeyGen completed in ([\d.]+)s',
            'encrypt_time': r'Encryption completed in ([\d.]+)s',
            'decrypt_time': r'Decryption completed in ([\d.]+)s'
        }
        
        # zkSNARK timing patterns
        zksnark_patterns = {
            'setup_zkp_time': r'zkSNARK Setup completed in ([\d.]+)s',
            'witness_gen_time': r'Witness generation completed in ([\d.]+)s',
            'proof_gen_time': r'Proof generation completed in ([\d.]+)s',
            'verify_offchain_time': r'Off-chain verification completed in ([\d.]+)s',
            'verify_onchain_time': r'On-chain verification completed in ([\d.]+)s'
        }
        
        # Combine all patterns
        all_patterns = {**maabe_patterns, **zksnark_patterns}
        
        combined_output = stdout + stderr
        for key, pattern in all_patterns.items():
            match = re.search(pattern, combined_output)
            if match:
                timing_data[key] = float(match.group(1))
        
        return timing_data
    
    def extract_size_metrics(self, operation_result):
        """Extract size metrics from operation results"""
        size_metrics = {}
        
        # Extract proof sizes
        proof_size_pattern = r'Proof size: ([\d.]+) bytes'
        match = re.search(proof_size_pattern, operation_result.get('stdout', ''))
        if match:
            size_metrics['proof_size'] = float(match.group(1))
        
        # Extract key sizes
        key_size_pattern = r'Key size: ([\d.]+) bytes'
        match = re.search(key_size_pattern, operation_result.get('stdout', ''))
        if match:
            size_metrics['key_size'] = float(match.group(1))
        
        # Extract ciphertext sizes
        ciphertext_size_pattern = r'Ciphertext size: ([\d.]+) bytes'
        match = re.search(ciphertext_size_pattern, operation_result.get('stdout', ''))
        if match:
            size_metrics['ciphertext_size'] = float(match.group(1))
        
        return size_metrics
    
    def extract_gas_costs(self, operation_result):
        """Extract blockchain gas costs from operation results"""
        gas_costs = {}
        
        # Gas cost patterns
        gas_patterns = {
            'deploy_gas': r'Contract deployment gas: ([\d]+)',
            'set_attr_commit_gas': r'setUserAttributes gas: ([\d]+)',
            'verify_attr_proof_gas': r'verifyAttributeProof gas: ([\d]+)',
            'verify_policy_proof_gas': r'verifyPolicyProof gas: ([\d]+)',
            'verify_process_proof_gas': r'verifyProcessProof gas: ([\d]+)'
        }
        
        combined_output = operation_result.get('stdout', '') + operation_result.get('stderr', '')
        for key, pattern in gas_patterns.items():
            match = re.search(pattern, combined_output)
            if match:
                gas_costs[key] = int(match.group(1))
        
        return gas_costs
    
    # =================== A. PERFORMANCE BENCHMARKS ===================
    
    def benchmark_maabe_setup(self, num_authorities=3, num_attributes=10):
        """Benchmark MA-ABE Setup operations"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation maabe_setup --authorities {num_authorities} --attributes {num_attributes}'
        return self.run_command_with_profiling(command, "maabe_setup")
    
    def benchmark_maabe_keygen(self, user_type='MANUFACTURER', num_attributes=5):
        """Benchmark MA-ABE KeyGen operations"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation maabe_keygen --user_type {user_type} --attributes {num_attributes}'
        return self.run_command_with_profiling(command, "maabe_keygen")
    
    def benchmark_maabe_encrypt(self, message_size='1KB', policy_complexity='medium'):
        """Benchmark MA-ABE Encrypt operations"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation maabe_encrypt --message_size {message_size} --policy {policy_complexity}'
        return self.run_command_with_profiling(command, "maabe_encrypt")
    
    def benchmark_maabe_decrypt(self, num_satisfying_attrs=3):
        """Benchmark MA-ABE Decrypt operations"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation maabe_decrypt --satisfying_attrs {num_satisfying_attrs}'
        return self.run_command_with_profiling(command, "maabe_decrypt")
    
    def benchmark_zksnark_setup(self, circuit_type='attribute'):
        """Benchmark zkSNARK Setup operations"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation zksnark_setup --circuit_type {circuit_type}'
        return self.run_command_with_profiling(command, "zksnark_setup")
    
    def benchmark_zksnark_witness_gen(self, circuit_type='attribute', input_size='small'):
        """Benchmark zkSNARK Witness Generation"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation zksnark_witness --circuit_type {circuit_type} --input_size {input_size}'
        return self.run_command_with_profiling(command, "zksnark_witness")
    
    def benchmark_zksnark_proof_gen(self, circuit_type='attribute'):
        """Benchmark zkSNARK Proof Generation"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation zksnark_proof --circuit_type {circuit_type}'
        return self.run_command_with_profiling(command, "zksnark_proof")
    
    def benchmark_zksnark_verify_offchain(self, circuit_type='attribute'):
        """Benchmark zkSNARK Off-chain Verification"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation zksnark_verify_offchain --circuit_type {circuit_type}'
        return self.run_command_with_profiling(command, "zksnark_verify_offchain")
    
    def benchmark_zksnark_verify_onchain(self, circuit_type='attribute'):
        """Benchmark zkSNARK On-chain Verification"""
        command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation zksnark_verify_onchain --circuit_type {circuit_type}'
        return self.run_command_with_profiling(command, "zksnark_verify_onchain")
    
    def benchmark_end_to_end_latency(self, user_type='MANUFACTURER'):
        """Benchmark End-to-End Latency"""
        # Key Request Latency
        key_request_result = self.run_command_with_profiling(
            f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation key_request --user_type {user_type}',
            "key_request_latency"
        )
        
        # Decryption Latency
        decryption_result = self.run_command_with_profiling(
            f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation decryption_e2e --user_type {user_type}',
            "decryption_latency"
        )
        
        return {
            'key_request': key_request_result,
            'decryption': decryption_result
        }
    
    # =================== B. COST BENCHMARKS ===================
    
    def benchmark_blockchain_costs(self):
        """Benchmark all blockchain-related costs"""
        operations = [
            'deploy_contracts',
            'set_attr_commit',
            'verify_attr_proof',
            'verify_policy_proof',
            'verify_process_proof'
        ]
        
        cost_results = {}
        for operation in operations:
            command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation blockchain_{operation}'
            result = self.run_command_with_profiling(command, f"blockchain_{operation}")
            cost_results[operation] = result
        
        return cost_results
    
    def calculate_gas_costs_usd(self, gas_costs):
        """Convert gas costs to USD"""
        gas_price_wei = self.blockchain_config['gas_price_gwei'] * 1e9
        eth_price = self.blockchain_config['eth_price_usd']
        
        usd_costs = {}
        for operation, gas_used in gas_costs.items():
            eth_cost = (gas_used * gas_price_wei) / 1e18
            usd_cost = eth_cost * eth_price
            usd_costs[operation] = {
                'gas_used': gas_used,
                'eth_cost': eth_cost,
                'usd_cost': usd_cost
            }
        
        return usd_costs
    
    # =================== C. SCALABILITY BENCHMARKS ===================
    
    def benchmark_authority_scalability(self):
        """Test scalability with varying number of authorities"""
        results = {}
        
        for num_auth in self.authorities:
            print(f"Testing with {num_auth} authorities...")
            
            # Test key operations with varying authorities
            setup_result = self.benchmark_maabe_setup(num_authorities=num_auth)
            keygen_result = self.benchmark_maabe_keygen()
            encrypt_result = self.benchmark_maabe_encrypt()
            
            results[num_auth] = {
                'setup': setup_result,
                'keygen': keygen_result,
                'encrypt': encrypt_result
            }
        
        return results
    
    def benchmark_user_scalability(self):
        """Test scalability with varying number of users"""
        results = {}
        
        for i, user_count in enumerate([10, 50, 100, 200, 500]):
            print(f"Testing with {user_count} users...")
            
            command = f'cd /test/sh_files && python3 ../src/benchmark_components.py --operation scalability_users --user_count {user_count}'
            result = self.run_command_with_profiling(command, "user_scalability")
            results[user_count] = result
        
        return results
    
    def benchmark_attribute_scalability(self):
        """Test scalability with varying number of attributes"""
        results = {}
        
        for num_attrs in self.attribute_counts:
            print(f"Testing with {num_attrs} attributes...")
            
            setup_result = self.benchmark_maabe_setup(num_attributes=num_attrs)
            keygen_result = self.benchmark_maabe_keygen(num_attributes=num_attrs)
            
            results[num_attrs] = {
                'setup': setup_result,
                'keygen': keygen_result
            }
        
        return results
    
    def benchmark_policy_complexity_scalability(self):
        """Test scalability with varying policy complexity"""
        results = {}
        
        for complexity in self.policy_complexities:
            print(f"Testing with {complexity} policy complexity...")
            
            encrypt_result = self.benchmark_maabe_encrypt(policy_complexity=complexity)
            decrypt_result = self.benchmark_maabe_decrypt()
            
            results[complexity] = {
                'encrypt': encrypt_result,
                'decrypt': decrypt_result
            }
        
        return results
    
    # =================== COMPREHENSIVE BENCHMARK EXECUTION ===================
    
    def run_comprehensive_benchmark(self):
        """Run complete MARTSIA-compliant benchmark suite"""
        print(f"Starting MARTSIA Comprehensive Benchmark ({self.iterations} iterations)")
        print("=" * 80)
        
        all_results = {
            'performance': defaultdict(list),
            'costs': defaultdict(list),
            'scalability': defaultdict(list),
            'gas_tracking': {},
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'iterations': self.iterations,
                'blockchain_config': self.blockchain_config,
                'enhanced_gas_tracking': self.enable_enhanced_gas_tracking
            }
        }
        
        # Enhanced Gas Tracking Demo (run once at the beginning)
        if self.enable_enhanced_gas_tracking:
            print("\n--- Enhanced Gas Tracking Demo ---")
            self.track_end_to_end_gas_costs("encryption", "demo_msg_001")
            self.track_end_to_end_gas_costs("decryption", "demo_msg_001", "MANUFACTURER")
            self.track_end_to_end_gas_costs("certification", "demo_proc_001")
            self.track_end_to_end_gas_costs("authority", "demo_auth_001")
            
            print("\n[INFO] Enhanced gas tracking demonstration completed")
            print("Step-by-step gas costs are being tracked throughout the benchmark...")
        
        for i in tqdm(range(self.iterations), desc="Running MARTSIA benchmarks"):
            iteration_results = {}
            
            # A. PERFORMANCE BENCHMARKS
            print(f"\n--- Performance Benchmarks (Iteration {i+1}) ---")
            
            # MA-ABE Operations
            iteration_results['maabe_setup'] = self.benchmark_maabe_setup()
            iteration_results['maabe_keygen'] = self.benchmark_maabe_keygen()
            iteration_results['maabe_encrypt'] = self.benchmark_maabe_encrypt()
            iteration_results['maabe_decrypt'] = self.benchmark_maabe_decrypt()
            
            # zkSNARK Operations
            for circuit_type in ['attribute', 'policy', 'process']:
                iteration_results[f'zksnark_setup_{circuit_type}'] = self.benchmark_zksnark_setup(circuit_type)
                iteration_results[f'zksnark_witness_{circuit_type}'] = self.benchmark_zksnark_witness_gen(circuit_type)
                iteration_results[f'zksnark_proof_{circuit_type}'] = self.benchmark_zksnark_proof_gen(circuit_type)
                iteration_results[f'zksnark_verify_offchain_{circuit_type}'] = self.benchmark_zksnark_verify_offchain(circuit_type)
                iteration_results[f'zksnark_verify_onchain_{circuit_type}'] = self.benchmark_zksnark_verify_onchain(circuit_type)
            
            # End-to-End Latency
            iteration_results['e2e_latency'] = self.benchmark_end_to_end_latency()
            
            # B. COST BENCHMARKS
            print(f"\n--- Cost Benchmarks (Iteration {i+1}) ---")
            iteration_results['blockchain_costs'] = self.benchmark_blockchain_costs()
            
            # Enhanced gas tracking for this iteration
            if self.enable_enhanced_gas_tracking and i % 10 == 0:  # Every 10th iteration
                print(f"[GAS] Running enhanced gas tracking for iteration {i+1}")
                self.track_end_to_end_gas_costs("encryption", f"iter_{i}_encryption")
                self.track_end_to_end_gas_costs("decryption", f"iter_{i}_decryption", "LOGISTIC")
            
            all_results['performance'][i] = iteration_results
            
            # Short pause between iterations
            time.sleep(0.5)
        
        # C. SCALABILITY BENCHMARKS (run once)
        print("\n--- Scalability Benchmarks ---")
        all_results['scalability']['authorities'] = self.benchmark_authority_scalability()
        all_results['scalability']['users'] = self.benchmark_user_scalability()
        all_results['scalability']['attributes'] = self.benchmark_attribute_scalability()
        all_results['scalability']['policy_complexity'] = self.benchmark_policy_complexity_scalability()
        
        # Enhanced gas tracking summary
        if self.enable_enhanced_gas_tracking:
            print("\n--- Enhanced Gas Tracking Summary ---")
            all_results['gas_tracking'] = self.get_gas_summary_report()
            self.print_gas_summary()
        
        # Analysis and Visualization
        self.analyze_comprehensive_results(all_results)
        self.generate_martsia_visualizations(all_results)
        self.save_comprehensive_results(all_results)
        
        # Save gas report
        if self.enable_enhanced_gas_tracking:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_gas_report(f"martsia_gas_report_{timestamp}.json")
        
        return all_results
    
    # =================== ANALYSIS AND VISUALIZATION ===================
    
    def analyze_comprehensive_results(self, results):
        """Comprehensive analysis of MARTSIA benchmark results"""
        print("\n" + "=" * 80)
        print("MARTSIA COMPREHENSIVE BENCHMARK ANALYSIS")
        print("=" * 80)
        
        # A. Performance Analysis
        self.analyze_performance_metrics(results['performance'])
        
        # B. Cost Analysis
        self.analyze_cost_metrics(results['performance'])
        
        # C. Scalability Analysis
        self.analyze_scalability_metrics(results['scalability'])
    
    def analyze_performance_metrics(self, performance_results):
        """Analyze performance metrics"""
        print("\nA. PERFORMANCE METRICS ANALYSIS")
        print("-" * 50)
        
        # MA-ABE Operations
        print("\n   MA-ABE Operations:")
        maabe_ops = ['maabe_setup', 'maabe_keygen', 'maabe_encrypt', 'maabe_decrypt']
        for op in maabe_ops:
            times = [result[op]['total_time'] for result in performance_results.values() if op in result and result[op]['success']]
            if times:
                print(f"      {op.replace('maabe_', '').title()}: {statistics.mean(times):.3f}s +/- {statistics.stdev(times):.3f}s")
        
        # zkSNARK Operations
        print("\n   zkSNARK Operations:")
        circuits = ['attribute', 'policy', 'process']
        zksnark_ops = ['setup', 'witness', 'proof', 'verify_offchain', 'verify_onchain']
        
        for circuit in circuits:
            print(f"      {circuit.title()} Circuit:")
            for op in zksnark_ops:
                key = f'zksnark_{op}_{circuit}'
                times = [result[key]['total_time'] for result in performance_results.values() if key in result and result[key]['success']]
                if times:
                    print(f"         {op.replace('_', ' ').title()}: {statistics.mean(times):.3f}s +/- {statistics.stdev(times):.3f}s")
    
    def analyze_cost_metrics(self, performance_results):
        """Analyze cost metrics"""
        print("\nB. COST METRICS ANALYSIS")
        print("-" * 50)
        
        # Extract size metrics
        print("\n   Size Metrics:")
        # Implementation would extract actual size data from results
        
        # Extract gas costs
        print("\n   Blockchain Gas Costs:")
        # Implementation would extract actual gas cost data from results
    
    def analyze_scalability_metrics(self, scalability_results):
        """Analyze scalability metrics"""
        print("\nC. SCALABILITY METRICS ANALYSIS")
        print("-" * 50)
        
        # Authority Scalability
        print("\n   Authority Scalability:")
        if 'authorities' in scalability_results:
            auth_data = scalability_results['authorities']
            for num_auth, data in auth_data.items():
                setup_time = data['setup']['total_time'] if data['setup']['success'] else float('inf')
                print(f"      {num_auth} authorities: Setup {setup_time:.3f}s")
        
        # User Scalability
        print("\n   User Scalability:")
        if 'users' in scalability_results:
            user_data = scalability_results['users']
            for user_count, data in user_data.items():
                total_time = data['total_time'] if data['success'] else float('inf')
                print(f"      {user_count} users: {total_time:.3f}s")
    
    def generate_martsia_visualizations(self, results):
        """Generate MARTSIA-specific visualizations"""
        # Performance visualizations
        self.plot_maabe_performance(results['performance'])
        self.plot_zksnark_performance(results['performance'])
        self.plot_scalability_analysis(results['scalability'])
        self.plot_cost_analysis(results['performance'])
    
    def plot_maabe_performance(self, performance_results):
        """Plot MA-ABE performance metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('MA-ABE Performance Metrics', fontsize=16)
        
        operations = ['maabe_setup', 'maabe_keygen', 'maabe_encrypt', 'maabe_decrypt']
        operation_names = ['Setup', 'KeyGen', 'Encrypt', 'Decrypt']
        
        for i, (op, name) in enumerate(zip(operations, operation_names)):
            ax = axes[i//2, i%2]
            times = [result[op]['total_time'] for result in performance_results.values() if op in result and result[op]['success']]
            memories = [result[op]['memory_delta'] for result in performance_results.values() if op in result and result[op]['success']]
            
            if times:
                ax.hist(times, bins=20, alpha=0.7, color=self.colors[i])
                ax.set_title(f'{name} Time Distribution')
                ax.set_xlabel('Time (seconds)')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'maabe_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_zksnark_performance(self, performance_results):
        """Plot zkSNARK performance metrics"""
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle('zkSNARK Performance Metrics by Circuit Type', fontsize=16)
        
        circuits = ['attribute', 'policy', 'process']
        operations = ['setup', 'proof']
        
        for i, circuit in enumerate(circuits):
            for j, op in enumerate(operations):
                ax = axes[i, j]
                key = f'zksnark_{op}_{circuit}'
                times = [result[key]['total_time'] for result in performance_results.values() if key in result and result[key]['success']]
                
                if times:
                    ax.hist(times, bins=15, alpha=0.7, color=self.colors[i*2+j])
                    ax.set_title(f'{circuit.title()} Circuit - {op.title()}')
                    ax.set_xlabel('Time (seconds)')
                    ax.set_ylabel('Frequency')
                    ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'zksnark_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_scalability_analysis(self, scalability_results):
        """Plot scalability analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('SMART-ZK Scalability Analysis', fontsize=16)
        
        # Authority scalability
        if 'authorities' in scalability_results:
            ax = axes[0, 0]
            auth_counts = list(scalability_results['authorities'].keys())
            setup_times = [data['setup']['total_time'] for data in scalability_results['authorities'].values() if data['setup']['success']]
            if setup_times:
                ax.plot(auth_counts, setup_times, 'o-', color=self.colors[0], linewidth=2, markersize=6)
                ax.set_title('Authority Scalability')
                ax.set_xlabel('Number of Authorities')
                ax.set_ylabel('Setup Time (seconds)')
                ax.grid(True, alpha=0.3)
        
        # User scalability
        if 'users' in scalability_results:
            ax = axes[0, 1]
            user_counts = list(scalability_results['users'].keys())
            processing_times = [data['total_time'] for data in scalability_results['users'].values() if data['success']]
            if processing_times:
                ax.plot(user_counts, processing_times, 's-', color=self.colors[1], linewidth=2, markersize=6)
                ax.set_title('User Scalability')
                ax.set_xlabel('Number of Users')
                ax.set_ylabel('Processing Time (seconds)')
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'smartzk_scalability_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_cost_analysis(self, performance_results):
        """Plot cost analysis"""
        # Implementation for cost visualization
        pass
    
    def save_comprehensive_results(self, results):
        """Save comprehensive results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        with open(os.path.join(self.results_dir, f'martsia_benchmark_{timestamp}.json'), 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save summary report
        summary = self.generate_summary_report(results)
        with open(os.path.join(self.results_dir, f'martsia_summary_{timestamp}.json'), 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\nResults saved to: {self.results_dir}")
    
    def generate_summary_report(self, results):
        """Generate summary report"""
        summary = {
            'benchmark_info': results['metadata'],
            'performance_summary': {},
            'cost_summary': {},
            'scalability_summary': {}
        }
        
        # Add performance summaries
        # Add cost summaries  
        # Add scalability summaries
        
        return summary

    # =================== ENHANCED GAS TRACKING METHODS ===================
    
    def track_end_to_end_gas_costs(self, operation_type: str, message_id: str = None, user_type: str = None):
        """Track detailed gas costs for end-to-end operations"""
        if not self.enable_enhanced_gas_tracking:
            return None
            
        if message_id is None:
            message_id = f"benchmark_{int(time.time())}"
            
        if operation_type == "encryption":
            return self.gas_tracker.track_encryption_workflow(message_id, slice_count=4)
        elif operation_type == "decryption":
            user = user_type or "MANUFACTURER"
            return self.gas_tracker.track_decryption_workflow(message_id, user, authority_count=3)
        elif operation_type == "certification":
            return self.gas_tracker.track_certification_workflow(message_id, attribute_count=10)
        elif operation_type == "authority":
            return self.gas_tracker.track_authority_operations(message_id, key_generations=5)
        
        return None
    
    def get_gas_summary_report(self):
        """Get comprehensive gas usage report"""
        if not self.enable_enhanced_gas_tracking:
            return "Enhanced gas tracking not enabled"
            
        return self.gas_tracker.get_comprehensive_report()
    
    def print_gas_summary(self):
        """Print gas usage summary"""
        if self.enable_enhanced_gas_tracking:
            self.gas_tracker.print_summary()
        else:
            print("[INFO] Enhanced gas tracking not enabled - no detailed gas report available")
    
    def save_gas_report(self, filename: str = None):
        """Save detailed gas report to file"""
        if self.enable_enhanced_gas_tracking:
            self.gas_tracker.save_detailed_report(filename)
        else:
            print("[INFO] Enhanced gas tracking not enabled - no gas report to save")

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = {
        'matplotlib': 'matplotlib',
        'numpy': 'numpy', 
        'psutil': 'psutil',
        'tqdm': 'tqdm'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"[OK] {package_name} available")
        except ImportError:
            missing_packages.append(package_name)
            print(f"[MISSING] {package_name}")
    
    # Check optional seaborn
    try:
        import seaborn
        print("[OK] seaborn available (optional)")
    except ImportError:
        print("[INFO] seaborn not available (optional, will use matplotlib defaults)")
    
    if missing_packages:
        print(f"\nError: Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Main benchmark execution with MARTSIA compliance"""
    import argparse
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="MARTSIA-Compliant MARTZK System Benchmark")
    parser.add_argument('-i', '--iterations', type=int, default=5,
                       help='Number of benchmark iterations (default: 5)')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick benchmark with 5 iterations')
    parser.add_argument('--performance-only', action='store_true',
                       help='Run only performance benchmarks')
    parser.add_argument('--scalability-only', action='store_true',
                       help='Run only scalability benchmarks')
    parser.add_argument('--disable-gas-tracking', action='store_true',
                       help='Disable enhanced step-by-step gas tracking')
    parser.add_argument('--gas-price', type=float, default=20,
                       help='Gas price in Gwei for cost calculations (default: 20)')
    parser.add_argument('--eth-price', type=float, default=2000,
                       help='ETH price in USD for cost calculations (default: 2000)')
    
    args = parser.parse_args()
    iterations = 5 if args.quick else args.iterations
    
    print("MARTSIA-Compliant MARTZK System Benchmark")
    print(f"Running {iterations} iterations")
    print("Measuring: MA-ABE, zkSNARK, Blockchain Costs, and Scalability")
    if not args.disable_gas_tracking:
        print(f"Enhanced Gas Tracking: Enabled (Gas: {args.gas_price} Gwei, ETH: ${args.eth_price})")
    else:
        print("Enhanced Gas Tracking: Disabled")
    print("-" * 80)
    
    try:
        # Configure blockchain settings
        blockchain_config = {
            'gas_price_gwei': args.gas_price,
            'eth_price_usd': args.eth_price
        }
        
        benchmark = MARTSIABenchmark(
            iterations=iterations, 
            enable_enhanced_gas_tracking=not args.disable_gas_tracking
        )
        
        # Update blockchain config
        benchmark.blockchain_config.update(blockchain_config)
        if benchmark.gas_tracker:
            benchmark.gas_tracker.gas_price_gwei = args.gas_price
            benchmark.gas_tracker.eth_price_usd = args.eth_price
        
        if args.scalability_only:
            print("Running scalability benchmarks only...")
            # Run only scalability tests
            results = {
                'scalability': {
                    'authorities': benchmark.benchmark_authority_scalability(),
                    'users': benchmark.benchmark_user_scalability(),
                    'attributes': benchmark.benchmark_attribute_scalability(),
                    'policy_complexity': benchmark.benchmark_policy_complexity_scalability()
                },
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'test_type': 'scalability_only'
                }
            }
            benchmark.analyze_scalability_metrics(results['scalability'])
            
        elif args.performance_only:
            print("Running performance benchmarks only...")
            # Run subset of performance tests
            performance_results = {}
            for i in range(iterations):
                print(f"Performance test iteration {i+1}/{iterations}")
                performance_results[i] = {
                    'maabe_setup': benchmark.benchmark_maabe_setup(),
                    'maabe_encrypt': benchmark.benchmark_maabe_encrypt(),
                    'zksnark_proof_attribute': benchmark.benchmark_zksnark_proof_gen('attribute')
                }
            
            results = {
                'performance': performance_results,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'test_type': 'performance_only'
                }
            }
            benchmark.analyze_performance_metrics(results['performance'])
            
        else:
            # Full comprehensive benchmark
            benchmark.run_comprehensive_benchmark()
            
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        if 'benchmark' in locals() and benchmark.enable_enhanced_gas_tracking:
            print("Saving partial gas tracking results...")
            benchmark.save_gas_report("interrupted_gas_report.json")
    except Exception as e:
        print(f"\nBenchmark failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nMARTSIA benchmark completed!")

if __name__ == "__main__":
    main() 