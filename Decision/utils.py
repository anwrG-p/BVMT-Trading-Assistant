import pandas as pd
import os
import glob

def load_tunisian_data(dataset_path, tickers, start_year=2020):
    """
    Loads historical data for specific Tunisian tickers from CSV files in the dataset folder.
    
    Args:
        dataset_path (str): Path to the folder containing 'histo_cotation_*.csv' files.
        tickers (list): List of ticker names (from 'VALEUR' column) to extract.
        start_year (int): Filter data starting from this year.
        
    Returns:
        pd.DataFrame: A DataFrame where columns are Tickers and index is Date, containing 'CLOTURE' prices.
    """
    all_data = []
    
    # Pattern to match the CSV files
    search_pattern = os.path.join(dataset_path, "histo_cotation_*.csv")
    files = glob.glob(search_pattern)
    
    print(f"Found {len(files)} data files in {dataset_path}")
    
    for file in files:
        try:
            # Read CSV - specific handling for Tunisian/French format
            # separator is ';', decimal might be ',' but usually in these specific dataset it might be '.' or ','
            # We will try reading as string first for safety or just standard pandas inference with sep=';'
            df = pd.read_csv(file, sep=';', encoding='latin-1', on_bad_lines='skip')
            
            # Normalize column names
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Clean string columns
            if 'VALEUR' not in df.columns:
                 continue
                 
            df['VALEUR'] = df['VALEUR'].astype(str).str.strip()
            
            # Filter for selected tickers
            df_filtered = df[df['VALEUR'].isin(tickers)].copy()
            
            if df_filtered.empty:
                continue
                
            # Parse Date
            # Format usually DD/MM/YYYY
            df_filtered['SEANCE'] = df_filtered['SEANCE'].astype(str).str.strip()
            df_filtered['Date'] = pd.to_datetime(df_filtered['SEANCE'], format='%d/%m/%Y', errors='coerce')
            
            # Clean and Convert Price
            # Handle potential comma decimals if present, distinct from thousands
            if df_filtered['CLOTURE'].dtype == object:
                df_filtered['CLOTURE'] = df_filtered['CLOTURE'].astype(str).str.strip().str.replace(',', '.', regex=False)
            
            df_filtered['CLOTURE'] = pd.to_numeric(df_filtered['CLOTURE'], errors='coerce')
            
            # Select relevant columns
            subset = df_filtered[['Date', 'VALEUR', 'CLOTURE']].dropna()
            all_data.append(subset)
            
        except Exception as e:
            print(f"Error reading {os.path.basename(file)}: {e}")
            
    if not all_data:
        print("No data found for the specified tickers.")
        return pd.DataFrame()
        
    # Combine all years
    full_df = pd.concat(all_data, ignore_index=True)
    
    # Filter by start year
    full_df = full_df[full_df['Date'].dt.year >= start_year]
    
    # Remove obvious duplicates
    full_df = full_df.drop_duplicates(subset=['Date', 'VALEUR'])
    
    # Pivot to create the desired structure: Index=Date, Columns=Tickers, Values=Close
    # aggfunc='mean' handles any remaining duplicates safely
    price_matrix = full_df.pivot_table(index='Date', columns='VALEUR', values='CLOTURE', aggfunc='mean')
    
    # Sort index
    price_matrix = price_matrix.sort_index()
    
    # Propagate last valid observation forward (handling missing trading days for some stocks)
    price_matrix = price_matrix.ffill()
    
    return price_matrix

if __name__ == "__main__":
    # Test block
    test_path = r"C:\Users\lenovo\Desktop\IHEC CODE 2.0\Dataset"
    test_tickers = ['SFBT', 'BIAT', 'BNA']
    print(f"Testing loader with {test_tickers}...")
    
    df = load_tunisian_data(test_path, test_tickers)
    print("\nResult Head:")
    print(df.head())
    print("\nResult Info:")
    print(df.info())
