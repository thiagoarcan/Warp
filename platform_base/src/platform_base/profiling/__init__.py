"""
Profiling module for Platform Base v2.0

Provides automatic profiling and performance monitoring
conforme PRD seção 10.6
"""

from .profiler import AutoProfiler, Profiler
from .decorators import profile, memory_profile
from .reports import ProfilingReport, generate_html_report

__all__ = [
    "AutoProfiler",
    "Profiler", 
    "profile",
    "memory_profile",
    "ProfilingReport",
    "generate_html_report"
]