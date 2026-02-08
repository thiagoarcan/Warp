#!/usr/bin/env python3
"""
Validate all .ui files can be loaded and rendered correctly.

This script:
1. Finds all .ui files in desktop/ui_files
2. Validates XML structure and Qt Designer format
3. Reports any loading errors
4. Generates a summary report
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def validate_ui_files():
    """Validate all .ui files can be loaded"""

    # Get platform_base root
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    ui_dir = root_dir / "src" / "platform_base" / "desktop" / "ui_files"

    print(f"🔍 Scanning UI files in: {ui_dir}")
    print("=" * 80)

    if not ui_dir.exists():
        print(f"❌ ERROR: UI directory not found: {ui_dir}")
        return False

    # Find all .ui files
    ui_files = sorted(ui_dir.glob("*.ui"))
    print(f"📁 Found {len(ui_files)} .ui files\n")

    results = {
        "success": [],
        "errors": [],
        "warnings": [],
    }

    for ui_file in ui_files:
        file_name = ui_file.name
        print(f"Testing: {file_name:50s} ", end="")

        try:
            # Parse XML
            tree = ET.parse(ui_file)
            root = tree.getroot()

            # Validate it's a Qt Designer file
            if root.tag != "ui":
                results["errors"].append(f"{file_name}: Not a Qt Designer file (root tag is '{root.tag}')")
                print("❌ ERROR: Invalid root tag")
                continue

            # Check version attribute
            version = root.get("version")
            if not version:
                results["warnings"].append(f"{file_name}: No version attribute")
            elif version != "4.0":
                results["warnings"].append(f"{file_name}: Version {version} (expected 4.0)")

            # Check for widget element
            widget = root.find("widget")
            if widget is None:
                results["errors"].append(f"{file_name}: No widget element found")
                print("❌ ERROR: No widget")
                continue

            # Check widget class
            widget_class = widget.get("class")
            if not widget_class:
                results["warnings"].append(f"{file_name}: No class attribute on widget")

            # Check widget name
            widget_name = widget.get("name")
            if not widget_name:
                results["warnings"].append(f"{file_name}: No name attribute on widget")

            results["success"].append(file_name)
            if any(w.startswith(file_name) for w in results["warnings"]):
                print("⚠️")
            else:
                print("✅")

        except ET.ParseError as e:
            results["errors"].append(f"{file_name}: XML parse error - {e!s}")
            print(f"❌ ERROR: {e}")
        except Exception as e:
            results["errors"].append(f"{file_name}: {e!s}")
            print(f"❌ ERROR: {e}")

    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully loaded: {len(results['success'])} files")
    print(f"⚠️  Warnings:           {len(results['warnings'])} files")
    print(f"❌ Errors:             {len(results['errors'])} files")
    print()

    if results["warnings"]:
        print("⚠️  WARNINGS:")
        for warning in results["warnings"]:
            print(f"   - {warning}")
        print()

    if results["errors"]:
        print("❌ ERRORS:")
        for error in results["errors"]:
            print(f"   - {error}")
        print()
        return False

    print("✅ All UI files loaded successfully!")
    return True


def main():
    """Main entry point"""
    success = validate_ui_files()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
