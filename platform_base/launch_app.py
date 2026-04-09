#!/usr/bin/env python3
"""Canonical launcher delegating to the maintained UI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from platform_base.ui.app import main as _main


def main(argv: list[str] | None = None) -> int:
    """Launch the supported desktop application entrypoint."""
    return _main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
