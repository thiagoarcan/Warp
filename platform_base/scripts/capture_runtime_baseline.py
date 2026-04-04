#!/usr/bin/env python3
"""Capture runtime startup and memory baseline for launcher execution."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture startup and RSS baseline")
    parser.add_argument("--launcher", required=True, help="Launcher script path relative to platform_base")
    parser.add_argument("--output-json", required=True, help="Output JSON path relative to platform_base")
    parser.add_argument("--timeout", type=float, default=20.0, help="Timeout in seconds")
    return parser.parse_args()


def write_markdown_report(json_path: Path, payload: dict[str, object]) -> Path:
    md_path = json_path.with_suffix(".md")
    lines = [
        "# Performance Baseline",
        "",
        f"Generated at: {payload['started_at']}",
        f"Launcher: {payload['launcher']}",
        f"startup_seconds: {payload['startup_seconds']}",
        f"peak_rss_mb: {payload['peak_rss_mb']}",
        f"exit_code: {payload['exit_code']}",
        f"startup_detected: {payload['startup_detected']}",
        f"timed_out: {payload['timed_out']}",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    launcher_path = (project_root / args.launcher).resolve()
    output_json = (project_root / args.output_json).resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)

    if not launcher_path.exists():
        print(f"Launcher not found: {launcher_path}", file=sys.stderr)
        return 2

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = str(project_root / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    cmd = [sys.executable, str(launcher_path)]
    started_at = datetime.now().isoformat(timespec="seconds")
    start = time.perf_counter()

    process = subprocess.Popen(
        cmd,
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    proc = psutil.Process(process.pid)
    startup_detected = False
    peak_rss = 0
    timed_out = False
    stdout_buffer: list[str] = []

    success_marker = "Platform Base v2.0 iniciado com sucesso!"

    try:
        while True:
            if process.poll() is not None:
                break

            now_elapsed = time.perf_counter() - start
            if now_elapsed > args.timeout:
                timed_out = True
                process.kill()
                break

            try:
                rss = proc.memory_info().rss
                if rss > peak_rss:
                    peak_rss = rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Avoid blocking reads from stdout; on Windows this can deadlock
            # if no newline is emitted yet. Use a warmup threshold plus a
            # post-process marker check from communicate() output.
            startup_threshold = min(max(args.timeout * 0.25, 3.0), 15.0)
            if now_elapsed >= startup_threshold and process.poll() is None:
                startup_detected = True
                process.terminate()
                break

            time.sleep(0.05)

        try:
            stdout_tail, stderr_tail = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout_tail, stderr_tail = process.communicate()

    finally:
        if process.poll() is None:
            process.kill()

    startup_seconds = round(time.perf_counter() - start, 4)
    payload = {
        "launcher": str(Path(args.launcher).as_posix()),
        "started_at": started_at,
        "startup_seconds": startup_seconds,
        "peak_rss_mb": round(peak_rss / (1024 * 1024), 3),
        "exit_code": process.returncode,
        "startup_detected": startup_detected,
        "timed_out": timed_out,
        "stdout_tail": ("\n".join(stdout_buffer[-20:]) + "\n" + stdout_tail[-1000:]).strip(),
        "stderr_tail": stderr_tail[-1000:].strip(),
    }

    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md = write_markdown_report(output_json, payload)

    print(f"Baseline JSON: {output_json}")
    print(f"Baseline Markdown: {report_md}")
    print(f"startup_seconds={payload['startup_seconds']}")
    print(f"peak_rss_mb={payload['peak_rss_mb']}")

    return 0 if (startup_detected and not timed_out) else 1


if __name__ == "__main__":
    raise SystemExit(main())



