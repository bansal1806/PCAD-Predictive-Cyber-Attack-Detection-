import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_distribution_pie():
    data_path = 'data/processed/aggregated_data.csv'
    output_dir = 'models'
    
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}")
        return

    # Load data
    df = pd.read_csv(data_path)
    
    if 'target' not in df.columns:
        print("Target column not found in data.")
        return
        
    counts = df['target'].value_counts()
    labels = ['Normal Traffic', 'Attack Traffic'] if 0 in counts and 1 in counts else counts.index.astype(str)
    
    # Sort to ensure consistency (0: Normal, 1: Attack)
    if 0 in counts.index and 1 in counts.index:
        plot_counts = [counts[0], counts[1]]
        plot_labels = ['Normal Traffic', 'Attack Traffic']
    else:
        plot_counts = counts.values
        plot_labels = counts.index.astype(str)

    # Styling
    colors = ['#00F2EA', '#FF3B3B'] # Cyan and Red (Cyber Aesthetic)
    explode = (0, 0.1) # Explode the Attack slice
    
    plt.figure(figsize=(10, 8), facecolor='none')
    plt.pie(
        plot_counts, 
        labels=plot_labels, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        explode=explode,
        textprops={'color':"black", 'weight':'bold', 'fontsize': 12},
        shadow=True
    )
    
    plt.title('PCAD Sentinel: Data Distribution (Normal vs Attack)', fontsize=15, pad=20, weight='bold')
    
    # Save Plot
    plot_path = os.path.join(output_dir, 'data_distribution_pie.png')
    plt.savefig(plot_path, transparent=False, dpi=300)
    plt.close()
    
    print(f"Distribution counts: {counts.to_dict()}")
    print(f"Pie chart saved to: {plot_path}")

if __name__ == "__main__":
    generate_distribution_pie()
