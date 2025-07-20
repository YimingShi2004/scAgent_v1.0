"""
Command-line interface for scAgent.
"""

from .main import main
from .commands import (
    test_connection,
    analyze_schema,
    analyze_geo,
    analyze_sra,
    find_eqtl_data,
    clean_data
)

__all__ = [
    "main",
    "test_connection",
    "analyze_schema", 
    "analyze_geo",
    "analyze_sra",
    "find_eqtl_data",
    "clean_data"
] 