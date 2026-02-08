"""Verify Tunisia-specific features."""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import TunisianTradingCalendar, logger

def verify_calendar():
    """Verify calendar features."""
    logger.info("=" * 60)
    logger.info("Verifying Tunisia-Specific Features")
    logger.info("=" * 60)
    
    calendar = TunisianTradingCalendar()
    
    # Check fixed holidays
    logger.info("\nChecking Fixed Holidays:")
    holidays_2024 = [
        datetime(2024, 1, 1),   # New Year
        datetime(2024, 3, 20),  # Independence
        datetime(2024, 4, 9),   # Martyrs
        datetime(2024, 5, 1),   # Labour
        datetime(2024, 7, 25),  # Republic
        datetime(2024, 8, 13),  # Women
        datetime(2024, 10, 15)  # Evacuation
    ]
    
    for dt in holidays_2024:
        is_trading = calendar.is_trading_day(dt)
        status = "Holiday (Correct)" if not is_trading else "Error: Should be holiday"
        logger.info(f"  {dt.strftime('%Y-%m-%d')}: {status}")
        
    # Check Ramadan 2024 (approx March 11 - April 9)
    logger.info("\nChecking Ramadan Trading Hours:")
    ramadan_date = datetime(2024, 3, 15)  # Definitely in Ramadan
    normal_date = datetime(2024, 6, 15)   # Definitely not
    
    r_start, r_end = calendar.get_trading_hours(ramadan_date)
    n_start, n_end = calendar.get_trading_hours(normal_date)
    
    logger.info(f"  Ramadan ({ramadan_date.strftime('%Y-%m-%d')}): {r_start}-{r_end}")
    logger.info(f"  Normal  ({normal_date.strftime('%Y-%m-%d')}): {n_start}-{n_end}")
    
    if r_start == "10:00" and r_end == "12:30":
        logger.info("  ✓ Ramadan hours correct")
    else:
        logger.error("  ✗ Ramadan hours incorrect")
        
    logger.info("\n" + "=" * 60)
    logger.info("✓ Verification Complete!")
    logger.info("=" * 60)

if __name__ == "__main__":
    verify_calendar()
