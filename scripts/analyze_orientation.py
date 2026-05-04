#!/usr/bin/env python3
"""Analyze single crystal slab orientation from XRD data."""

import argparse
import sys
sys.path.insert(0, '.')

from powder_xrd_analyzer.io import read_cif, auto_read_xrd
from powder_xrd_analyzer.peak_finding import preprocess_xrd_data, find_xrd_peaks
from powder_xrd_analyzer.orientation import analyze_slab_orientation, print_orientation_results


def main():
    parser = argparse.ArgumentParser(description='Analyze single crystal slab orientation')
    parser.add_argument('--cif', required=True, help='Path to CIF file')
    parser.add_argument('--data', required=True, help='Path to experimental XRD data')
    parser.add_argument('--wavelength', default='CuKa', help='X-ray wavelength (default: CuKa)')
    parser.add_argument('--tolerance', type=float, default=0.15, help='Peak matching tolerance (default: 0.15°)')
    parser.add_argument('--max-index', type=int, default=3, help='Max Miller index to consider (default: 3)')
    parser.add_argument('--height-pct', type=float, default=1.0, help='Min peak height as % of max (default: 1.0)')
    parser.add_argument('--prominence', type=float, default=5.0, help='Peak prominence (default: 5.0)')
    parser.add_argument('--top-n', type=int, default=5, help='Number of top orientations to show (default: 5)')
    args = parser.parse_args()

    print(f"Reading CIF file: {args.cif}")
    structure = read_cif(args.cif)
    print(f"Structure: {structure.composition.reduced_formula}")
    print(f"Space group: {structure.get_space_group_info()[0]}")

    print(f"\nReading experimental data: {args.data}")
    tt, intensity = auto_read_xrd(args.data)

    print("Preprocessing...")
    processed = preprocess_xrd_data(tt, intensity)

    print("Finding peaks...")
    peak_tt, peak_int, _ = find_xrd_peaks(
        tt, processed, height_pct=args.height_pct, prominence=args.prominence
    )
    print(f"Found {len(peak_tt)} experimental peaks")

    print(f"\nAnalyzing orientations (max Miller index={args.max_index})...")
    print("This may take a minute...")
    results = analyze_slab_orientation(
        structure,
        peak_tt,
        max_index=args.max_index,
        tolerance=args.tolerance,
        wavelength=args.wavelength,
        two_theta_range=(tt[0], tt[-1])
    )

    print(f"\nTop {args.top_n} orientations:")
    print_orientation_results(results, n_top=args.top_n)

    if results:
        best = results[0]
        print(f"\nBest orientation: {best['miller_index']}")
        print(f"Peaks matched: {best['n_matched']}/{best['total_peaks']} ({best['match_ratio']:.1%})")
        print(f"Matched peak positions: {[f'{p:.2f}' for p in best['matched_peaks']]}")


if __name__ == '__main__':
    main()
