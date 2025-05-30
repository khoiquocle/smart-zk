#!/usr/bin/env python3
"""
MARTZK Benchmark Results Visualization
Generates charts and visualizations from benchmark data
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class BenchmarkVisualizer:
    def __init__(self, results_dir="benchmark_results", charts_dir="benchmark_charts"):
        self.results_dir = results_dir
        self.charts_dir = charts_dir
        os.makedirs(charts_dir, exist_ok=True)
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def load_latest_results(self):
        """Load the most recent benchmark results file"""
        result_files = [f for f in os.listdir(self.results_dir) if f.endswith('.json')]
        if not result_files:
            raise FileNotFoundError("No benchmark results found")
            
        latest_file = max(result_files, key=lambda x: os.path.getctime(os.path.join(self.results_dir, x)))
        with open(os.path.join(self.results_dir, latest_file)) as f:
            return json.load(f)
    
    def plot_operation_times(self, data):
        """Plot average operation times"""
        operations = ['encryption', 'decryption', 'zksnark', 'end_to_end']
        times = [data['summary_metrics'][op]['mean_time'] for op in operations]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(operations, times)
        plt.title('Average Operation Times')
        plt.ylabel('Time (seconds)')
        plt.xticks(rotation=45)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}s',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'operation_times.png'))
        plt.close()
    
    def plot_success_rates(self, data):
        """Plot operation success rates"""
        operations = ['encryption', 'decryption', 'zksnark']
        rates = [data['summary_metrics'][op]['success_rate'] * 100 for op in operations]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(operations, rates)
        plt.title('Operation Success Rates')
        plt.ylabel('Success Rate (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=45)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'success_rates.png'))
        plt.close()
    
    def plot_file_size_impact(self, data):
        """Plot impact of file size on encryption/decryption time"""
        detailed = data['detailed_results']
        
        # Extract file sizes and times
        sizes = []
        enc_times = []
        dec_times = []
        
        for result in detailed:
            if 'encryption' in result and result['encryption']['success']:
                sizes.append(result['encryption']['file_size'] / 1024)  # Convert to KB
                enc_times.append(result['encryption']['time'])
            if 'decryption' in result and result['decryption']['success']:
                dec_times.append(result['decryption']['time'])
        
        plt.figure(figsize=(10, 6))
        plt.scatter(sizes, enc_times, alpha=0.5, label='Encryption')
        if dec_times:
            plt.scatter(sizes[:len(dec_times)], dec_times, alpha=0.5, label='Decryption')
        
        plt.title('File Size Impact on Processing Time')
        plt.xlabel('File Size (KB)')
        plt.ylabel('Time (seconds)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'file_size_impact.png'))
        plt.close()
    
    def plot_memory_usage(self, data):
        """Plot memory usage distribution"""
        detailed = data['detailed_results']
        memory_deltas = []
        
        for result in detailed:
            if 'encryption' in result and result['encryption']['success']:
                memory_deltas.append(result['encryption']['memory_delta'])
        
        plt.figure(figsize=(10, 6))
        sns.histplot(memory_deltas, bins=20)
        plt.title('Memory Usage Distribution')
        plt.xlabel('Memory Delta (MB)')
        plt.ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.charts_dir, 'memory_usage.png'))
        plt.close()
    
    def generate_all_charts(self):
        """Generate all benchmark visualization charts"""
        print("🎨 Generating benchmark visualization charts...")
        
        try:
            data = self.load_latest_results()
            
            print("📊 Plotting operation times...")
            self.plot_operation_times(data)
            
            print("📈 Plotting success rates...")
            self.plot_success_rates(data)
            
            print("📉 Plotting file size impact...")
            self.plot_file_size_impact(data)
            
            print("💾 Plotting memory usage...")
            self.plot_memory_usage(data)
            
            print(f"\n✅ Charts generated successfully in {self.charts_dir}/")
            
        except Exception as e:
            print(f"❌ Error generating charts: {e}")

def main():
    visualizer = BenchmarkVisualizer()
    visualizer.generate_all_charts()

if __name__ == "__main__":
    main() 