#!/usr/bin/env python3
"""
Launcher simples para Platform Base v2.0
"""

import os
import sys
from pathlib import Path


# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment for Windows console encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

def main():
    """Launch the application"""
    try:
        print("Starting Platform Base v2.0...")
        print("run_app.py is a compatibility wrapper. Canonical launcher: launch_app.py")

        # Delegate to canonical launcher path
        from launch_app import main as launch_main

        return launch_main()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

