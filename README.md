# Powder XRD Analyzer

A minimal Python tool for:
1. **Reading CIF files and calculating theoretical powder XRD patterns** (VESTA-style)
2. **Reading Bruker BRML files and plotting experimental XRD data**

## Features

- **CIF processing**: Read crystal structures using pymatgen
- **Pattern calculation**: Compute theoretical powder XRD patterns with configurable wavelength
- **hkl labeling**: Display Miller indices on calculated pattern plots
- **BRML support**: Read Bruker .brml (XML-based) measurement files
- **Visualization**: Plot experimental patterns from BRML files
- **Web application**: Browse `.brml` files and plot them through a FastAPI + uvicorn SPA

## Installation

```bash
uv sync
```

## Quick Start

### Start the Web App

```bash
uv sync
uv run powderxrd-webapp --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000`.

The web app provides a single workspace view:
- **Left panel**: recursively scans the current directory and lists all `.brml` files
- **Right panel**: renders the selected `.brml` files in the same plot for direct comparison
- **Multi-select**: click multiple files to overlay several XRD curves at once
- **Experiment metadata**: if `experiment_record.csv` exists in the scanned root, file cards show `exp-id`, `sample`, and `comment`
- **Sample filter**: narrow the file list by sample name from `experiment_record.csv`
- **CIF overlay**: read `.cif` files from `cifs/`, calculate powder patterns, and overlay requested `hkl` peaks on the experimental plot

To scan a different directory:

```bash
uv run powderxrd-webapp --root /path/to/data --host 0.0.0.0 --port 8000
```

### Calculate Pattern from CIF

```python
from powder_xrd_analyzer import read_cif, calculate_powder_pattern, print_pattern_summary, plot_pattern_with_hkl

# Read CIF and calculate pattern
structure = read_cif("cif_files/your_structure.cif")
pattern = calculate_powder_pattern(structure, wavelength="CuKa", two_theta_range=(5, 90))

# Print summary of peaks
print_pattern_summary(pattern, n_peaks=20)

# Plot pattern with hkl labels
fig = plot_pattern_with_hkl(pattern)
fig.savefig("calculated_pattern.png", dpi=150)
```

### Plot BRML Data

```python
from powder_xrd_analyzer import read_brml, plot_brml

# Read BRML file
two_theta, intensity = read_brml("data/your_measurement.brml")

# Plot pattern
fig = plot_brml(two_theta, intensity, title="Your XRD Data")
fig.savefig("brml_plot.png", dpi=150)
```

## API Reference

### `read_cif(filename, primitive=False)`
Read a CIF file and return a pymatgen Structure object.

### `calculate_powder_pattern(structure, wavelength="CuKa", two_theta_range=(5, 90), scaled=True, symprec=0.1)`
Calculate theoretical powder XRD pattern. Returns a DiffractionPattern object with:
- `.x`: numpy array of 2θ angles (degrees)
- `.y`: numpy array of relative intensities
- `.hkls`: hkl indices information
- `.d_hkls`: d-spacings in angstroms

### `print_pattern_summary(pattern, n_peaks=None)`
Print a formatted summary of calculated peaks.

### `read_brml(filename)`
Read a Bruker BRML file. Returns `(two_theta, intensity)` as numpy arrays.

### `plot_brml(two_theta, intensity, figsize=(12, 5), title="XRD Pattern", **kwargs)`
Plot experimental XRD pattern.

### `plot_pattern(pattern, figsize=(12, 5), title="Calculated XRD Pattern", color="red", linewidth=2)`
Plot calculated pattern as vertical lines.

### `plot_pattern_with_hkl(pattern, figsize=(14, 6), title="Calculated XRD Pattern", color="red", linewidth=2, label_intensity_threshold=5)`
Plot calculated pattern with hkl indices labeled above peaks.
