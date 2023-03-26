import importlib.metadata

from .problem import (
    Problem,
    UnboundedException,
    UndefinedException,
    InfeasibleException,
    NotSolvedException,
)
from .coverage import Coverage

__all__ = [
    "Problem",
    "UnboundedException",
    "UndefinedException",
    "InfeasibleException",
    "NotSolvedException",
    "Coverage",
]

__version__ = importlib.metadata.version(__package__ or __name__)
