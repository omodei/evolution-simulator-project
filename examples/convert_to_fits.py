import pandas as pd
from astropy.table import Table
import argparse
import os
import sys

def convert_txt_to_fits(input_file, output_file, overwrite=False):
    """
    Reads a specially formatted text file, converts it to an Astropy Table,
    and saves it as a FITS file.
    """
    # --- 1. Validate Input File ---
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at '{input_file}'")
        sys.exit(1) # Exit with an error code

    # --- 2. Manually Read and Construct the Header ---
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
            # The header names are on the second line (index 1)
            if len(lines) < 2:
                print(f"Error: File '{input_file}' is too short to be a valid data file.")
                sys.exit(1)
            
            # The header names are on the second line (index 1)
            header_line = lines[0].strip()
            
        # The first two column names are implied by the data structure.
        column_names =[h.strip() for h in header_line.lstrip(',').split(',')]
    except Exception as e:
        print(f"Error reading header from '{input_file}': {e}")
        sys.exit(1)

    # --- 3. Use Pandas to Read the CSV Data ---
    try:
        df = pd.read_csv(
            input_file,
            comment='#',            # Ignore lines starting with '#'
            skiprows=1,             # Skip the comment and header lines
            header=None,            # No header in the data part
            names=column_names,     # Provide our constructed column names
            skipinitialspace=True   # Handle extra spaces after commas
        )
    except Exception as e:
        print(f"Error parsing data with Pandas: {e}")
        sys.exit(1)

    # --- 4. Convert to Astropy Table and Save to FITS ---
    print(f"Successfully parsed {len(df)} data rows.")
    astro_table = Table.from_pandas(df)
    
    try:
        # The overwrite flag from argparse is passed directly here
        astro_table.write(output_file, format='fits', overwrite=overwrite)
        print(f"Successfully converted '{input_file}' to '{output_file}'")
    except Exception as e:
        # This will catch errors, e.g., if the file exists and overwrite is False
        print(f"\nError writing to FITS file: {e}")
        print("Hint: If the output file already exists, use the --overwrite flag.")
        sys.exit(1)

def main():
    """Main function to parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert a simulation log text file to a FITS file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required argument for the input file
    parser.add_argument(
        "input_file",
        help="Path to the input text file (e.g., simulation_log.txt)."
    )
    
    # Optional argument for the output file
    parser.add_argument(
        "-o", "--output",
        help="Path for the output FITS file. If not provided, it defaults to the "
             "input filename with a .fits extension."
    )
    
    # Optional flag to allow overwriting the output file
    parser.add_argument(
        "--overwrite",
        action="store_true", # Makes it a flag: if present, sets value to True
        help="Overwrite the output file if it already exists."
    )
    
    args = parser.parse_args()
    
    # --- Determine Output Filename ---
    # If an output file is specified, use it.
    if args.output:
        output_filename = args.output
    # Otherwise, generate a default name (e.g., 'data.txt' -> 'data.fits')
    else:
        base_name = os.path.splitext(args.input_file)[0]
        output_filename = base_name + '.fits'
        
    # --- Call the main conversion function ---
    convert_txt_to_fits(args.input_file, output_filename, args.overwrite)


if __name__ == "__main__":
    main()