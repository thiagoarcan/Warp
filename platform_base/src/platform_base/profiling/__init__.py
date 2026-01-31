"""
Profiling module for Platform Base v2.0

Provides automatic profiling and performance monitoring
conforme PRD seção 10.6
"""

from .decorators import memory_profile, profile
from .profiler import AutoProfiler, Profiler
from .reports import ProfilingReport, generate_html_report


__all__ = [
    "AutoProfiler",
    "Profiler",
    "ProfilingReport",
    "generate_html_report",
    "memory_profile",
    "profile",
]
