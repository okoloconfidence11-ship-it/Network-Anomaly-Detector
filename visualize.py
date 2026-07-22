import matplotlib.pyplot as plt
import pandas as pd

def plot_distribution(file_path):
    try:
        data = pd.read_csv(file_path)
        label_column = data.columns[-1]
        counts = data[label_column].value_counts()

        plt.figure(figsize=(10, 6))
        counts.plot(kind= 'bar', color=['skyblue', 'salmon', 'lightgreen', 'orange'])

        plt.title(f"Network Traffic Distribution", fontsize=16, fontweight='bold')
        plt.xlabel("Traffic Type (Class)", fontsize=12)
        plt.ylabel("Number of Occurences", fontsize=12)
        plt.xticks(rotation=45, fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)       
       
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print(f"Error: Could not find '{file_path}'. Make sure the file is in the folder.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
if __name__ == "__main__":
    plot_distribution("data/train.csv")
    
