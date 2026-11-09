"""Structured logging for BVMT forecasting system."""

import sys
import logging
from pathlib import Path

from src.utils.config import config

try:
    from loguru import logger

    def setup_logger() -> None:
        """Configure loguru logger with settings from config."""
        logger.remove()
        log_level = config.get('logging.level', 'INFO')
        log_format = config.get('logging.format')
        rotation = config.get('logging.rotation', '100 MB')
        retention = config.get('logging.retention', '30 days')
        
        logger.add(
            sys.stderr,
            format=log_format,
            level=log_level,
            colorize=True
        )
        
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

    setup_logger()

except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s - %(message)s"
    )
    logger = logging.getLogger("bvmt")

    def setup_logger() -> None:
        pass
