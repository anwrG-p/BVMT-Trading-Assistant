"""Tunisia-specific trading calendar and holidays."""

import pandas as pd
from datetime import date, datetime
import hijri_converter
from typing import List, Optional

class TunisianTradingCalendar:
    """Calendar for BVMT trading days and holidays."""
    
    def __init__(self):
        # Fixed holidays (Month, Day)
        self.fixed_holidays = [
            (1, 1),   # New Year's Day
            (1, 14),  # Revolution and Youth Day
            (3, 20),  # Independence Day
            (4, 9),   # Martyrs' Day
            (5, 1),   # Labour Day
            (7, 25),  # Republic Day
            (8, 13),  # Women's Day
            (10, 15), # Evacuation Day
        ]
    
    def is_trading_day(self, dt: datetime) -> bool:
        """Check if date is a trading day."""
        # Check weekends (Saturday=5, Sunday=6)
        if dt.weekday() >= 5:
            return False
            
        # Check fixed holidays
        if (dt.month, dt.day) in self.fixed_holidays:
            return False
            
        # Note: Variable Islamic holidays (Eid, Mouled) need manual updates
        # or complex calculation. For now, we rely on data presence for historical
        # checks, this is mostly for future schedule validaton.
        
        return True
        
    def get_trading_hours(self, dt: datetime) -> tuple:
        """Get trading hours for a specific date (handling Ramadan)."""
        # Default hours
        start = "09:00"
        end = "14:10"
        
        # Check if Ramadan
        hijri = hijri_converter.convert.Gregorian(dt.year, dt.month, dt.day).to_hijri()
        if hijri.month == 9:  # Ramadan
            start = "10:00"
            end = "12:30"
            
        return start, end

    def get_ramadan_dates(self, year: int) -> tuple:
        """Get start and end dates of Ramadan for a Gregorian year."""
        # This is an approximation as lunar visibility varies
        # Using hijri-converter to find the range
        start_date = None
        end_date = None
        
        d = date(year, 1, 1)
        while d.year == year:
            h = hijri_converter.convert.Gregorian(d.year, d.month, d.day).to_hijri()
            if h.month == 9:
                if start_date is None:
                    start_date = d
                end_date = d
            d += pd.Timedelta(days=1)
            
        return start_date, end_date
