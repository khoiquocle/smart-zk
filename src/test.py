import matplotlib.pyplot as plt
import json
# Data


with open('benchmark_data/data.json', 'r') as f:
    data = json.load(f)

x = data['x']
y1 = data['y1']
y2 = data['y2']

# Set figure size and DPI
plt.figure(figsize=(8, 5), dpi=100)

# Plot with custom style
plt.bar(x, y1, 
         color='royalblue', 
         linewidth=2.5, 
         linestyle='-', 
         marker='.', 
         markersize=8,
         markerfacecolor='orange',
         label='Users over Time per minute')
plt.bar(x, y2, 
         color='orange', 
         linewidth=2.5, 
         linestyle='-', 
         marker='.', 
         markersize=8,
         markerfacecolor='royalblue',
         label='Performance')

# Titles and labels with custom font sizes
plt.title('Line Chart Example', fontsize=16, fontweight='bold', color='black')
plt.xlabel('X Users', fontsize=12, color='black', fontweight='bold')
plt.ylabel('Y Time', fontsize=12 ,fontweight='bold', color='black')

# Grid with style
# plt.grid(True, linestyle=':', color='gray', alpha=0.7)

# Add legend
plt.legend(loc='upper right')      # top-left
# plt.legend(loc='lower right')     # bottom-right


# Add padding and display
plt.tight_layout()
plt.savefig('test.png', dpi=300, bbox_inches='tight')
plt.show()
