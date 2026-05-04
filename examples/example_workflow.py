#!/usr/bin/env python3
"""Example workflow for Powder XRD Analyzer."""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("POWDER XRD ANALYZER - EXAMPLE WORKFLOW")
print("=" * 70)

# Configuration - update these paths to your files
CIF_FILE = "your_structure.cif"
XRD_DATA = "your_xrd_data.txt"

print("\n" + "=" * 70)
print("STEP 1: Calculate powder pattern from CIF")
print("=" * 70)

try:
    from powder_xrd_analyzer.io import read_cif
    from powder_xrd_analyzer.pattern_calculator import calculate_powder_pattern, print_pattern_summary

    structure = read_cif(CIF_FILE)
    print(f"Structure: {structure.composition.reduced_formula}")
    print(f"Space group: {structure.get_space_group_info()[0]}")

    pattern = calculate_powder_pattern(structure, two_theta_range=(5, 90))
    print(f"\nCalculated {len(pattern.x)} peaks:")
    print_pattern_summary(pattern, n_peaks=20)

except FileNotFoundError:
    print(f"Note: {CIF_FILE} not found - this is just an example!")
    print("Replace CIF_FILE and XRD_DATA with your actual file paths.")
    print("Skipping to documentation...")


print("\n" + "=" * 70)
print("STEP 2: Find peaks in experimental data")
print("=" * 70)

print("""
from powder_xrd_analyzer.io import auto_read_xrd
from powder_xrd_analyzer.peak_finding import preprocess_xrd_data, find_xrd_peaks

tt, intensity = auto_read_xrd(XRD_DATA)
processed = preprocess_xrd_data(tt, intensity)
peak_tt, peak_int, peak_idx = find_xrd_peaks(tt, processed, height_pct=1.0)

print(f"Found {len(peak_tt)} peaks")
""")


print("\n" + "=" * 70)
print("STEP 3: Index peaks (match with calculated pattern)")
print("=" * 70)

print("""
from powder_xrd_analyzer.peak_matching import match_peaks, print_indexed_peaks

matches = match_peaks(peak_tt, pattern, tolerance=0.1)
print_indexed_peaks(matches)
""")


print("\n" + "=" * 70)
print("STEP 4: Analyze slab orientation")
print("=" * 70)

print("""
from powder_xrd_analyzer.orientation import analyze_slab_orientation, print_orientation_results

results = analyze_slab_orientation(structure, peak_tt, max_index=3)
print_orientation_results(results, n_top=5)
""")


print("\n" + "=" * 70)
print("COMMAND LINE USAGE")
print("=" * 70)

print("""
# 1. Calculate powder pattern from CIF
python scripts/calculate_pattern.py --cif your_structure.cif

# 2. Find peaks in experimental data
python scripts/find_peaks.py --data your_data.txt --output peaks.png

# 3. Index peaks by matching with CIF
python scripts/index_peaks.py --cif your_structure.cif --data your_data.txt --output comparison.png

# 4. Analyze slab orientation
python scripts/analyze_orientation.py --cif your_structure.cif --data your_data.txt
""")


print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
