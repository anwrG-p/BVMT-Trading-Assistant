"""Data pipeline collectors for BVMT Trading Assistant."""

from .bct_collector import BCTCollector
from .tustex_collector import TustexCollector

# InvestingCollector requires playwright-stealth, make it optional
try:
    from .investing_collector import InvestingCollector
    __all__ = ["BCTCollector", "InvestingCollector", "TustexCollector"]
except ImportError:
    __all__ = ["BCTCollector", "TustexCollector"]
