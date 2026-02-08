"""Structured logging for BVMT forecasting system."""

import sys
from pathlib import Path
from loguru import logger

from src.utils.config import config


def setup_logger() -> None:
    """Configure loguru logger with settings from config."""
    
    # Remove default handler
    logger.remove()
    
    # Get config values
    log_level = config.get('logging.level', 'INFO')
    log_format = config.get('logging.format')
    rotation = config.get('logging.rotation', '100 MB')
    retention = config.get('logging.retention', '30 days')
    
    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "bvmt_{time:YYYY-MM-DD}.log",
        format=log_format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression="zip"
    )
    
    logger.info(f"Logger initialized with level: {log_level}")


# Initialize logger on import
setup_logger()
