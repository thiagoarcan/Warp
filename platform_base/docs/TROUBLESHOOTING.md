# Platform Base v2.0 - Troubleshooting Guide

**Solutions to common problems and issues**

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Startup Problems](#startup-problems)
3. [Data Loading Issues](#data-loading-issues)
4. [Performance Problems](#performance-problems)
5. [Visualization Issues](#visualization-issues)
6. [Calculation Errors](#calculation-errors)
7. [Memory Issues](#memory-issues)
8. [UI/Display Problems](#uidisplay-problems)
9. [Export Issues](#export-issues)
10. [Plugin Problems](#plugin-problems)
11. [System-Specific Issues](#system-specific-issues)
12. [Getting More Help](#getting-more-help)

---

## Installation Issues

### Problem: pip install fails with "No module named 'platform_base'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'platform_base'
```

**Solutions**:
1. Ensure you're in correct directory:
   ```bash
   cd /path/to/Warp/platform_base
   pwd  # Should show platform_base directory
   ```

2. Install in editable mode:
   ```bash
   pip install -e .
   ```

3. Check Python version:
   ```bash
   python --version  # Should be 3.12+
   ```

### Problem: Dependency conflicts during installation

**Symptoms**:
```
ERROR: package X requires Y<2.0, but you have Y 2.1
```

**Solutions**:
1. Create clean virtual environment:
   ```bash
   python -m venv venv_clean
   source venv_clean/bin/activate
   pip install -e .
   ```

2. Update pip:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. Install with specific versions:
   ```bash
   pip install -e . --no-deps
   pip install -r requirements.txt
   ```

### Problem: PyQt6 won't install

**Symptoms**:
```
ERROR: Could not build wheels for PyQt6
```

**Solutions**:

**Linux**:
```bash
sudo apt-get update
sudo apt-get install python3-pyqt6 libgl1-mesa-glx
pip install PyQt6
```

**macOS**:
```bash
brew install qt6
pip install PyQt6
```

**Windows**:
- Ensure Visual C++ Redistributable is installed
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Startup Problems

### Problem: Application won't start

**Symptoms**:
- Window doesn't appear
- Command hangs
- Immediate exit

**Solutions**:

1. **Check for error messages**:
   ```bash
   python -m platform_base.desktop.main_window --debug
   ```

2. **Check logs**:
   ```bash
   cat ~/.platform_base/logs/app.log
   ```

3. **Test Qt installation**:
   ```python
   from PyQt6.QtWidgets import QApplication
   import sys
   app = QApplication(sys.argv)
   print("Qt working!")
   ```

4. **Check display**:
   ```bash
   echo $DISPLAY  # Linux
   # Should output :0 or similar
   ```

### Problem: Application crashes on startup

**Symptoms**:
```
Segmentation fault (core dumped)
```

**Solutions**:

1. **Update graphics drivers** (most common cause)

2. **Try software rendering**:
   ```bash
   export QT_QPA_PLATFORM=offscreen
   python launch_app.py
   ```

3. **Check OpenGL**:
   ```bash
   glxinfo | grep "OpenGL version"
   ```

4. **Reinstall PyQt6**:
   ```bash
   pip uninstall PyQt6
   pip install PyQt6 --no-cache-dir
   ```

---

## Data Loading Issues

### Problem: CSV file won't load

**Symptoms**:
- "Unable to parse file" error
- Empty dataset
- Wrong columns

**Solutions**:

1. **Check file encoding**:
   ```bash
   file -i your_file.csv
   # or
   chardet your_file.csv
   ```

2. **Try different delimiter**:
   - Load dialog → Delimiter → Try Tab, Semicolon, Space

3. **Check for BOM (Byte Order Mark)**:
   ```python
   with open('file.csv', 'rb') as f:
       first_bytes = f.read(3)
       if first_bytes == b'\xef\xbb\xbf':
           print("UTF-8 BOM detected")
   ```
   Solution: Re-save file without BOM

4. **Validate CSV structure**:
   ```bash
   head -5 your_file.csv
   # Check:
   # - Consistent number of columns
   # - No empty lines at start
   # - Header row present
   ```

### Problem: Excel file loads but data is wrong

**Symptoms**:
- Missing columns
- Wrong sheet loaded
- Dates showing as numbers

**Solutions**:

1. **Specify correct sheet**:
   - Load dialog → Sheet dropdown → Select correct sheet

2. **Check date format**:
   - Load dialog → Date columns → Manual selection
   - Or: Format dates as ISO in Excel (YYYY-MM-DD)

3. **Handle merged cells**:
   - Excel merged cells not supported
   - Unmerge in Excel before loading

4. **Check formula cells**:
   - Formulas not evaluated
   - Copy-paste as values in Excel first

### Problem: Large file takes forever to load

**Symptoms**:
- Loading progress stuck
- Application not responding
- Memory grows continuously

**Solutions**:

1. **Enable decimation**:
   ```python
   load(file, config={"max_rows": 100000})
   ```

2. **Use Parquet instead of CSV**:
   ```python
   # Convert first
   import pandas as pd
   df = pd.read_csv("large.csv")
   df.to_parquet("large.parquet")
   ```

3. **Load specific columns only**:
   - Load dialog → Select Columns → Choose only needed columns

4. **Split file into chunks**:
   ```bash
   split -l 100000 large.csv chunk_
   ```

---

## Performance Problems

### Problem: Application is slow/laggy

**Symptoms**:
- UI freezes
- Plot updates slow
- Operations take too long

**Solutions**:

1. **Enable auto-decimation**:
   - Settings → Performance → Auto-decimate: ON
   - Decimation threshold: 10000 points

2. **Close unused tabs**:
   - Each plot uses memory
   - Close: Right-click tab → Close

3. **Reduce data size**:
   - Export decimated version
   - Work with filtered subset

4. **Check CPU usage**:
   ```bash
   top -p $(pgrep -f platform_base)
   ```

5. **Disable anti-aliasing**:
   - Settings → Visualization → Anti-aliasing: OFF

### Problem: Plot rendering is slow

**Symptoms**:
- Zoom/pan laggy
- Plot takes seconds to update

**Solutions**:

1. **Enable GPU acceleration**:
   - Settings → Performance → GPU: ON

2. **Use LTTB downsampling**:
   ```python
   from platform_base.processing.downsampling import downsample_lttb
   downsampled = downsample_lttb(data, time, n_out=2000)
   ```

3. **Reduce number of series**:
   - Too many series (>10) slows rendering
   - Plot subsets separately

4. **Check graphics driver**:
   ```bash
   glxinfo | grep "renderer"
   ```

---

## Visualization Issues

### Problem: Plot is blank/empty

**Symptoms**:
- White canvas
- No data visible
- Axes present but no lines

**Solutions**:

1. **Check data range**:
   - Data might be outside view
   - Right-click → Reset View (or press `R`)

2. **Check series is added**:
   - Look for series in legend
   - If missing, double-click series in data tree

3. **Check for NaN values**:
   ```python
   import numpy as np
   has_nan = np.any(np.isnan(series.values))
   ```

4. **Check axis scales**:
   - Linear vs Log scale mismatch
   - Right-click axis → Linear Scale

### Problem: Colors not displaying correctly

**Symptoms**:
- All series same color
- Colors very similar
- Can't distinguish series

**Solutions**:

1. **Reset color scheme**:
   - Settings → Visualization → Colors → Reset to Default

2. **Manually set colors**:
   - Right-click series in legend
   - Change Color → Pick distinct color

3. **Use colorblind-friendly palette**:
   - Settings → Visualization → Color Palette → Colorblind

4. **Check theme**:
   - Dark theme may affect visibility
   - Try: Settings → Appearance → Theme → Light

### Problem: 3D plot won't render

**Symptoms**:
- Error: "VTK not available"
- 3D window blank
- Crash when opening 3D

**Solutions**:

1. **Install VTK**:
   ```bash
   pip install vtk pyvista
   ```

2. **Check OpenGL support**:
   ```bash
   glxinfo | grep "OpenGL"
   # Should show OpenGL 3.0+
   ```

3. **Use software rendering**:
   ```bash
   export PYVISTA_OFF_SCREEN=true
   ```

4. **Update graphics drivers**

---

## Calculation Errors

### Problem: Derivative returns NaN

**Symptoms**:
```
RuntimeWarning: invalid value encountered
Result contains NaN
```

**Solutions**:

1. **Check input for NaN**:
   - Operations → Interpolation → Fill gaps first

2. **Check time array**:
   - Must be monotonically increasing
   - No duplicate timestamps

3. **Use different method**:
   - Try: Forward difference instead of central

4. **Filter noise first**:
   - Operations → Filters → Lowpass
   - Then calculate derivative

### Problem: Interpolation fails

**Symptoms**:
```
ValueError: x must be strictly increasing
```

**Solutions**:

1. **Sort time array**:
   ```python
   sorted_indices = np.argsort(t)
   t_sorted = t[sorted_indices]
   y_sorted = y[sorted_indices]
   ```

2. **Remove duplicates**:
   ```python
   unique_indices = np.unique(t, return_index=True)[1]
   t_unique = t[unique_indices]
   y_unique = y[unique_indices]
   ```

3. **Check for gaps**:
   - Large gaps (>10x median spacing) may cause issues
   - Consider: Operations → Interpolation → Method → Linear (more robust)

### Problem: "Out of bounds" error

**Symptoms**:
```
IndexError: index out of bounds
```

**Solutions**:

1. **Check array lengths match**:
   ```python
   len(time) == len(values)  # Must be true
   ```

2. **Check for empty arrays**:
   ```python
   if len(data) == 0:
       # Handle empty case
   ```

3. **Validate indices**:
   - Don't access data[len(data)]
   - Use data[-1] for last element

---

## Memory Issues

### Problem: Out of memory error

**Symptoms**:
```
MemoryError
killed
```

**Solutions**:

1. **Increase memory limit**:
   - Settings → Performance → Memory Limit → 80% of RAM

2. **Use chunked loading**:
   ```python
   load(file, config={"max_rows": 50000, "chunked": True})
   ```

3. **Close other applications**

4. **Use 64-bit Python**:
   ```bash
   python -c "import struct; print(struct.calcsize('P') * 8)"
   # Should print: 64
   ```

5. **Enable disk caching**:
   - Settings → Performance → Disk Cache: ON

### Problem: Memory usage keeps growing

**Symptoms**:
- RAM usage increases over time
- Application slows down
- Eventually crashes

**Solutions**:

1. **Clear undo history**:
   - Edit → Clear Undo History

2. **Close unused tabs**:
   - Each tab holds data in memory

3. **Restart application periodically**

4. **Check for memory leaks**:
   ```bash
   python -m memory_profiler launch_app.py
   ```

5. **Disable auto-save**:
   - Settings → Auto-save → Disabled

---

## UI/Display Problems

### Problem: UI elements too small/large

**Symptoms**:
- Text unreadable
- Buttons tiny
- Widgets overlap

**Solutions**:

1. **Adjust DPI scaling** (Windows):
   - Right-click app → Properties → Compatibility
   - Override high DPI scaling: Application

2. **Change font size**:
   - Settings → Appearance → Font Size → Adjust

3. **Use UI zoom**:
   - Settings → Accessibility → UI Zoom → 125% or 150%

### Problem: Theme not applying

**Symptoms**:
- Changed theme but no effect
- Mixed light/dark elements

**Solutions**:

1. **Restart application** (required for theme change)

2. **Check theme files**:
   ```bash
   ls ~/.platform_base/themes/
   ```

3. **Reset to default**:
   - Settings → Appearance → Theme → Reset to Default

### Problem: Menus/dialogs appear off-screen

**Symptoms**:
- Can't see dialog
- Menu cut off

**Solutions**:

1. **Reset window positions**:
   - Settings → General → Reset Window Positions

2. **Change monitor** (multi-monitor setup):
   ```bash
   # Move window to primary monitor
   xrandr --output HDMI-1 --primary
   ```

3. **Use keyboard navigation**:
   - `Tab` to cycle through elements
   - `Enter` to activate

---

## Export Issues

### Problem: Export fails silently

**Symptoms**:
- Export button clicked
- No file created
- No error message

**Solutions**:

1. **Check file permissions**:
   ```bash
   ls -l /export/directory/
   # Should have write permission
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Try different location**:
   - Export to home directory first
   - Then move file

4. **Check logs**:
   ```bash
   tail ~/.platform_base/logs/export.log
   ```

### Problem: Exported CSV is corrupted

**Symptoms**:
- File won't open
- Columns misaligned
- Extra characters

**Solutions**:

1. **Specify encoding explicitly**:
   - Export dialog → Encoding → UTF-8 (BOM)

2. **Check delimiter**:
   - Export dialog → Delimiter → Match import tool

3. **Validate exported file**:
   ```bash
   head -10 exported.csv
   wc -l exported.csv
   ```

---

## Plugin Problems

### Problem: Plugin not loading

**Symptoms**:
- Plugin not in menu
- Import error
- "Plugin failed to load"

**Solutions**:

1. **Check plugin directory**:
   ```bash
   ls ~/.platform_base/plugins/
   ```

2. **Check plugin.yaml**:
   ```bash
   cat ~/.platform_base/plugins/myplugin/plugin.yaml
   # Validate YAML syntax
   ```

3. **Check dependencies**:
   ```bash
   pip list | grep plugin-name
   ```

4. **Enable plugin logging**:
   - Settings → Advanced → Plugin Debug: ON

5. **Reinstall plugin**:
   ```bash
   python -m platform_base.plugins uninstall myplugin
   python -m platform_base.plugins install /path/to/myplugin
   ```

---

## System-Specific Issues

### Linux

**Problem**: libEGL error
```
ImportError: libEGL.so.1: cannot open shared object file
```

**Solution**:
```bash
sudo apt-get install libegl1-mesa libgl1-mesa-glx
```

**Problem**: X11 connection error
```
qt.qpa.xcb: could not connect to display
```

**Solution**:
```bash
export DISPLAY=:0
xhost +local:
```

### macOS

**Problem**: App not authorized
```
"Platform Base" cannot be opened because the developer cannot be verified
```

**Solution**:
```bash
xattr -cr /path/to/platform_base.app
```

**Problem**: Retina display issues
**Solution**:
- Settings → Display → Use Native Resolution: ON

### Windows

**Problem**: DLL load failed
```
ImportError: DLL load failed while importing QtCore
```

**Solution**:
- Install Visual C++ Redistributable 2015-2022
- https://aka.ms/vs/17/release/vc_redist.x64.exe

**Problem**: Antivirus blocking
**Solution**:
- Add exception for platform_base.exe
- Or temporarily disable antivirus

---

## Getting More Help

### Before Asking for Help

1. **Check logs**:
   ```bash
   # Application log
   cat ~/.platform_base/logs/app.log
   
   # Error log
   cat ~/.platform_base/logs/errors.log
   ```

2. **Try verbose mode**:
   ```bash
   python launch_app.py --verbose --debug
   ```

3. **Check system info**:
   ```bash
   python -c "import platform; print(platform.platform())"
   python -c "import platform_base; print(platform_base.__version__)"
   ```

### Reporting Issues

When creating GitHub issue, include:

1. **Platform Base version**
2. **Operating system** (name + version)
3. **Python version**
4. **Steps to reproduce**
5. **Expected vs actual behavior**
6. **Error messages** (full traceback)
7. **Log files** (if relevant)
8. **Screenshots** (if UI issue)

### Community Resources

- **GitHub Issues**: https://github.com/thiagoarcan/Warp/issues
- **Discussions**: https://github.com/thiagoarcan/Warp/discussions
- **Documentation**: All docs in `/docs` directory

### Professional Support

For enterprise support, contact: support@platform-base.com

---

## Diagnostic Tools

### System Info Script

```python
#!/usr/bin/env python3
"""Print diagnostic information."""

import sys
import platform
import platform_base

print("System Information")
print("=" * 50)
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Platform Base: {platform_base.__version__}")

try:
    from PyQt6 import QtCore
    print(f"PyQt6: {QtCore.PYQT_VERSION_STR}")
except ImportError:
    print("PyQt6: NOT INSTALLED")

try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
except ImportError:
    print("NumPy: NOT INSTALLED")

print("\nInstallation directory:")
print(platform_base.__file__)
```

### Quick Health Check

```bash
#!/bin/bash
echo "Platform Base Health Check"
echo "=========================="

# Check Python
python --version || echo "ERROR: Python not found"

# Check installation
python -c "import platform_base" && echo "✓ Package installed" || echo "✗ Package not installed"

# Check Qt
python -c "from PyQt6.QtWidgets import QApplication" && echo "✓ Qt available" || echo "✗ Qt not available"

# Check dependencies
pip check && echo "✓ No dependency conflicts" || echo "✗ Dependency issues"

# Check logs
if [ -f ~/.platform_base/logs/app.log ]; then
    echo "✓ Logs directory exists"
    echo "Last log entry:"
    tail -1 ~/.platform_base/logs/app.log
else
    echo "✗ No logs found"
fi
```

---

*Platform Base v2.0 - Troubleshooting Guide*  
*Last Updated: 2026-02-02*
