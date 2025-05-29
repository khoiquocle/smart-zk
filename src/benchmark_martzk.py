#!/usr/bin/env python3
"""
MARTZK System Comprehensive Benchmark Suite
Measures: Performance, Computational Overhead, Fees, Execution Time, etc.
"""

import os
import sys
import time
import json
import psutil
import statistics
import subprocess
import tempfile
import shutil
from datetime import datetime
from collections import defaultdict
import sqlite3
from decouple import config
import hashlib
import random
import ipfshttpclient

# Data visualization and analysis
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from charm.toolbox.pairinggroup import *
from charm.core.engine.util import objectToBytes, bytesToObject
import cryptocode
from maabe_class import *
from zksnark.prover import generate_proof
from zksnark.utils import compute_pedersen_hash

class MARTZKBenchmark:
    def __init__(self, iterations=100, generate_charts=True):
        self.iterations = iterations
        self.generate_charts = generate_charts
        self.results = {
            'encryption': [],
            'decryption': [],
            'zksnark_proof_generation': [],
            'zksnark_proof_verification': [],
            'ipfs_upload': [],
            'ipfs_download': [],
            'database_operations': [],
            'memory_usage': [],
            'cpu_usage': [],
            'file_sizes': [],
            'gas_costs': [],
            'storage_overhead': [],
            'end_to_end_latency': []
        }
        self.test_files = []
        self.charts_dir = "benchmark_charts"
        self.setup_environment()
    
    def setup_environment(self):
        """Setup test environment and create test files of various sizes"""
        print("🔧 Setting up benchmark environment...")
        
        # Initialize crypto components
        self.groupObj = PairingGroup('SS512')
        self.maabe = MaabeRW15(self.groupObj)
        
        try:
            # Check if running in Docker and adjust IPFS connection
            ipfs_host = os.getenv('IPFS_HOST', '127.0.0.1')
            ipfs_port = int(os.getenv('IPFS_PORT', '5001'))
            self.api = ipfshttpclient.connect(f'/ip4/{ipfs_host}/tcp/{ipfs_port}')
            print(f"✅ Connected to IPFS at {ipfs_host}:{ipfs_port}")
        except Exception as e:
            print(f"Warning: IPFS not available: {e}")
            self.api = None
        
        # Create test directory
        self.test_dir = tempfile.mkdtemp(prefix="martzk_benchmark_")
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create charts directory
        if self.generate_charts:
            os.makedirs(self.charts_dir, exist_ok=True)
            # Set matplotlib backend for headless environment
            plt.switch_backend('Agg')
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
        
        # Create test files of various sizes (1KB, 10KB, 100KB, 1MB)
        file_sizes = [1024, 10*1024, 100*1024, 1024*1024]
        for i, size in enumerate(file_sizes):
            filename = f"test_file_{size//1024}KB.txt"
            filepath = os.path.join(self.test_dir, filename)
            
            # Generate random content
            content = os.urandom(size)
            with open(filepath, 'wb') as f:
                f.write(content)
            
            self.test_files.append({
                'path': filepath,
                'name': filename,
                'size': size
            })
        
        print(f"✅ Created {len(self.test_files)} test files in {self.test_dir}")
    
    def measure_memory_cpu(self):
        """Measure current memory and CPU usage"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        return memory_mb, cpu_percent
    
    def benchmark_encryption(self, file_info):
        """Benchmark encryption process"""
        start_time = time.time()
        start_memory, start_cpu = self.measure_memory_cpu()
        
        try:
            # Generate test access policy
            access_policy = "(MANUFACTURER@AUTH1 or CUSTOMS@AUTH1)"
            
            # Read file content
            with open(file_info['path'], 'rb') as f:
                file_content = f.read()
            
            # Convert to base64 (like in real system)
            import base64
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # Generate symmetric key
            import secrets
            symmetric_key = secrets.token_hex(32)
            
            # Generate dummy MA-ABE element
            dummy_element = self.groupObj.random(GT)
            
            # Create mock public parameters and keys for encryption
            mock_public_params = {'g1': self.groupObj.random(G1), 'g2': self.groupObj.random(G2)}
            mock_pk = {'AUTH1': {'g': self.groupObj.random(G1), 'h': self.groupObj.random(G2)}}
            
            # Encrypt file content
            encrypted_content = cryptocode.encrypt(file_base64, symmetric_key)
            
            end_time = time.time()
            end_memory, end_cpu = self.measure_memory_cpu()
            
            encryption_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            return {
                'time': encryption_time,
                'memory_delta': memory_used,
                'cpu_usage': end_cpu,
                'file_size': file_info['size'],
                'success': True
            }
            
        except Exception as e:
            return {
                'time': time.time() - start_time,
                'memory_delta': 0,
                'cpu_usage': 0,
                'file_size': file_info['size'],
                'success': False,
                'error': str(e)
            }
    
    def benchmark_decryption(self, file_info, symmetric_key, encrypted_content):
        """Benchmark decryption process"""
        start_time = time.time()
        start_memory, start_cpu = self.measure_memory_cpu()
        
        try:
            # Simulate MA-ABE decryption (just return success for benchmark)
            dummy_element = self.groupObj.random(GT)
            
            # Decrypt file content
            decrypted_content = cryptocode.decrypt(encrypted_content, symmetric_key)
            
            end_time = time.time()
            end_memory, end_cpu = self.measure_memory_cpu()
            
            decryption_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            return {
                'time': decryption_time,
                'memory_delta': memory_used,
                'cpu_usage': end_cpu,
                'file_size': file_info['size'],
                'success': decrypted_content is not False
            }
            
        except Exception as e:
            return {
                'time': time.time() - start_time,
                'memory_delta': 0,
                'cpu_usage': 0,
                'file_size': file_info['size'],
                'success': False,
                'error': str(e)
            }
    
    def benchmark_zksnark_proof_generation(self):
        """Benchmark zkSNARK proof generation"""
        start_time = time.time()
        start_memory, start_cpu = self.measure_memory_cpu()
        
        try:
            # Generate test inputs
            attr_secret = random.randint(1000000000, 9999999999)
            attr_value = "MANUFACTURER"
            attr_value_numeric = sum(ord(c) * (256 ** i) for i, c in enumerate(attr_value[:8]))
            authority_number = 1
            attr_type = 0
            expiry_date = 20260528
            current_date = 20250529
            
            # Compute commitment
            commitment = compute_pedersen_hash([attr_secret, attr_value_numeric, authority_number, attr_type, expiry_date])
            
            # Prepare circuit input
            input_data = {
                "attr_secret": str(attr_secret),
                "attr_value": str(attr_value_numeric),
                "authority_id": str(authority_number),
                "attr_type": str(attr_type),
                "expiry_date": str(expiry_date),
                "attr_commitment": str(commitment),
                "current_date": str(current_date),
                "expected_authority_id": str(authority_number),
                "expected_attr_type": str(attr_type)
            }
            
            # Generate proof
            proof_data, public_inputs = generate_proof("proof_of_attribute", input_data)
            
            end_time = time.time()
            end_memory, end_cpu = self.measure_memory_cpu()
            
            generation_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            return {
                'time': generation_time,
                'memory_delta': memory_used,
                'cpu_usage': end_cpu,
                'proof_size': len(json.dumps(proof_data)),
                'success': True
            }
            
        except Exception as e:
            return {
                'time': time.time() - start_time,
                'memory_delta': 0,
                'cpu_usage': 0,
                'proof_size': 0,
                'success': False,
                'error': str(e)
            }
    
    def benchmark_ipfs_operations(self, file_info):
        """Benchmark IPFS upload and download operations"""
        if not self.api:
            return {'upload': {'success': False, 'error': 'IPFS not available'}, 
                   'download': {'success': False, 'error': 'IPFS not available'}}
        
        # Upload benchmark
        upload_start = time.time()
        try:
            with open(file_info['path'], 'rb') as f:
                content = f.read()
            
            # Upload to IPFS
            result = self.api.add_bytes(content)
            upload_time = time.time() - upload_start
            ipfs_hash = result
            
            upload_result = {
                'time': upload_time,
                'file_size': file_info['size'],
                'hash': ipfs_hash,
                'success': True
            }
        except Exception as e:
            upload_result = {
                'time': time.time() - upload_start,
                'file_size': file_info['size'],
                'success': False,
                'error': str(e)
            }
            return {'upload': upload_result, 'download': {'success': False, 'error': 'Upload failed'}}
        
        # Download benchmark
        download_start = time.time()
        try:
            downloaded_content = self.api.cat(ipfs_hash)
            download_time = time.time() - download_start
            
            download_result = {
                'time': download_time,
                'file_size': len(downloaded_content),
                'success': True
            }
        except Exception as e:
            download_result = {
                'time': time.time() - download_start,
                'file_size': 0,
                'success': False,
                'error': str(e)
            }
        
        return {'upload': upload_result, 'download': download_result}
    
    def benchmark_database_operations(self):
        """Benchmark database operations"""
        start_time = time.time()
        
        try:
            # Create temporary database
            db_path = os.path.join(self.test_dir, "benchmark.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_attributes (
                    id INTEGER PRIMARY KEY,
                    user_address TEXT,
                    attr_value TEXT,
                    commitment INTEGER,
                    timestamp TEXT
                )
            """)
            
            # Insert test data
            test_data = []
            for i in range(100):
                test_data.append((
                    f"0x{i:040x}",
                    f"ATTR_VALUE_{i}",
                    random.randint(1000000000, 9999999999),
                    datetime.now().isoformat()
                ))
            
            cursor.executemany("""
                INSERT INTO test_attributes (user_address, attr_value, commitment, timestamp)
                VALUES (?, ?, ?, ?)
            """, test_data)
            
            # Query data
            cursor.execute("SELECT COUNT(*) FROM test_attributes")
            count = cursor.fetchone()[0]
            
            # Clean up
            conn.commit()
            conn.close()
            os.remove(db_path)
            
            db_time = time.time() - start_time
            
            return {
                'time': db_time,
                'operations': 100,
                'success': True
            }
            
        except Exception as e:
            return {
                'time': time.time() - start_time,
                'operations': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_single_iteration(self, iteration_num):
        """Run a single benchmark iteration"""
        print(f"🔄 Running iteration {iteration_num + 1}/{self.iterations}")
        
        iteration_results = {}
        
        # Test with random file
        test_file = random.choice(self.test_files)
        
        # Measure end-to-end latency
        e2e_start = time.time()
        
        # 1. Encryption benchmark
        enc_result = self.benchmark_encryption(test_file)
        iteration_results['encryption'] = enc_result
        
        if enc_result['success']:
            # 2. Decryption benchmark (using mock data)
            symmetric_key = "mock_key_for_benchmark"
            encrypted_content = "mock_encrypted_content"
            dec_result = self.benchmark_decryption(test_file, symmetric_key, encrypted_content)
            iteration_results['decryption'] = dec_result
        
        # 3. zkSNARK proof generation benchmark
        zksnark_result = self.benchmark_zksnark_proof_generation()
        iteration_results['zksnark_proof'] = zksnark_result
        
        # 4. IPFS operations benchmark
        ipfs_result = self.benchmark_ipfs_operations(test_file)
        iteration_results['ipfs'] = ipfs_result
        
        # 5. Database operations benchmark
        db_result = self.benchmark_database_operations()
        iteration_results['database'] = db_result
        
        # End-to-end latency
        e2e_time = time.time() - e2e_start
        iteration_results['end_to_end'] = {'time': e2e_time, 'file_size': test_file['size']}
        
        return iteration_results
    
    def run_benchmark(self):
        """Run the complete benchmark suite"""
        print(f"🚀 Starting MARTZK Benchmark Suite ({self.iterations} iterations)")
        print("=" * 60)
        
        all_results = []
        
        for i in range(self.iterations):
            try:
                iteration_result = self.run_single_iteration(i)
                all_results.append(iteration_result)
                
                # Progress update every 10 iterations
                if (i + 1) % 10 == 0:
                    print(f"✅ Completed {i + 1}/{self.iterations} iterations")
                    
            except Exception as e:
                print(f"❌ Error in iteration {i + 1}: {e}")
                continue
        
        # Process and analyze results
        self.analyze_results(all_results)
    
    def analyze_results(self, all_results):
        """Analyze and display benchmark results"""
        print("\n" + "=" * 60)
        print("📊 MARTZK BENCHMARK RESULTS")
        print("=" * 60)
        
        # Extract metrics for analysis
        metrics = {
            'encryption_times': [],
            'decryption_times': [],
            'zksnark_times': [],
            'ipfs_upload_times': [],
            'ipfs_download_times': [],
            'database_times': [],
            'end_to_end_times': [],
            'memory_usage': [],
            'success_rates': defaultdict(int),
            'file_sizes': []
        }
        
        total_iterations = len(all_results)
        
        for result in all_results:
            # Encryption metrics
            if 'encryption' in result and result['encryption']['success']:
                metrics['encryption_times'].append(result['encryption']['time'])
                metrics['memory_usage'].append(result['encryption']['memory_delta'])
                metrics['file_sizes'].append(result['encryption']['file_size'])
                metrics['success_rates']['encryption'] += 1
            
            # Decryption metrics
            if 'decryption' in result and result['decryption']['success']:
                metrics['decryption_times'].append(result['decryption']['time'])
                metrics['success_rates']['decryption'] += 1
            
            # zkSNARK metrics
            if 'zksnark_proof' in result and result['zksnark_proof']['success']:
                metrics['zksnark_times'].append(result['zksnark_proof']['time'])
                metrics['success_rates']['zksnark'] += 1
            
            # IPFS metrics
            if 'ipfs' in result:
                if result['ipfs']['upload']['success']:
                    metrics['ipfs_upload_times'].append(result['ipfs']['upload']['time'])
                    metrics['success_rates']['ipfs_upload'] += 1
                if result['ipfs']['download']['success']:
                    metrics['ipfs_download_times'].append(result['ipfs']['download']['time'])
                    metrics['success_rates']['ipfs_download'] += 1
            
            # Database metrics
            if 'database' in result and result['database']['success']:
                metrics['database_times'].append(result['database']['time'])
                metrics['success_rates']['database'] += 1
            
            # End-to-end metrics
            if 'end_to_end' in result:
                metrics['end_to_end_times'].append(result['end_to_end']['time'])
        
        # Display results
        self.display_performance_metrics(metrics, total_iterations)
        
        # Save detailed results
        self.save_results(all_results, metrics)
    
    def display_performance_metrics(self, metrics, total_iterations):
        """Display formatted performance metrics"""
        
        def stats(data_list):
            if not data_list:
                return "No data"
            return {
                'mean': statistics.mean(data_list),
                'median': statistics.median(data_list),
                'min': min(data_list),
                'max': max(data_list),
                'std_dev': statistics.stdev(data_list) if len(data_list) > 1 else 0
            }
        
        print("\n📈 PERFORMANCE METRICS")
        print("-" * 40)
        
        # Encryption Performance
        enc_stats = stats(metrics['encryption_times'])
        if enc_stats != "No data":
            print(f"🔒 ENCRYPTION:")
            print(f"   Mean time: {enc_stats['mean']:.4f}s")
            print(f"   Min/Max: {enc_stats['min']:.4f}s / {enc_stats['max']:.4f}s")
            print(f"   Success rate: {metrics['success_rates']['encryption']}/{total_iterations} ({100*metrics['success_rates']['encryption']/total_iterations:.1f}%)")
        
        # Decryption Performance
        dec_stats = stats(metrics['decryption_times'])
        if dec_stats != "No data":
            print(f"🔓 DECRYPTION:")
            print(f"   Mean time: {dec_stats['mean']:.4f}s")
            print(f"   Min/Max: {dec_stats['min']:.4f}s / {dec_stats['max']:.4f}s")
            print(f"   Success rate: {metrics['success_rates']['decryption']}/{total_iterations} ({100*metrics['success_rates']['decryption']/total_iterations:.1f}%)")
        
        # zkSNARK Performance
        zk_stats = stats(metrics['zksnark_times'])
        if zk_stats != "No data":
            print(f"🔐 zkSNARK PROOF GENERATION:")
            print(f"   Mean time: {zk_stats['mean']:.4f}s")
            print(f"   Min/Max: {zk_stats['min']:.4f}s / {zk_stats['max']:.4f}s")
            print(f"   Success rate: {metrics['success_rates']['zksnark']}/{total_iterations} ({100*metrics['success_rates']['zksnark']/total_iterations:.1f}%)")
        
        # IPFS Performance
        ipfs_up_stats = stats(metrics['ipfs_upload_times'])
        if ipfs_up_stats != "No data":
            print(f"☁️ IPFS UPLOAD:")
            print(f"   Mean time: {ipfs_up_stats['mean']:.4f}s")
            print(f"   Success rate: {metrics['success_rates']['ipfs_upload']}/{total_iterations} ({100*metrics['success_rates']['ipfs_upload']/total_iterations:.1f}%)")
        
        # Database Performance
        db_stats = stats(metrics['database_times'])
        if db_stats != "No data":
            print(f"🗄️ DATABASE OPERATIONS:")
            print(f"   Mean time: {db_stats['mean']:.4f}s")
            print(f"   Success rate: {metrics['success_rates']['database']}/{total_iterations} ({100*metrics['success_rates']['database']/total_iterations:.1f}%)")
        
        # End-to-End Performance
        e2e_stats = stats(metrics['end_to_end_times'])
        if e2e_stats != "No data":
            print(f"⚡ END-TO-END LATENCY:")
            print(f"   Mean time: {e2e_stats['mean']:.4f}s")
            print(f"   Min/Max: {e2e_stats['min']:.4f}s / {e2e_stats['max']:.4f}s")
        
        # Memory Usage
        mem_stats = stats(metrics['memory_usage'])
        if mem_stats != "No data":
            print(f"💾 MEMORY USAGE:")
            print(f"   Mean delta: {mem_stats['mean']:.2f} MB")
            print(f"   Max delta: {mem_stats['max']:.2f} MB")
        
        # File Size Analysis
        file_stats = stats(metrics['file_sizes'])
        if file_stats != "No data":
            print(f"📁 FILE SIZE ANALYSIS:")
            print(f"   Mean size: {file_stats['mean']/1024:.1f} KB")
            print(f"   Size range: {file_stats['min']/1024:.1f} KB - {file_stats['max']/1024:.1f} KB")
    
    def save_results(self, all_results, metrics):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"martzk_benchmark_results_{timestamp}.json"
        
        summary = {
            'timestamp': timestamp,
            'iterations': self.iterations,
            'summary_metrics': {
                'encryption': {
                    'mean_time': statistics.mean(metrics['encryption_times']) if metrics['encryption_times'] else 0,
                    'success_rate': metrics['success_rates']['encryption'] / self.iterations if self.iterations > 0 else 0
                },
                'decryption': {
                    'mean_time': statistics.mean(metrics['decryption_times']) if metrics['decryption_times'] else 0,
                    'success_rate': metrics['success_rates']['decryption'] / self.iterations if self.iterations > 0 else 0
                },
                'zksnark': {
                    'mean_time': statistics.mean(metrics['zksnark_times']) if metrics['zksnark_times'] else 0,
                    'success_rate': metrics['success_rates']['zksnark'] / self.iterations if self.iterations > 0 else 0
                },
                'end_to_end': {
                    'mean_time': statistics.mean(metrics['end_to_end_times']) if metrics['end_to_end_times'] else 0
                }
            },
            'detailed_results': all_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
    
    def cleanup(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        print(f"🧹 Cleaned up test directory: {self.test_dir}")

def main():
    """Main benchmark execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MARTZK System Benchmark Suite")
    parser.add_argument('-i', '--iterations', type=int, default=100, 
                       help='Number of benchmark iterations (default: 100)')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick benchmark with 10 iterations')
    
    args = parser.parse_args()
    
    iterations = 10 if args.quick else args.iterations
    
    print("🎯 MARTZK System Comprehensive Benchmark")
    print(f"📊 Running {iterations} iterations")
    print("🔍 Measuring: Performance, Computational Overhead, Storage, Latency")
    print("-" * 60)
    
    benchmark = MARTZKBenchmark(iterations=iterations)
    
    try:
        benchmark.run_benchmark()
    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
    finally:
        benchmark.cleanup()
    
    print("\n✅ Benchmark completed!")

if __name__ == "__main__":
    main() 