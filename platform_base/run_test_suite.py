#!/usr/bin/env python
"""Portable runner for the automated test suite."""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def _extract_pytest_summary(stdout_text: str) -> str:
    lines = [line.strip() for line in stdout_text.splitlines() if line.strip()]
    summary_markers = ("passed", "failed", "error", "skipped", "xfailed", "xpassed")
    for line in reversed(lines):
        lowered = line.lower()
        if any(marker in lowered for marker in summary_markers):
            return line
    return "summary-not-found"


def main() -> int:
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/automated",
        "--cache-clear",
        "-q",
        "--tb=no",
        "-rA",
    ]

    print("=== EXECUTED COMMAND ===")
    print(shlex.join(cmd))
    print(f"CWD: {PROJECT_ROOT}")

    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=1200,
    )

    summary = _extract_pytest_summary(result.stdout)

    print("\n=== PYTEST SUMMARY ===")
    print(summary)

    print("\n=== STDOUT (last 40 lines) ===")
    out_lines = result.stdout.strip().splitlines()
    for line in out_lines[-40:]:
        print(line)

    print("\n=== STDERR (last 20 lines) ===")
    err_lines = result.stderr.strip().splitlines()
    if err_lines:
        for line in err_lines[-20:]:
            print(line)
    else:
        print("(none)")

    print(f"\n=== EXIT CODE: {result.returncode} ===")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
