#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_tests.py - Script para execucao dos testes automatizados.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_reports_dir(project_root: Path) -> Path:
    reports_dir = project_root / "docs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def extract_pytest_summary(stdout_text: str, stderr_text: str) -> str:
    combined = [line.strip() for line in (stdout_text + "\n" + stderr_text).splitlines() if line.strip()]
    summary_markers = ("passed", "failed", "error", "skipped", "xfailed", "xpassed")
    for line in reversed(combined):
        lowered = line.lower()
        if any(marker in lowered for marker in summary_markers):
            return line
    return "summary-not-found"


def run_pytest(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "pytest"] + args

    print("\n" + "=" * 60)
    print(f"Executando: {' '.join(cmd)}")
    print(f"Diretorio: {cwd}")
    print("=" * 60 + "\n")

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = str(cwd / "src")

    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )


def write_baseline_artifact(
    reports_dir: Path,
    cmd: list[str],
    cwd: Path,
    result: subprocess.CompletedProcess[str],
    pytest_summary: str,
) -> Path:
    baseline_file = reports_dir / "test_baseline.md"
    generated_at = datetime.now().isoformat(timespec="seconds")

    content = [
        "# Test Baseline",
        "",
        f"Generated at: {generated_at}",
        f"Command: {' '.join(cmd)}",
        f"Working directory: {cwd}",
        "QT_QPA_PLATFORM=offscreen",
        "PYTHONPATH=src",
        f"Exit code: {result.returncode}",
        f"Pytest summary: {pytest_summary}",
        "",
        "## Stdout (last 80 lines)",
        "```text",
        "\n".join(result.stdout.strip().splitlines()[-80:]) or "(none)",
        "```",
        "",
        "## Stderr (last 40 lines)",
        "```text",
        "\n".join(result.stderr.strip().splitlines()[-40:]) or "(none)",
        "```",
        "",
    ]
    baseline_file.write_text("\n".join(content), encoding="utf-8")
    return baseline_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa testes automatizados do projeto")
    parser.add_argument("--fast", action="store_true", help="Executa apenas testes rapidos")
    parser.add_argument("--cov", action="store_true", help="Habilita cobertura de codigo")
    parser.add_argument("--memray", action="store_true", help="Habilita detecao de memory leaks com memray")
    parser.add_argument("--all", action="store_true", help="Habilita todos os recursos")
    parser.add_argument("--verbose", "-v", action="store_true", help="Saida detalhada")
    parser.add_argument("--module", type=str, help="Executa apenas um modulo especifico")
    parser.add_argument("--markers", "-m", type=str, help="Filtra por markers")

    args = parser.parse_args()

    project_root = get_project_root()
    reports_dir = ensure_reports_dir(project_root)

    pytest_args = [
        "tests/automated",
        f"--html={reports_dir / 'test_report.html'}",
        "--self-contained-html",
        f"--junitxml={reports_dir / 'junit.xml'}",
    ]

    if args.verbose:
        pytest_args.append("-v")
    else:
        pytest_args.append("-q")

    if args.fast:
        pytest_args.extend([
            "--ignore=tests/automated/test_08_memory_leaks.py",
            "-m",
            "not slow",
        ])

    if args.cov or args.all:
        pytest_args.extend([
            "--cov=src/platform_base",
            "--cov-report=html:docs/reports/htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=70",
        ])

    if args.memray or args.all:
        pytest_args.append("--memray")

    if args.module:
        pytest_args = [f"tests/automated/{args.module}*.py"] + pytest_args[1:]

    if args.markers:
        pytest_args.extend(["-m", args.markers])

    executed_cmd = [sys.executable, "-m", "pytest"] + pytest_args
    result = run_pytest(pytest_args, project_root)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    pytest_summary = extract_pytest_summary(result.stdout, result.stderr)
    baseline_file = write_baseline_artifact(reports_dir, executed_cmd, project_root, result, pytest_summary)

    print("\n" + "=" * 60)
    print("RESUMO DA EXECUCAO")
    print("=" * 60)
    print(f"Codigo de saida: {result.returncode}")
    print(f"Relatorio HTML: {reports_dir / 'test_report.html'}")
    print(f"Relatorio JUnit: {reports_dir / 'junit.xml'}")
    print(f"Baseline: {baseline_file}")
    print(f"Pytest summary: {pytest_summary}")

    if args.cov or args.all:
        print(f"Cobertura HTML: {reports_dir / 'htmlcov' / 'index.html'}")

    print("=" * 60 + "\n")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
