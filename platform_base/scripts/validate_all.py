#!/usr/bin/env python3
"""Current regression gate for phase 01 baseline validation."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path, label: str) -> int:
    print("\n" + "=" * 70)
    print(f"[RUN] {label}")
    print(f"[CMD] {' '.join(cmd)}")
    print("=" * 70)
    result = subprocess.run(cmd, cwd=cwd)
    print(f"[EXIT] {result.returncode}")
    return result.returncode


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]

    critical_pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/automated/test_01_ui_loading.py",
        "tests/automated/test_03_navigation.py",
        "tests/automated/test_04_signals_slots.py",
        "tests/automated/test_05_initialization.py",
        "tests/automated/test_09_exceptions_errors.py",
        "-q",
        "--tb=no",
        "-x",
    ]

    perf_cmd = [
        sys.executable,
        "scripts/capture_runtime_baseline.py",
        "--launcher",
        "launch_app.py",
        "--output-json",
        "docs/reports/performance_baseline.json",
        "--timeout",
        "60",
    ]

    gate_exit = run_command(critical_pytest_cmd, project_root, "Critical-path pytest gate")
    if gate_exit != 0:
        return gate_exit

    perf_exit = run_command(perf_cmd, project_root, "Runtime baseline capture")
    if perf_exit != 0:
        return perf_exit

    print("\n[OK] validate_all completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
