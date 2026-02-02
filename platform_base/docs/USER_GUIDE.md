# Platform Base v2.0 - Complete User Guide

**Comprehensive guide for end users**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [User Interface Overview](#user-interface-overview)
5. [Loading Data](#loading-data)
6. [Visualization](#visualization)
7. [Data Analysis](#data-analysis)
8. [Streaming & Playback](#streaming--playback)
9. [Export & Reports](#export--reports)
10. [Keyboard Shortcuts](#keyboard-shortcuts)
11. [Settings & Configuration](#settings--configuration)
12. [Tips & Best Practices](#tips--best-practices)
13. [FAQ](#faq)
14. [Support](#support)

---

## Introduction

Platform Base is a desktop application for exploring and analyzing time-series data from sensors, navigation systems, and SCADA equipment. It provides interactive visualization, advanced calculations, and export capabilities.

### Key Features

- 📊 **Interactive 2D/3D Visualization** - Real-time plots with zoom, pan, and selection
- 📁 **Multi-format Support** - CSV, Excel, Parquet, HDF5, MAT files
- 🧮 **Advanced Calculations** - Derivatives, integrals, interpolation, filtering
- 🎬 **Time Streaming** - Animated playback of temporal data
- 🔄 **Synchronization** - Align multiple time series automatically
- 🌙 **Themes** - Light and dark modes
- 🌍 **Multilingual** - English and Portuguese

### System Requirements

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.12 or higher
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 500MB for installation
- **Display**: 1920x1080 or higher recommended

---

## Getting Started

### Quick Start (5 minutes)

1. **Install Platform Base**
   ```bash
   pip install -e .
   ```

2. **Launch the application**
   ```bash
   python -m platform_base.desktop.main_window
   ```

3. **Load sample data**
   - Click "File → Open" or press `Ctrl+O`
   - Select a CSV or Excel file
   - Data appears in the left panel

4. **Visualize**
   - Double-click a series in the data tree
   - Series appears in the visualization panel
   - Use mouse to zoom/pan

5. **Calculate**
   - Select a series
   - Click "Operations → Derivative"
   - Result appears as new series

---

## Installation

### Standard Installation

```bash
# Clone repository
git clone https://github.com/thiagoarcan/Warp.git
cd Warp/platform_base

# Install dependencies
pip install -e .

# Install development tools (optional)
pip install -e ".[dev]"

# Install visualization extras (optional)
pip install -e ".[viz]"
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install
pip install -e .
```

### Verify Installation

```bash
python -c "import platform_base; print(platform_base.__version__)"
# Should print: 2.0.0
```

---

## User Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Menu Bar: File | Edit | View | Operations | Tools | Help    │
├─────────────────────────────────────────────────────────────┤
│ Toolbar: [Open] [Save] [Zoom] [Pan] [Settings]             │
├──────────────┬──────────────────────────────┬───────────────┤
│              │                              │               │
│  Data Panel  │   Visualization Panel        │  Operations   │
│              │                              │   Panel       │
│  📁 Files    │   [2D/3D Plots]             │               │
│  📊 Series   │                              │  [Calculate]  │
│  ℹ️  Info     │   [Controls]                │  [Filter]     │
│              │                              │  [Export]     │
│              │                              │               │
├──────────────┴──────────────────────────────┴───────────────┤
│ Status Bar: Ready | Memory: 120MB | Series: 3               │
└─────────────────────────────────────────────────────────────┘
```

### Panels

#### Data Panel (Left)
- **Tree View**: Hierarchical view of datasets and series
- **Info Tabs**: Summary, Metadata, Quality
- **Buttons**: Load, Remove, Refresh

#### Visualization Panel (Center)
- **Plot Area**: Interactive 2D or 3D plots
- **Tabs**: Multiple plots in tabs
- **Toolbar**: Zoom, Pan, Reset, Screenshot
- **Controls**: Line width, grid, legend settings

#### Operations Panel (Right)
- **Calculations**: Derivative, Integral, Area
- **Filters**: Lowpass, Highpass, Bandpass
- **Interpolation**: Fill gaps in data
- **Statistics**: Min, Max, Mean, Std Dev

---

## Loading Data

### Supported Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| CSV | .csv | ✅ | ✅ | Fastest |
| Excel | .xlsx | ✅ | ✅ | Multiple sheets supported |
| Parquet | .parquet | ✅ | ✅ | Best for large files |
| HDF5 | .h5, .hdf5 | ✅ | ✅ | Scientific data |
| MAT | .mat | ✅ | ❌ | MATLAB files |

### Loading Files

**Method 1: Menu**
1. File → Open (or `Ctrl+O`)
2. Select file
3. Configure import settings (if prompted)
4. Click OK

**Method 2: Drag & Drop**
1. Drag file from file explorer
2. Drop onto main window
3. Data loads automatically

**Method 3: Command Line**
```bash
python launch_app.py --file data.csv
```

### Import Settings

#### CSV Options
- **Delimiter**: Comma, Tab, Semicolon, Space
- **Encoding**: UTF-8, Latin-1, ASCII
- **Header Row**: Line number for column names
- **Skip Rows**: Number of rows to skip at start

#### Excel Options
- **Sheet**: Select which sheet to load
- **Range**: Specific cell range (e.g., A1:D1000)
- **Date Columns**: Auto-detect or manual selection

### Handling Large Files

For files > 100MB:

1. **Use Parquet format** - Faster than CSV/Excel
2. **Enable decimation** - Settings → Performance → Auto-decimate
3. **Increase memory limit** - Settings → Performance → Memory Limit
4. **Load specific columns only** - Import dialog → Select Columns

---

## Visualization

### 2D Plots

#### Creating a Plot

1. **Double-click** a series in data tree
2. Or **right-click** → "Add to Plot"
3. Or **drag** series to plot area

#### Plot Controls

- **Zoom**: Mouse wheel or `Ctrl + Drag`
- **Pan**: Click and drag or Arrow keys
- **Reset**: Right-click → Reset View or press `R`
- **Select**: `Ctrl + Drag` rectangle

#### Multiple Series

Add multiple series to same plot:
1. Click first series
2. Hold `Ctrl` and click additional series
3. Right-click → "Plot Selected"

All series appear with different colors.

#### Multiple Y Axes

For series with different scales:
1. Right-click series in legend
2. Select "Move to Y2 axis"
3. Second Y axis appears on right

#### Customization

**Line Style**
- Width: Toolbar → Line Width spinbox
- Color: Right-click series → Change Color
- Style: Solid, Dashed, Dotted

**Grid**
- Toggle: Toolbar → Show Grid checkbox
- Or press `G`

**Legend**
- Toggle: Toolbar → Show Legend checkbox
- Or press `L`
- Position: Drag legend to desired location

### 3D Plots

#### Creating 3D Plot

1. Select exactly 3 series (X, Y, Z axes)
2. Operations → Visualization → 3D Trajectory
3. 3D plot opens in new window

#### 3D Controls

- **Rotate**: Click and drag
- **Zoom**: Mouse wheel
- **Pan**: `Shift + Drag`
- **Reset Camera**: Press `R`

#### 3D Settings

- **Colormap**: Settings → Colormap dropdown
- **Point Size**: Settings → Point Size slider
- **Show Surface**: Settings → Show Surface checkbox

### Export Plots

**As Image**
1. Right-click plot → Export
2. Choose format: PNG, SVG, PDF
3. Select resolution (72-600 DPI)
4. Save

**As Animation**
1. Enable streaming mode
2. Tools → Export → Video
3. Choose format: MP4, GIF
4. Configure FPS and quality
5. Export

---

## Data Analysis

### Interpolation

Fill gaps in time series data:

1. Select series with gaps
2. Operations → Interpolation
3. Choose method:
   - **Linear**: Fast, simple
   - **Spline Cubic**: Smooth curves
   - **PCHIP**: Preserves monotonicity
   - **Akima**: Minimizes overshoot
4. Click "Apply"
5. New interpolated series created

### Derivatives

Calculate rate of change:

1. Select series (e.g., position)
2. Operations → Calculus → Derivative
3. Select order:
   - **1st**: Velocity
   - **2nd**: Acceleration
   - **3rd**: Jerk
4. Result: New series with derivative

**Example**: Position → Velocity
- Input: GPS position (meters)
- Output: Velocity (m/s)

### Integrals

Calculate area under curve:

1. Select series (e.g., velocity)
2. Operations → Calculus → Integral
3. Choose method:
   - **Trapezoidal**: Standard
   - **Simpson's**: More accurate
4. Result: Integrated series

**Example**: Velocity → Position
- Input: Velocity (m/s)
- Output: Displacement (meters)

### Filters

Remove noise from signals:

#### Lowpass Filter
Removes high-frequency noise:
1. Operations → Filters → Lowpass
2. Set cutoff frequency (Hz)
3. Preview result
4. Apply

#### Highpass Filter
Removes low-frequency drift:
1. Operations → Filters → Highpass
2. Set cutoff frequency
3. Apply

#### Bandpass Filter
Keeps only specific frequency range:
1. Operations → Filters → Bandpass
2. Set low and high cutoff
3. Apply

#### Moving Average
Simple smoothing:
1. Operations → Filters → Moving Average
2. Set window size
3. Apply

### Statistics

Get summary statistics:

1. Select series
2. Operations → Statistics → Summary
3. View results:
   - Count, Min, Max
   - Mean, Median, Mode
   - Std Dev, Variance
   - Percentiles (25%, 50%, 75%)

### Synchronization

Align multiple series with different time grids:

1. Select 2+ series
2. Operations → Synchronization
3. Choose method:
   - **Common Grid Interpolate**: Resample all to same time grid
   - **Nearest Neighbor**: Fast, less accurate
4. Apply
5. All series now have same time points

---

## Streaming & Playback

### Overview

Stream mode allows animated playback of time-series data, useful for:
- Reviewing sensor data over time
- Creating presentations
- Finding patterns in temporal data

### Enable Streaming

1. Load time-series data
2. View → Streaming Controls
3. Streaming panel appears at bottom

### Controls

```
[◀◀] [◀] [▶] [▶▶] [■] [Loop]
├─────────────────────────────┤ Timeline
│         Position            │
└─────────────────────────────┘

Speed: [0.5x] [1x] [2x] [4x]
Window: [5 sec] [10 sec] [30 sec]
```

- **Play/Pause**: Space bar or ▶ button
- **Stop**: ■ button or Escape
- **Seek**: Click timeline or use Left/Right arrows
- **Speed**: Adjust playback speed
- **Window**: How many seconds shown at once

### Streaming with Filters

Apply filters in real-time during playback:

1. Enable streaming
2. Operations → Filters → Real-time
3. Select filter (e.g., Lowpass)
4. Configure parameters
5. Play - filter applies as data streams

### Export Streaming Video

1. Configure streaming window
2. Tools → Export → Video
3. Choose:
   - Format: MP4, GIF
   - Resolution: 720p, 1080p, 4K
   - FPS: 15, 24, 30, 60
4. Click "Export"
5. Video generated

---

## Export & Reports

### Export Data

#### Single Series
1. Right-click series → Export
2. Choose format: CSV, Excel, Parquet
3. Save

#### Multiple Series
1. Select series (Ctrl+Click)
2. File → Export Selected
3. Options:
   - **Single file, multiple columns**
   - **Separate files**
4. Save

### Export Configuration

**CSV Options**
- Delimiter: Comma, Tab, Semicolon
- Encoding: UTF-8, Latin-1
- Include header: Yes/No
- Precision: Number of decimal places

**Excel Options**
- Single sheet: All series in one sheet
- Multiple sheets: One series per sheet
- Include metadata: Add info sheet

### Generate Report

Create PDF/HTML report:

1. Tools → Generate Report
2. Select content:
   - [ ] Summary statistics
   - [ ] Plots
   - [ ] Calculation results
   - [ ] Metadata
3. Choose template: Default, Technical, Executive
4. Generate
5. Report saved

---

## Keyboard Shortcuts

### General

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save session |
| `Ctrl+W` | Close current tab |
| `Ctrl+Q` | Quit application |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+A` | Select all |
| `Escape` | Deselect all |
| `F1` | Help |
| `F5` | Refresh data |
| `F11` | Toggle fullscreen |

### Visualization

| Shortcut | Action |
|----------|--------|
| `Space` | Play/Pause streaming |
| `R` | Reset view |
| `G` | Toggle grid |
| `L` | Toggle legend |
| `+` / `-` | Zoom in/out |
| `←` `→` | Pan left/right |
| `↑` `↓` | Pan up/down |
| `Ctrl+Drag` | Box zoom |
| `Shift+Drag` | Pan plot |

### Data

| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Duplicate series |
| `Delete` | Remove selected series |
| `Ctrl+F` | Find series |
| `Ctrl+E` | Export selected |

### Operations

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Calculate derivative |
| `Ctrl+2` | Calculate integral |
| `Ctrl+3` | Interpolate |
| `Ctrl+4` | Apply filter |

---

## Settings & Configuration

### General Settings

**File → Preferences** or `Ctrl+,`

#### Appearance
- **Theme**: Light, Dark, System
- **Font Size**: 8-16pt
- **Language**: English, Português

#### Performance
- **Auto-decimate**: Enable for files > 100K points
- **Decimation threshold**: Number of points
- **Memory limit**: Max RAM usage (MB)
- **Cache size**: Disk cache size (MB)

#### Data
- **Default delimiter**: CSV delimiter
- **Date format**: ISO, US, EU
- **Time zone**: UTC, Local
- **Precision**: Decimal places for display

#### Visualization
- **Default colors**: Color scheme for plots
- **Line width**: Default line width
- **Grid**: Show by default
- **Legend**: Show by default
- **Anti-aliasing**: Enable for smoother plots

### Advanced Settings

#### Interpolation
- **Default method**: Linear, Spline, PCHIP
- **Fill gaps**: Auto-fill gaps > X seconds
- **Max gap size**: Don't interpolate gaps larger than

#### Filters
- **Default cutoff**: Lowpass cutoff frequency
- **Filter order**: Butterworth filter order

#### Auto-save
- **Enable**: Auto-save session
- **Interval**: Save every X minutes
- **Keep versions**: Number of backup versions

---

## Tips & Best Practices

### Performance Tips

1. **Use Parquet for large files** - 5-10x faster than CSV
2. **Enable auto-decimation** - For files > 100K points
3. **Close unused tabs** - Reduces memory usage
4. **Export filtered data** - Work with smaller datasets
5. **Use keyboard shortcuts** - Faster than mouse

### Data Quality

1. **Check for gaps** - View → Quality Report
2. **Interpolate missing data** - Operations → Interpolation
3. **Remove outliers** - Operations → Filters → Outlier Detection
4. **Validate time stamps** - Ensure monotonic increasing
5. **Check units** - Verify physical units make sense

### Workflow Tips

1. **Save session regularly** - `Ctrl+S` after major changes
2. **Use descriptive names** - Rename series for clarity
3. **Add metadata** - Right-click → Edit Metadata
4. **Export intermediate results** - Save calculated series
5. **Document your work** - Use Notes panel

### Troubleshooting

**Problem**: App runs slow with large files
- **Solution**: Enable decimation, increase memory limit

**Problem**: Plot looks jagged
- **Solution**: Enable anti-aliasing in settings

**Problem**: Data not loading
- **Solution**: Check file format, try different delimiter

**Problem**: Out of memory error
- **Solution**: Close other apps, reduce dataset size, increase swap

---

## FAQ

### General Questions

**Q: What file formats are supported?**
A: CSV, Excel (.xlsx), Parquet, HDF5, MAT files. See [Loading Data](#loading-data).

**Q: How large files can I load?**
A: Tested up to 10M rows (1GB). Performance depends on available RAM.

**Q: Can I use this for real-time data?**
A: Yes, streaming mode supports real-time playback and filtering.

**Q: Is there a Python API?**
A: Yes, see [API Reference](API_REFERENCE.md).

### Data Questions

**Q: How do I handle missing data?**
A: Use interpolation: Operations → Interpolation. Choose method based on data characteristics.

**Q: Can I load multiple files?**
A: Yes, File → Open Multiple or drag & drop multiple files.

**Q: How do I merge datasets?**
A: Select series → Operations → Synchronization → Common Grid.

### Visualization Questions

**Q: How do I compare two series?**
A: Add both to same plot. For different scales, use multiple Y axes.

**Q: Can I export plots?**
A: Yes, right-click plot → Export. PNG, SVG, PDF supported.

**Q: How do I create animations?**
A: Enable streaming, then Tools → Export → Video.

### Calculation Questions

**Q: What interpolation method should I use?**
A: 
- **Linear**: Fast, good for most cases
- **Spline**: Smooth curves
- **PCHIP**: Preserves monotonicity

**Q: How accurate are derivatives?**
A: Uses numerical differentiation (finite differences). Accuracy depends on sampling rate and noise level.

**Q: Can I write custom operations?**
A: Yes, use plugin system. See [Plugin Development](PLUGIN_DEVELOPMENT.md).

---

## Support

### Documentation

- **User Guide**: This document
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)
- **Plugin Guide**: [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Community

- **GitHub Issues**: Report bugs
- **Discussions**: Ask questions, share tips
- **Wiki**: Community-contributed guides

### Getting Help

1. Check [FAQ](#faq) above
2. Read [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Search existing [GitHub Issues](https://github.com/thiagoarcan/Warp/issues)
4. Create new issue with:
   - Platform Base version
   - Operating system
   - Steps to reproduce
   - Error messages/screenshots

---

## Appendix

### Glossary

- **Series**: A sequence of values over time
- **Dataset**: Collection of related series
- **Decimation**: Reducing number of points for visualization
- **Interpolation**: Estimating values between known points
- **Synchronization**: Aligning multiple time series

### File Formats Details

#### CSV Structure
```
time,sensor_1,sensor_2
0.0,1.5,2.3
0.1,1.6,2.4
0.2,1.4,2.2
```

#### Excel Structure
- Sheet 1: Data (time + value columns)
- Sheet 2: Metadata (optional)

### Calculation Methods

**Derivative Methods**
- Forward difference
- Backward difference
- Central difference (default)

**Integral Methods**
- Trapezoidal rule (default)
- Simpson's rule
- Romberg integration

**Filter Types**
- Butterworth (smooth frequency response)
- Chebyshev (steeper roll-off)
- Bessel (linear phase)

---

*Platform Base v2.0 - User Guide*  
*Last Updated: 2026-02-02*  
*Copyright © 2026 Platform Base Team*
