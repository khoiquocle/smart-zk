import matplotlib.pyplot as plt
import json
import numpy as np

# Load JSON data
with open('benchmark_data/data.json', 'r') as f:
    data = json.load(f)
# quockhoi802@gmail.com

x = data['x']
y1 = data['y1']
y2 = data['y2']

# Set figure size and DPI
plt.figure(figsize=(8, 5), dpi=100)

# Bar width
width = 0.2

# Positions of bars
x_pos = np.arange(len(x))

# Plot bars side by side
plt.bar(x_pos - width/2, y1, width=width, color='royalblue', label='Users over Time per minute')
plt.bar(x_pos + width/2, y2, width=width, color='orange', label='Performance')

# Set X-axis labels
plt.xticks(x_pos, x)

# Titles and labels
plt.title('Bar Chart Example', fontsize=16, fontweight='bold', color='black')
plt.xlabel('X Users', fontsize=12, color='black', fontweight='bold')
plt.ylabel('Y Time', fontsize=12, color='black', fontweight='bold')

# Add legend
plt.legend(loc='upper right')

# Layout and save
plt.tight_layout()
plt.savefig('test.png', dpi=300, bbox_inches='tight')
plt.show()
