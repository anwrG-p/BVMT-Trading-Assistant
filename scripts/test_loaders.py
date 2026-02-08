"""Test script for data loaders - validates all data files can be loaded."""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FileLoaderFactory, DataQualityValidator
from src.utils import logger, config
from tqdm import tqdm


def test_stock_quotation_loaders():
    """Test loading all stock quotation files."""
    logger.info("=" * 60)
    logger.info("Testing Stock Quotation Loaders")
    logger.info("=" * 60)
    
    stock_dir = Path(config.get('data.stock_quotation_dir'))
    files = sorted(stock_dir.glob('*.txt')) + sorted(stock_dir.glob('*.csv'))
    
    results = []
    
    for file_path in tqdm(files, desc="Loading stock files"):
        try:
            loader = FileLoaderFactory.create_loader(file_path)
            df = loader.load()
            
            results.append({
                'file': file_path.name,
                'status': 'SUCCESS',
                'rows': len(df),
                'columns': len(df.columns),
                'symbols': df['symbol'].nunique() if 'symbol' in df.columns else 0,
                'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A'
            })
            
            logger.info(f"✓ {file_path.name}: {len(df)} rows, {df['symbol'].nunique() if 'symbol' in df.columns else 0} symbols")
            
        except Exception as e:
            results.append({
                'file': file_path.name,
                'status': 'FAILED',
                'error': str(e)
            })
            logger.error(f"✗ {file_path.name}: {str(e)}")
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    logger.info(f"\nStock Quotation Summary: {success_count}/{len(results)} files loaded successfully")
    
    return results


def test_dividend_loaders():
    """Test loading all dividend files."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Dividend Loaders")
    logger.info("=" * 60)
    
    div_dir = Path(config.get('data.dividends_dir'))
    files = sorted(div_dir.glob('*.xls')) + sorted(div_dir.glob('*.xlsx'))
    
    results = []
    
    for file_path in tqdm(files, desc="Loading dividend files"):
        try:
            loader = FileLoaderFactory.create_loader(file_path)
            df = loader.load()
            
            results.append({
                'file': file_path.name,
                'status': 'SUCCESS',
                'rows': len(df),
                'columns': len(df.columns)
            })
            
            logger.info(f"✓ {file_path.name}: {len(df)} rows")
            
        except Exception as e:
            results.append({
                'file': file_path.name,
                'status': 'FAILED',
                'error': str(e)
            })
            logger.error(f"✗ {file_path.name}: {str(e)}")
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    logger.info(f"\nDividend Summary: {success_count}/{len(results)} files loaded successfully")
    
    return results


def test_index_loaders():
    """Test loading all index files."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Index Loaders")
    logger.info("=" * 60)
    
    index_dir = Path(config.get('data.index_dir'))
    files = sorted(index_dir.glob('histo_indice*.txt')) + sorted(index_dir.glob('histo_indice*.csv'))
    
    results = []
    
    for file_path in tqdm(files, desc="Loading index files"):
        try:
            loader = FileLoaderFactory.create_loader(file_path)
            df = loader.load()
            
            results.append({
                'file': file_path.name,
                'status': 'SUCCESS',
                'rows': len(df),
                'columns': len(df.columns)
            })
            
            logger.info(f"✓ {file_path.name}: {len(df)} rows")
            
        except Exception as e:
            results.append({
                'file': file_path.name,
                'status': 'FAILED',
                'error': str(e)
            })
            logger.error(f"✗ {file_path.name}: {str(e)}")
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    logger.info(f"\nIndex Summary: {success_count}/{len(results)} files loaded successfully")
    
    return results


def test_data_quality():
    """Test data quality validation on a sample file."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Data Quality Validation")
    logger.info("=" * 60)
    
    # Load a sample file (2025 data)
    stock_dir = Path(config.get('data.stock_quotation_dir'))
    sample_file = stock_dir / 'histo_cotation_2025.csv'
    
    if sample_file.exists():
        loader = FileLoaderFactory.create_loader(sample_file)
        df = loader.load()
        
        # Run validation
        validator = DataQualityValidator(df, name="histo_cotation_2025")
        report = validator.validate_all()
        
        # Save report
        report_dir = Path(config.get('data.reports_dir'))
        report_dir.mkdir(parents=True, exist_ok=True)
        validator.save_report(report_dir / 'sample_validation_report.json')
        
        logger.info(f"✓ Validation complete: {len(report['issues'])} issues found")
        logger.info(f"  - Duplicates: {report['summary']['duplicates']}")
        logger.info(f"  - Outliers: {report['summary']['outliers']}")
        logger.info(f"  - Missing values: {report['summary']['missing_values']}")
        logger.info(f"  - Date gaps: {report['summary']['date_gaps']}")
        logger.info(f"  - Zero volume days: {report['summary']['zero_volume_days']}")
    else:
        logger.warning(f"Sample file not found: {sample_file}")


if __name__ == '__main__':
    logger.info("Starting Data Loader Tests")
    logger.info("=" * 60)
    
    # Test all loaders
    stock_results = test_stock_quotation_loaders()
    dividend_results = test_dividend_loaders()
    index_results = test_index_loaders()
    
    # Test data quality
    test_data_quality()
    
    # Final summary
    total_files = len(stock_results) + len(dividend_results) + len(index_results)
    total_success = (
        sum(1 for r in stock_results if r['status'] == 'SUCCESS') +
        sum(1 for r in dividend_results if r['status'] == 'SUCCESS') +
        sum(1 for r in index_results if r['status'] == 'SUCCESS')
    )
    
    logger.info("\n" + "=" * 60)
    logger.info(f"FINAL SUMMARY: {total_success}/{total_files} files loaded successfully")
    logger.info("=" * 60)
    
    if total_success == total_files:
        logger.info("✓ All tests passed!")
        sys.exit(0)
    else:
        logger.error(f"✗ {total_files - total_success} files failed to load")
        sys.exit(1)
