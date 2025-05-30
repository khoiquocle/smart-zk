#!/usr/bin/env python3
"""
MARTZK System Performance Benchmark
Measures encryption and decryption operations in real-world scenarios
"""

import os
import sys
import time
import json
import psutil
import statistics
import subprocess
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

class MARTZKBenchmark:
    def __init__(self, iterations=100):
        self.iterations = iterations
        self.results = defaultdict(list)
        self.charts_dir = "benchmark_charts"
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Test scenarios
        self.users = ['MANUFACTURER', 'LOGISTIC', 'CUSTOMS', 'SUPPLIER']
        self.file_sizes = ['slice1', 'slice2', 'slice3', 'slice4']  # Different slice sizes
        
        # Basic matplotlib settings
        plt.rcParams['figure.figsize'] = [10, 6]
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    def run_command(self, command):
        """Run a shell command and measure its performance"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        cpu_start = psutil.Process().cpu_percent()
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            success = process.returncode == 0
            if not success:
                print(f"Command failed with error: {stderr.decode('utf-8', errors='ignore')}")
                print(f"Command output: {stdout.decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"Error running command: {e}")
            success = False
            
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        cpu_end = psutil.Process().cpu_percent()
        
        return {
            'time': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'cpu_usage': (cpu_end - cpu_start),
            'success': success
        }
    
    def benchmark_encryption(self):
        """Benchmark encryption operation"""
        command = 'cd /test/sh_files && sh cipher.sh --sender_name MANUFACTURER --input ../input_files/ --policies ../json_files/policies.json'
        return self.run_command(command)
    
    def benchmark_decryption_multi_user(self, message_id, slice_id):
        """Benchmark decryption with different users (access control test)"""
        results = {}
        for user in self.users:
            print(f"\nTesting decryption with user: {user}")
            command = f'cd /test/sh_files && sh decipher.sh --message_id {message_id} --slice_id {slice_id} --requester_name {user} --output_folder ../output_files/'
            result = self.run_command(command)
            results[user] = result
        return results
    
    def benchmark_file_sizes(self, message_id):
        """Benchmark performance with different file sizes"""
        results = {}
        slice_ids = {
            'slice1': '17282457773780031541',
            'slice2': '10414025325405685428',
            'slice3': '14198374505591576510',
            'slice4': '14064569387101332895'
        }
        
        for size, slice_id in slice_ids.items():
            print(f"\nTesting with file size: {size}")
            command = f'cd /test/sh_files && sh decipher.sh --message_id {message_id} --slice_id {slice_id} --requester_name MANUFACTURER --output_folder ../output_files/'
            result = self.run_command(command)
            results[size] = result
        return results
    
    def run_benchmark(self):
        """Run complete benchmark suite"""
        print(f"Starting MARTZK Comprehensive Benchmark ({self.iterations} iterations)")
        print("=" * 60)
        
        all_results = []
        
        for i in tqdm(range(self.iterations), desc="Running benchmarks"):
            iteration_result = {}
            
            # 1. Basic Encryption Benchmark
            print(f"\nRunning encryption benchmark {i+1}/{self.iterations}")
            enc_result = self.benchmark_encryption()
            iteration_result['encryption'] = enc_result
            
            if enc_result['success']:
                message_id = "17039503075528269530"  # Example ID
                slice_id = "17282457773780031541"    # Example ID
                
                # 2. Multi-User Access Control Test
                print(f"Running multi-user access control test {i+1}/{self.iterations}")
                access_results = self.benchmark_decryption_multi_user(message_id, slice_id)
                iteration_result['access_control'] = access_results
                
                # 3. File Size Impact Test
                print(f"Running file size impact test {i+1}/{self.iterations}")
                size_results = self.benchmark_file_sizes(message_id)
                iteration_result['file_sizes'] = size_results
            
            all_results.append(iteration_result)
            time.sleep(1)  # Short pause between iterations
        
        self.analyze_results(all_results)
    
    def analyze_results(self, all_results):
        """Analyze benchmark results"""
        metrics = {
            'encryption': defaultdict(list),
            'access_control': defaultdict(lambda: defaultdict(list)),
            'file_sizes': defaultdict(lambda: defaultdict(list))
        }
        
        # Process results
        for result in all_results:
            if 'encryption' in result:
                metrics['encryption']['time'].append(result['encryption']['time'])
                metrics['encryption']['memory'].append(result['encryption']['memory_delta'])
                metrics['encryption']['cpu'].append(result['encryption'].get('cpu_usage', 0))
            
            if 'access_control' in result:
                for user, data in result['access_control'].items():
                    metrics['access_control'][user]['time'].append(data['time'])
                    metrics['access_control'][user]['success'].append(data['success'])
            
            if 'file_sizes' in result:
                for size, data in result['file_sizes'].items():
                    metrics['file_sizes'][size]['time'].append(data['time'])
                    metrics['file_sizes'][size]['memory'].append(data['memory_delta'])
        
        self.display_results(metrics)
        self.plot_comprehensive_results(metrics)
        self.save_results(metrics, all_results)
    
    def plot_comprehensive_results(self, metrics):
        """Generate comprehensive visualization charts"""
        # 1. Access Control Success Rates
        plt.figure()
        success_rates = []
        for user in self.users:
            if user in metrics['access_control']:
                successes = metrics['access_control'][user]['success']
                rate = sum(successes) / len(successes) * 100 if successes else 0
                success_rates.append(rate)
            else:
                success_rates.append(0)
        
        plt.bar(self.users, success_rates, color=self.colors)
        plt.title('Access Control Success Rates by User')
        plt.ylabel('Success Rate (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'access_control_success.png'))
        plt.close()

        # 2. File Size Performance Impact
        plt.figure()
        times = []
        sizes = []
        for size in self.file_sizes:
            if size in metrics['file_sizes']:
                avg_time = statistics.mean(metrics['file_sizes'][size]['time'])
                times.append(avg_time)
                sizes.append(size)
        
        plt.plot(sizes, times, marker='o')
        plt.title('Processing Time by File Size')
        plt.xlabel('File Size')
        plt.ylabel('Average Time (seconds)')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'file_size_impact.png'))
        plt.close()

        # 3. Resource Usage Comparison
        plt.figure()
        resources = ['CPU Usage', 'Memory Usage (MB)', 'Time (s)']
        enc_metrics = [
            statistics.mean(metrics['encryption']['cpu']),
            statistics.mean(metrics['encryption']['memory']),
            statistics.mean(metrics['encryption']['time'])
        ]
        
        plt.bar(resources, enc_metrics, color=self.colors[0])
        plt.title('Resource Usage Metrics')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'resource_usage.png'))
        plt.close()

    def display_results(self, metrics):
        """Display comprehensive benchmark results"""
        print("\nCOMPREHENSIVE BENCHMARK RESULTS")
        print("=" * 60)
        
        # 1. Basic Performance
        print("\nBASIC PERFORMANCE:")
        if metrics['encryption']['time']:
            print(f"   Encryption Time: {statistics.mean(metrics['encryption']['time']):.2f}s")
            print(f"   Memory Usage: {statistics.mean(metrics['encryption']['memory']):.1f}MB")
            print(f"   CPU Usage: {statistics.mean(metrics['encryption']['cpu']):.1f}%")
        
        # 2. Access Control
        print("\nACCESS CONTROL RESULTS:")
        for user in self.users:
            if user in metrics['access_control']:
                successes = metrics['access_control'][user]['success']
                success_rate = sum(successes) / len(successes) * 100 if successes else 0
                avg_time = statistics.mean(metrics['access_control'][user]['time']) if metrics['access_control'][user]['time'] else 0
                print(f"   {user}:")
                print(f"      Success Rate: {success_rate:.1f}%")
                print(f"      Average Time: {avg_time:.2f}s")
        
        # 3. File Size Impact
        print("\nFILE SIZE IMPACT:")
        for size in self.file_sizes:
            if size in metrics['file_sizes']:
                avg_time = statistics.mean(metrics['file_sizes'][size]['time'])
                avg_memory = statistics.mean(metrics['file_sizes'][size]['memory'])
                print(f"   {size}:")
                print(f"      Processing Time: {avg_time:.2f}s")
                print(f"      Memory Usage: {avg_memory:.1f}MB")
    
    def save_results(self, metrics, all_results):
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        summary = {
            'timestamp': timestamp,
            'iterations': self.iterations,
            'summary': {
                'encryption': {
                    'mean_time': statistics.mean(metrics['encryption']['time']) if metrics['encryption']['time'] else 0,
                    'success_rate': sum(metrics['encryption']['success']) / len(metrics['encryption']['success']) if metrics['encryption']['success'] else 0
                },
                'access_control': {
                    user: {
                        'mean_time': statistics.mean(metrics['access_control'][user]['time']) if metrics['access_control'][user]['time'] else 0,
                        'success_rate': sum(metrics['access_control'][user]['success']) / len(metrics['access_control'][user]['success']) if metrics['access_control'][user]['success'] else 0
                    } for user in self.users
                },
                'file_sizes': {
                    size: {
                        'mean_time': statistics.mean(metrics['file_sizes'][size]['time']) if metrics['file_sizes'][size]['time'] else 0,
                        'success_rate': sum(metrics['file_sizes'][size]['success']) / len(metrics['file_sizes'][size]['success']) if metrics['file_sizes'][size]['success'] else 0
                    } for size in self.file_sizes
                }
            },
            'detailed_results': all_results
        }
        
        os.makedirs('benchmark_results', exist_ok=True)
        with open(f'benchmark_results/martzk_benchmark_{timestamp}.json', 'w') as f:
            json.dump(summary, f, indent=2)

def main():
    """Main benchmark execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MARTZK System Benchmark")
    parser.add_argument('-i', '--iterations', type=int, default=100,
                       help='Number of benchmark iterations (default: 100)')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick benchmark with 10 iterations')
    
    args = parser.parse_args()
    iterations = 10 if args.quick else args.iterations
    
    print("MARTZK System Benchmark")
    print(f"Running {iterations} iterations")
    print("Measuring: Encryption and Decryption Performance")
    print("-" * 60)
    
    benchmark = MARTZKBenchmark(iterations=iterations)
    
    try:
        benchmark.run_benchmark()
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nBenchmark failed: {e}")
    
    print("\nBenchmark completed!")

if __name__ == "__main__":
    main() 