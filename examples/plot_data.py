import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import sys

def create_plots(input_file, output_dir):
    """
    Reads simulation data from a text file and generates a plot for each
    numeric column against the 'Tick' column.
    """
    # --- 1. Validate Input and Prepare Output Directory ---
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at '{input_file}'")
        sys.exit(1)
        
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Plots will be saved in the '{output_dir}/' directory.")

    # --- 2. Load the Data using Pandas (same logic as before) ---
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
            header_line = lines[0].strip()
        
        column_names = [h.strip() for h in header_line.lstrip(',').split(',')]
        
        df = pd.read_csv(
            input_file,
            comment='#',
            skiprows=1,
            header=None,
            names=column_names,
            skipinitialspace=True
        )
    except Exception as e:
        print(f"Error parsing data from '{input_file}': {e}")
        sys.exit(1)

    if df.empty:
        print("Warning: The data file is empty. No plots will be generated.")
        return
    print (df.head()) # Show the first few rows of the data for verification
    # --- 3. Identify Columns to Plot ---
    # We want to plot every column against 'Tick', except 'Tick' itself and 'Type'.
    x_axis_col = 'tick'
    columns_to_plot = [col for col in df.columns if col not in [x_axis_col, 'Type']]
    
    print(f"Found {len(columns_to_plot)} columns to plot against '{x_axis_col}'.")

    # --- 4. Generate and Save a Plot for Each Column ---
    for y_axis_col in columns_to_plot:
        
        # Ensure the column contains numeric data before trying to plot
        if not pd.api.types.is_numeric_dtype(df[y_axis_col]):
            print(f"  - Skipping non-numeric column: '{y_axis_col}'")
            continue

        # Set a nice visual style for the plots
        sns.set_theme(style="darkgrid")
        
        # Create a new figure for each plot to prevent them from overlapping
        plt.figure(figsize=(12, 7))
        
        # Create the line plot
        plot = sns.lineplot(data=df, x=x_axis_col, y=y_axis_col)
        
        # Set titles and labels for clarity
        plt.title(f'{y_axis_col} vs. {x_axis_col}', fontsize=16)
        plt.xlabel(x_axis_col, fontsize=12)
        plt.ylabel(y_axis_col, fontsize=12)
        
        # Define a clean filename for the output image
        output_filename = f"plot_{y_axis_col}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save the figure to a file and close it to free up memory
        plt.savefig(output_path)
        plt.close()
        
        print(f"  - Saved plot for '{y_axis_col}' to '{output_path}'")

def main():
    """Main function to parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate plots from a simulation log text file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input text file (e.g., simulation_log.txt)."
    )
    
    parser.add_argument(
        "-d", "--directory",
        default="plots", # Default output directory name
        help="Directory where the output plot images will be saved."
    )
    
    args = parser.parse_args()
    create_plots(args.input_file, args.directory)

if __name__ == "__main__":
    main()