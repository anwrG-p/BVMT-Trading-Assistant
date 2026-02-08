
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import logger, config

def export_features_to_csv():
    """Export features.parquet to CSV."""
    processed_dir = Path(config.get('data.processed_dir'))
    parquet_path = processed_dir / 'features.parquet'
    csv_path = processed_dir / 'features.csv'
    
    if not parquet_path.exists():
        logger.error(f"Features file not found: {parquet_path}")
        return
    
    logger.info(f"Reading {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    
    logger.info(f"Exporting to {csv_path}...")
    df.to_csv(csv_path, index=False)
    
    logger.info(f"✓ Export complete: {csv_path}")
    logger.info(f"  - Rows: {len(df)}")
    logger.info(f"  - Columns: {len(df.columns)}")

if __name__ == "__main__":
    export_features_to_csv()
