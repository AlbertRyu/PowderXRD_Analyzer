# Powder XRD Analyzer

A Python tool for analyzing Powder XRD data from single crystal slab samples.
Calculates theoretical powder patterns from CIF files, identifies experimental peaks,
determines Miller indices (hkl), and estimates crystal orientation.

## Features

- **Read CIF files**: Load crystal structures using pymatgen
- **Calculate powder patterns**: Compute theoretical XRD patterns with configurable wavelength
- **Peak detection**: Advanced peak finding with background subtraction (SNIP algorithm)
- **Peak indexing**: Match experimental peaks with theoretical to determine hkl indices
- **Orientation analysis**: Determine single crystal slab orientation by pattern matching
- **Visualization**: Plot experimental vs calculated patterns with hkl labels
- **Support for Bruker .txt format**: Auto-detects common XRD data formats

## Installation

```bash
pip install -r requirements.txt
```

Or using uv:

```bash
uv sync
```

## Interactive Jupyter Notebook

An interactive Jupyter notebook is available at `examples/workflow.ipynb`:

```bash
cd examples
jupyter notebook workflow.ipynb
# or
jupyter lab
```

The notebook includes:
- Step-by-step interactive workflow
- Visualization at each step
- Simulated data demo if no real data is available
- Parameter tuning guidance

## Quick Start

### Command Line

```bash
# 1. Calculate powder pattern from CIF
python scripts/calculate_pattern.py --cif your_structure.cif

# 2. Find peaks in experimental data
python scripts/find_peaks.py --data your_xrd_data.txt --output peaks.png

# 3. Index peaks (match experimental with calculated pattern)
python scripts/index_peaks.py --cif your_structure.cif --data your_xrd_data.txt --output comparison.png

# 4. Analyze slab orientation
python scripts/analyze_orientation.py --cif your_structure.cif --data your_xrd_data.txt
```

### Python API

```python
import sys
sys.path.insert(0, '.')

from powder_xrd_analyzer import (
    read_cif, auto_read_xrd,
    calculate_powder_pattern,
    preprocess_xrd_data, find_xrd_peaks,
    match_peaks, print_indexed_peaks,
    analyze_slab_orientation, print_orientation_results,
    plot_comparison
)

# Read data
structure = read_cif("your_structure.cif")
tt, intensity = auto_read_xrd("your_xrd_data.txt")

# Find peaks
processed = preprocess_xrd_data(tt, intensity)
peak_tt, peak_int, _ = find_xrd_peaks(tt, processed)

# Calculate pattern and index peaks
pattern = calculate_powder_pattern(structure)
matches = match_peaks(peak_tt, pattern, tolerance=0.1)
print_indexed_peaks(matches)

# Analyze orientation
results = analyze_slab_orientation(structure, peak_tt, max_index=3)
print_orientation_results(results)

# Visualize
plot_comparison(tt, processed, pattern, matches)
```

## Modules

| Module | Purpose |
|--------|---------|
| `io.py` | Read CIF files and XRD data (Bruker .txt or two-column) |
| `pattern_calculator.py` | Calculate theoretical powder XRD patterns |
| `peak_finding.py` | Background subtraction and peak detection |
| `peak_matching.py` | Match peaks and determine Miller indices |
| `orientation.py` | Single crystal slab orientation analysis |
| `visualization.py` | Plotting utilities for comparison |

## Parameters

### Peak Finding
- `height_pct`: Minimum peak height as percentage of maximum intensity
- `prominence`: Peak prominence for noise rejection (higher = fewer peaks)
- `min_distance`: Minimum peak separation (data points)

### Peak Matching
- `tolerance`: Maximum 2θ difference for peak matching (degrees, default: 0.1)

### Orientation Analysis
- `max_index`: Maximum Miller index to consider (default: 3 = up to (333))
- `tolerance`: Peak matching tolerance for orientation scoring (default: 0.15)

## Example Data Format

### Bruker .txt Files
```
[Data]
"Angle","Intensity"
5.001,1234.5
5.021,1256.7
...
```

### Two-column Text Files
```
5.001 1234.5
5.021 1256.7
...
```

## Dependencies

- `pymatgen`: Core crystallographic calculations
- `numpy/scipy`: Numerical operations and peak finding
- `matplotlib`: Visualization
- `pandas`: Data handling

## License

MIT
