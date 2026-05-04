#!/usr/bin/env python3
"""Index experimental XRD peaks by matching to calculated pattern from CIF."""

import argparse
import sys
sys.path.insert(0, '.')

import matplotlib.pyplot as plt
from powder_xrd_analyzer.io import read_cif, auto_read_xrd
from powder_xrd_analyzer.pattern_calculator import calculate_powder_pattern
from powder_xrd_analyzer.peak_finding import preprocess_xrd_data, find_xrd_peaks
from powder_xrd_analyzer.peak_matching import match_peaks, print_indexed_peaks
from powder_xrd_analyzer.visualization import plot_comparison, save_figure


def main():
    parser = argparse.ArgumentParser(description='Index XRD peaks by matching to calculated pattern')
    parser.add_argument('--cif', required=True, help='Path to CIF file')
    parser.add_argument('--data', required=True, help='Path to experimental XRD data')
    parser.add_argument('--wavelength', default='CuKa', help='X-ray wavelength (default: CuKa)')
    parser.add_argument('--tolerance', type=float, default=0.1, help='Peak matching tolerance (default: 0.1°)')
    parser.add_argument('--height-pct', type=float, default=1.0, help='Min peak height as % of max (default: 1.0)')
    parser.add_argument('--prominence', type=float, default=5.0, help='Peak prominence (default: 5.0)')
    parser.add_argument('--output', help='Save comparison plot to file')
    args = parser.parse_args()

    print(f"Reading CIF file: {args.cif}")
    structure = read_cif(args.cif)
    print(f"Structure: {structure.composition.reduced_formula}")
    print(f"Space group: {structure.get_space_group_info()[0]}")

    print(f"\nReading experimental data: {args.data}")
    tt, intensity = auto_read_xrd(args.data)

    print("Preprocessing experimental data...")
    processed = preprocess_xrd_data(tt, intensity)

    print("Finding peaks...")
    peak_tt, peak_int, _ = find_xrd_peaks(
        tt, processed, height_pct=args.height_pct, prominence=args.prominence
    )
    print(f"Found {len(peak_tt)} experimental peaks")

    print("\nCalculating powder pattern...")
    calc_pattern = calculate_powder_pattern(
        structure,
        wavelength=args.wavelength,
        two_theta_range=(tt[0], tt[-1])
    )
    print(f"Calculated pattern has {len(calc_pattern.x)} peaks")

    print(f"\nMatching peaks (tolerance={args.tolerance}°)...")
    matches = match_peaks(peak_tt, calc_pattern, tolerance=args.tolerance)

    print("\nIndexed Peaks:")
    print_indexed_peaks(matches, show_unmatched=True, observed_peaks=peak_tt)

    fig = plot_comparison(tt, processed, calc_pattern, matches)

    if args.output:
        save_figure(fig, args.output)
        print(f"\nPlot saved to: {args.output}")
    else:
        plt.show()


if __name__ == '__main__':
    main()
