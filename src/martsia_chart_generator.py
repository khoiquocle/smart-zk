#!/usr/bin/env python3
"""
MARTSIA Benchmark Chart Generator
Creates comprehensive visualization charts from benchmark results
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

def setup_chart_style():
    """Setup matplotlib style for professional charts"""
    styles_to_try = ['seaborn-v0_8', 'seaborn', 'ggplot', 'default']
    
    for style in styles_to_try:
        try:
            plt.style.use(style)
            print(f"[INFO] Using matplotlib style: {style}")
            break
        except OSError:
            continue
    
    # Set global font sizes for better readability
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 11,
        'figure.titlesize': 16
    })

def create_maabe_performance_chart(output_dir):
    """Create MA-ABE operations performance chart"""
    # Data from benchmark results
    operations = ['Setup', 'Keygen', 'Encrypt', 'Decrypt']
    mean_times = [0.440, 0.085, 0.125, 0.101]
    std_devs = [0.003, 0.002, 0.009, 0.006]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart with error bars
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    bars = ax.bar(operations, mean_times, yerr=std_devs, 
                  capsize=5, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Customize chart
    ax.set_title('MA-ABE Operations Performance Analysis', fontweight='bold', pad=20)
    ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
    ax.set_xlabel('MA-ABE Operations', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar, mean_val, std_val in zip(bars, mean_times, std_devs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std_val + 0.01,
                f'{mean_val:.3f}s\n+/- {std_val:.3f}s',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Set y-axis limit to accommodate labels
    ax.set_ylim(0, max(mean_times) + max(std_devs) + 0.1)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'maabe_performance.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] MA-ABE performance chart created")

def create_zksnark_performance_chart(output_dir):
    """Create zkSNARK operations performance chart"""
    # Data from benchmark results
    operations = ['Setup', 'Witness', 'Proof', 'Verify\nOffchain', 'Verify\nOnchain']
    
    # Data for each circuit type
    attribute_times = [0.742, 0.090, 0.343, 0.054, 0.259]
    attribute_stds = [0.003, 0.002, 0.008, 0.005, 0.050]
    
    policy_times = [1.240, 0.122, 0.540, 0.049, 0.260]
    policy_stds = [0.002, 0.003, 0.001, 0.002, 0.037]
    
    process_times = [1.746, 0.164, 0.843, 0.050, 0.295]
    process_stds = [0.012, 0.007, 0.004, 0.005, 0.040]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set positions for grouped bars
    x = np.arange(len(operations))
    width = 0.25
    
    # Create grouped bars
    bars1 = ax.bar(x - width, attribute_times, width, yerr=attribute_stds,
                   label='Attribute Circuit', capsize=4, color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x, policy_times, width, yerr=policy_stds,
                   label='Policy Circuit', capsize=4, color='#A23B72', alpha=0.8)
    bars3 = ax.bar(x + width, process_times, width, yerr=process_stds,
                   label='Process Circuit', capsize=4, color='#F18F01', alpha=0.8)
    
    # Customize chart
    ax.set_title('zkSNARK Operations Performance by Circuit Type', fontweight='bold', pad=20)
    ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
    ax.set_xlabel('zkSNARK Operations', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(operations)
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on bars (only for the tallest bars to avoid clutter)
    def add_labels(bars, times, stds):
        for bar, time_val, std_val in zip(bars, times, stds):
            if time_val > 0.5:  # Only label significant values
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + std_val + 0.05,
                        f'{time_val:.3f}s', ha='center', va='bottom', 
                        fontweight='bold', fontsize=9)
    
    add_labels(bars1, attribute_times, attribute_stds)
    add_labels(bars2, policy_times, policy_stds)
    add_labels(bars3, process_times, process_stds)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'zksnark_performance.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] zkSNARK performance chart created")

def create_scalability_charts(output_dir):
    """Create scalability analysis charts as separate images"""
    # Authority Scalability Data
    authorities = [1, 2, 3, 4, 5]
    auth_times = [0.338, 0.388, 0.438, 0.490, 0.536]
    
    # User Scalability Data
    users = [10, 50, 100, 200, 500]
    user_times = [0.050, 0.088, 0.137, 0.239, 0.537]
    
    # Authority Scalability Chart (separate image)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(authorities, auth_times, 'o-', color='#2E86AB', linewidth=3, 
             markersize=8, markerfacecolor='white', markeredgewidth=2)
    ax1.set_title('Authority Scalability Analysis', fontweight='bold', pad=15)
    ax1.set_xlabel('Number of Authorities', fontweight='bold')
    ax1.set_ylabel('Setup Time (seconds)', fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(authorities)
    
    # Add trend line for authority scalability
    z1 = np.polyfit(authorities, auth_times, 1)
    p1 = np.poly1d(z1)
    ax1.plot(authorities, p1(authorities), "--", alpha=0.8, color='red', linewidth=2)
    
    # Add data labels
    for x, y in zip(authorities, auth_times):
        ax1.annotate(f'{y:.3f}s', (x, y), textcoords="offset points", 
                     xytext=(0,10), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'authority_scalability.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Authority scalability chart created")
    
    # User Scalability Chart (separate image)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(users, user_times, 's-', color='#F18F01', linewidth=3, 
             markersize=8, markerfacecolor='white', markeredgewidth=2)
    ax2.set_title('User Scalability Analysis', fontweight='bold', pad=15)
    ax2.set_xlabel('Number of Users', fontweight='bold')
    ax2.set_ylabel('Processing Time (seconds)', fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xticks(users)
    
    # Add trend line for user scalability (logarithmic fit)
    log_users = np.log(users)
    z2 = np.polyfit(log_users, user_times, 1)
    user_trend = z2[0] * np.log(users) + z2[1]
    ax2.plot(users, user_trend, "--", alpha=0.8, color='red', linewidth=2)
    
    # Add data labels
    for x, y in zip(users, user_times):
        ax2.annotate(f'{y:.3f}s', (x, y), textcoords="offset points", 
                     xytext=(0,10), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'user_scalability.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] User scalability chart created")

def create_setup_comparison_chart(output_dir):
    """Create setup time comparison chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # MA-ABE vs zkSNARK Setup Times
    categories = ['MA-ABE\nSetup', 'zkSNARK\nAttribute', 'zkSNARK\nPolicy', 'zkSNARK\nProcess']
    setup_times = [0.440, 0.742, 1.240, 1.746]
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    bars = ax.bar(categories, setup_times, color=colors, alpha=0.8, edgecolor='black')
    ax.set_title('Setup Time Comparison', fontweight='bold', pad=20)
    ax.set_ylabel('Time (seconds)', fontweight='bold')
    ax.set_xlabel('Operation Types', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    for bar, time_val in zip(bars, setup_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{time_val:.3f}s', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'setup_comparison.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Setup comparison chart created")

def create_proof_verification_chart(output_dir):
    """Create proof generation vs verification chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Proof Generation vs Verification Times
    operations = ['Attribute', 'Policy', 'Process']
    proof_times = [0.343, 0.540, 0.843]
    verify_times = [0.054, 0.049, 0.050]  # Off-chain verification
    
    x = np.arange(len(operations))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, proof_times, width, label='Proof Generation', 
                    color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, verify_times, width, label='Verification (Off-chain)', 
                    color='#F18F01', alpha=0.8)
    
    ax.set_title('Proof Generation vs Verification Times', fontweight='bold', pad=20)
    ax.set_ylabel('Time (seconds)', fontweight='bold')
    ax.set_xlabel('Circuit Types', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(operations)
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, time_val in zip(bars1, proof_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{time_val:.3f}s', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    for bar, time_val in zip(bars2, verify_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.002,
                f'{time_val:.3f}s', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'proof_verification_comparison.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Proof vs verification chart created")

def create_authority_trend_chart(output_dir):
    """Create authority scalability trend chart with growth rate"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    authorities = [1, 2, 3, 4, 5, 6]
    auth_times = [0.338, 0.358, 0.438, 0.490, 0.536, 0.586]
    
    ax.plot(authorities, auth_times, 'o-', color='#2E86AB', linewidth=3, markersize=8)
    ax.set_title('Authority Scalability Trend Analysis', fontweight='bold', pad=20)
    ax.set_xlabel('Number of Authorities', fontweight='bold')
    ax.set_ylabel('Setup Time (seconds)', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(authorities)
    
    # Add trend line
    z = np.polyfit(authorities, auth_times, 1)
    p = np.poly1d(z)
    ax.plot(authorities, p(authorities), "--", alpha=0.8, color='red', linewidth=2, label='Linear Trend')
    
    # Calculate and display growth rate
    growth_rate = ((auth_times[-1] - auth_times[0]) / auth_times[0]) * 100
    ax.text(0.05, 0.95, f'Growth Rate: {growth_rate:.1f}%\nSlope: {z[0]:.3f}s per authority', 
             transform=ax.transAxes, fontweight='bold', 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.8))
    
    # Add data labels
    for x, y in zip(authorities, auth_times):
        ax.annotate(f'{y:.3f}s', (x, y), textcoords="offset points", 
                     xytext=(0,15), ha='center', fontweight='bold')
    
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'authority_trend_analysis.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Authority trend analysis chart created")

def create_user_complexity_chart(output_dir):
    """Create user scalability complexity analysis chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    users = [10, 50, 100, 200, 500]
    user_times = [0.050, 0.088, 0.137, 0.239, 0.537]
    
    ax.loglog(users, user_times, 's-', color='#F18F01', linewidth=3, markersize=8)
    ax.set_title('User Scalability Complexity Analysis', fontweight='bold', pad=20)
    ax.set_xlabel('Number of Users (log scale)', fontweight='bold')
    ax.set_ylabel('Processing Time (log scale)', fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add complexity estimation
    log_users = np.log10(users)
    log_times = np.log10(user_times)
    slope = np.polyfit(log_users, log_times, 1)[0]
    
    # Add trend line in log space
    trend_users = np.logspace(1, 2.7, 100)  # From 10 to ~500
    trend_times = 10**(slope * np.log10(trend_users) + np.polyfit(log_users, log_times, 1)[1])
    ax.plot(trend_users, trend_times, "--", alpha=0.8, color='red', linewidth=2, label='Power Law Fit')
    
    ax.text(0.05, 0.95, f'Complexity: O(n^{slope:.2f})\nAlgorithmic Classification: {"Sub-linear" if slope < 1 else "Linear" if slope == 1 else "Super-linear"}', 
             transform=ax.transAxes, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.8))
    
    # Add data labels
    for x, y in zip(users, user_times):
        ax.annotate(f'{y:.3f}s', (x, y), textcoords="offset points", 
                     xytext=(5,5), ha='left', fontweight='bold')
    
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'user_complexity_analysis.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] User complexity analysis chart created")

def create_comprehensive_comparison_chart(output_dir):
    """Create individual comparison charts (removed - replaced by separate functions above)"""
    # This function is now replaced by the individual chart functions above
    pass

def create_performance_summary_table(output_dir):
    """Create a performance summary table visualization"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare data for table
    table_data = [
        ['Operation Category', 'Operation', 'Mean Time (s)', 'Std Dev (s)', 'Performance Rating'],
        ['MA-ABE', 'Setup', '0.440', '0.003', 'Good'],
        ['MA-ABE', 'KeyGen', '0.085', '0.002', 'Excellent'],
        ['MA-ABE', 'Encrypt', '0.125', '0.009', 'Excellent'],
        ['MA-ABE', 'Decrypt', '0.101', '0.006', 'Excellent'],
        ['zkSNARK (Attr)', 'Setup', '0.742', '0.003', 'Good'],
        ['zkSNARK (Attr)', 'Proof Gen', '0.343', '0.008', 'Good'],
        ['zkSNARK (Attr)', 'Verify', '0.054', '0.005', 'Excellent'],
        ['zkSNARK (Policy)', 'Setup', '1.240', '0.002', 'Fair'],
        ['zkSNARK (Policy)', 'Proof Gen', '0.540', '0.001', 'Good'],
        ['zkSNARK (Process)', 'Setup', '1.746', '0.012', 'Fair'],
        ['zkSNARK (Process)', 'Proof Gen', '0.843', '0.004', 'Fair'],
    ]
    
    # Create table
    table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                     cellLoc='center', loc='center')
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Color code performance ratings
    for i in range(1, len(table_data)):
        rating = table_data[i][4]
        if rating == 'Excellent':
            table[(i, 4)].set_facecolor('#90EE90')  # Light green
        elif rating == 'Good':
            table[(i, 4)].set_facecolor('#FFFFE0')  # Light yellow
        elif rating == 'Fair':
            table[(i, 4)].set_facecolor('#FFB6C1')  # Light pink
    
    # Style header
    for j in range(5):
        table[(0, j)].set_facecolor('#4472C4')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    ax.set_title('MARTSIA Performance Summary Table', fontsize=16, fontweight='bold', pad=20)
    
    plt.savefig(os.path.join(output_dir, 'performance_summary_table.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Performance summary table created")

def generate_all_charts():
    """Generate all MARTSIA benchmark charts"""
    print("MARTSIA Benchmark Chart Generator")
    print("=" * 50)
    
    # Create output directory
    output_dir = "src/bench_marckchart"
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Charts will be saved to: {output_dir}")
    
    # Setup chart style
    setup_chart_style()
    
    # Generate all charts
    print("\n[INFO] Generating charts...")
    create_maabe_performance_chart(output_dir)
    create_zksnark_performance_chart(output_dir)
    create_scalability_charts(output_dir)
    create_setup_comparison_chart(output_dir)
    create_proof_verification_chart(output_dir)
    create_authority_trend_chart(output_dir)
    create_user_complexity_chart(output_dir)
    create_performance_summary_table(output_dir)
    
    # Create index file
    create_chart_index(output_dir)
    
    print(f"\n[SUCCESS] All charts generated successfully in {output_dir}/")
    print("Chart files created:")
    for file in os.listdir(output_dir):
        if file.endswith('.png'):
            print(f"  - {file}")

def create_chart_index(output_dir):
    """Create an HTML index file for easy viewing"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MARTSIA Benchmark Charts</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2E86AB; }}
        h2 {{ color: #A23B72; }}
        .chart {{ margin: 20px 0; text-align: center; }}
        .chart img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 8px; }}
        .timestamp {{ color: #666; font-style: italic; }}
    </style>
</head>
<body>
    <h1>SMARTZK Benchmark Analysis Charts</h1>
    <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>1. MA-ABE Performance Analysis</h2>
    <div class="chart">
        <img src="maabe_performance.png" alt="MA-ABE Performance">
    </div>
    
    <h2>2. zkSNARK Performance by Circuit Type</h2>
    <div class="chart">
        <img src="zksnark_performance.png" alt="zkSNARK Performance">
    </div>
    
    <h2>3. Authority Scalability Analysis</h2>
    <div class="chart">
        <img src="authority_scalability.png" alt="Authority Scalability">
    </div>
    
    <h2>4. User Scalability Analysis</h2>
    <div class="chart">
        <img src="user_scalability.png" alt="User Scalability">
    </div>
    
    <h2>5. Setup Time Comparison</h2>
    <div class="chart">
        <img src="setup_comparison.png" alt="Setup Time Comparison">
    </div>
    
    <h2>6. Proof Generation vs Verification</h2>
    <div class="chart">
        <img src="proof_verification_comparison.png" alt="Proof Generation vs Verification">
    </div>
    
    <h2>7. Authority Scalability Trend Analysis</h2>
    <div class="chart">
        <img src="authority_trend_analysis.png" alt="Authority Scalability Trend">
    </div>
    
    <h2>8. User Scalability Complexity Analysis</h2>
    <div class="chart">
        <img src="user_complexity_analysis.png" alt="User Scalability Complexity">
    </div>
    
    <h2>9. Performance Summary Table</h2>
    <div class="chart">
        <img src="performance_summary_table.png" alt="Performance Summary">
    </div>
</body>
</html>
"""
    
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(html_content)
    
    print("[OK] Chart index.html created")

if __name__ == "__main__":
    generate_all_charts() 