#!/usr/bin/env python3
"""
Script de validação de performance targets conforme PRD seção 10.6

Executa benchmarks dos targets definidos e gera relatório de conformidade.

Usage:
    python scripts/validate_performance.py [--config configs/platform.yaml] [--output performance_report.html]
"""

import argparse
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from platform_base.profiling.setup import setup_profiling_from_config
from platform_base.profiling.reports import generate_html_report, generate_json_report
from platform_base.processing.interpolation import interpolate
from platform_base.processing.calculus import derivative, integral
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def generate_test_data(n_points: int) -> tuple:
    """Gera dados de teste para benchmarks"""
    t = np.linspace(0, 10, n_points)
    # Signal com características reais: trend + oscilação + ruído
    signal = 2*t + 5*np.sin(2*np.pi*t) + 0.1*np.random.randn(n_points)
    
    # Adiciona alguns NaN para testar interpolação
    nan_indices = np.random.choice(n_points, size=n_points//20, replace=False)
    signal[nan_indices] = np.nan
    
    return t, signal


def benchmark_interpolation_1m(profiler):
    """Benchmark: Interpolação 1M pontos < 2s"""
    logger.info("benchmark_start", target="interpolation_1m", points=1000000)
    
    t, signal = generate_test_data(1000000)
    
    start_time = time.perf_counter()
    
    result = profiler.profile_function(
        interpolate,
        signal, t, "linear", {},
        target_name="interpolation_1m"
    )
    
    duration = time.perf_counter() - start_time
    
    success = duration <= 2.0
    
    logger.info("benchmark_complete",
               target="interpolation_1m", 
               duration=duration,
               target_time=2.0,
               success=success,
               points_interpolated=len(result.values))
    
    return success, duration, 2.0


def benchmark_derivative_1m(profiler):
    """Benchmark: Derivada 1M pontos < 1s"""
    logger.info("benchmark_start", target="derivative_1m", points=1000000)
    
    t, signal = generate_test_data(1000000)
    # Remove NaNs para derivada
    valid_mask = np.isfinite(signal)
    t_clean = t[valid_mask]
    signal_clean = signal[valid_mask]
    
    start_time = time.perf_counter()
    
    result = profiler.profile_function(
        derivative,
        signal_clean, t_clean, 1, "finite_diff", {},
        target_name="derivative_1m"
    )
    
    duration = time.perf_counter() - start_time
    
    success = duration <= 1.0
    
    logger.info("benchmark_complete",
               target="derivative_1m",
               duration=duration, 
               target_time=1.0,
               success=success,
               points_processed=len(result.values))
    
    return success, duration, 1.0


def benchmark_integral_500k(profiler):
    """Benchmark: Integral 500K pontos < 0.5s"""
    logger.info("benchmark_start", target="integral_500k", points=500000)
    
    t, signal = generate_test_data(500000)
    # Remove NaNs para integral
    valid_mask = np.isfinite(signal)
    t_clean = t[valid_mask]
    signal_clean = signal[valid_mask]
    
    start_time = time.perf_counter()
    
    result = profiler.profile_function(
        integral,
        signal_clean, t_clean, "trapezoid",
        target_name="integral_500k"
    )
    
    duration = time.perf_counter() - start_time
    
    success = duration <= 0.5
    
    logger.info("benchmark_complete",
               target="integral_500k",
               duration=duration,
               target_time=0.5, 
               success=success)
    
    return success, duration, 0.5


def run_performance_validation(config_path: str, output_html: str = None, output_json: str = None):
    """Executa validação completa de performance targets"""
    
    logger.info("performance_validation_start", config=config_path)
    
    # Setup profiler
    profiler = setup_profiling_from_config(config_path)
    if not profiler:
        logger.error("profiler_setup_failed")
        return False
    
    # Clear existing results
    profiler.clear_results()
    
    benchmarks = [
        ("interpolation_1m", benchmark_interpolation_1m),
        ("derivative_1m", benchmark_derivative_1m), 
        ("integral_500k", benchmark_integral_500k)
    ]
    
    results = {}
    overall_success = True
    
    for target_name, benchmark_func in benchmarks:
        try:
            success, duration, target_time = benchmark_func(profiler)
            results[target_name] = {
                "success": success,
                "duration": duration, 
                "target_time": target_time,
                "ratio": duration / target_time
            }
            
            if not success:
                overall_success = False
                
        except Exception as e:
            logger.error("benchmark_failed", target=target_name, error=str(e))
            results[target_name] = {
                "success": False,
                "error": str(e)
            }
            overall_success = False
    
    # Gera relatórios
    profiling_results = profiler.get_results()
    
    if output_html:
        generate_html_report(profiling_results, output_html)
        logger.info("html_report_generated", file=output_html)
    
    if output_json:
        generate_json_report(profiling_results, output_json)
        logger.info("json_report_generated", file=output_json)
    
    # Summary
    logger.info("performance_validation_complete",
               overall_success=overall_success,
               results=results)
    
    # Print summary to console
    print("\n" + "="*80)
    print("PLATFORM BASE v2.0 - PERFORMANCE VALIDATION RESULTS")
    print("="*80)
    
    for target, result in results.items():
        if "error" in result:
            status = f"❌ ERROR: {result['error']}"
        elif result["success"]:
            status = f"✅ PASS ({result['duration']:.3f}s / {result['target_time']:.1f}s)"
        else:
            status = f"❌ FAIL ({result['duration']:.3f}s / {result['target_time']:.1f}s, {result['ratio']:.1f}x slower)"
            
        print(f"{target:20s}: {status}")
    
    print("\n" + "="*80)
    
    if overall_success:
        print("🎉 ALL PERFORMANCE TARGETS MET - 100% PRD COMPLIANCE ACHIEVED!")
        return True
    else:
        print("⚠️  SOME PERFORMANCE TARGETS MISSED - Review failed benchmarks")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate Platform Base performance targets")
    parser.add_argument("--config", default="configs/platform.yaml", 
                       help="Path to platform configuration file")
    parser.add_argument("--output-html", help="Output HTML report file")
    parser.add_argument("--output-json", help="Output JSON report file") 
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Default outputs if not specified
    output_html = args.output_html or "performance_validation_report.html"
    output_json = args.output_json or "performance_validation_report.json"
    
    success = run_performance_validation(
        str(config_path), 
        output_html,
        output_json
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()