"""Custom exceptions for BVMT forecasting system."""


class BVMTException(Exception):
    """Base exception for BVMT forecasting system."""
    pass


class DataLoadError(BVMTException):
    """Raised when data loading fails."""
    pass


class ValidationError(BVMTException):
    """Raised when data validation fails."""
    pass


class FeatureEngineeringError(BVMTException):
    """Raised when feature engineering fails."""
    pass


class ModelError(BVMTException):
    """Raised when model training/prediction fails."""
    pass


class PredictionError(BVMTException):
    """Raised when prediction fails."""
    pass


class ConfigurationError(BVMTException):
    """Raised when configuration is invalid."""
    pass
