#!/usr/bin/env python3
"""Calculate powder XRD pattern from a CIF file."""

import argparse
import sys
sys.path.insert(0, '.')

from powder_xrd_analyzer.io import read_cif
from powder_xrd_analyzer.pattern_calculator import calculate_powder_pattern, print_pattern_summary


def main():
    parser = argparse.ArgumentParser(description='Calculate powder XRD pattern from CIF file')
    parser.add_argument('--cif', required=True, help='Path to CIF file')
    parser.add_argument('--wavelength', default='CuKa', help='X-ray wavelength (default: CuKa)')
    parser.add_argument('--min-2theta', type=float, default=5, help='Minimum 2θ (default: 5)')
    parser.add_argument('--max-2theta', type=float, default=90, help='Maximum 2θ (default: 90)')
    parser.add_argument('--n-peaks', type=int, default=50, help='Number of peaks to display')
    args = parser.parse_args()

    print(f"Reading CIF file: {args.cif}")
    structure = read_cif(args.cif)
    print(f"Structure: {structure.composition.reduced_formula}")
    print(f"Space group: {structure.get_space_group_info()[0]}")

    print(f"\nCalculating powder pattern (wavelength={args.wavelength})...")
    pattern = calculate_powder_pattern(
        structure,
        wavelength=args.wavelength,
        two_theta_range=(args.min_2theta, args.max_2theta)
    )

    print(f"\nFound {len(pattern.x)} peaks:")
    print_pattern_summary(pattern, n_peaks=args.n_peaks)


if __name__ == '__main__':
    main()
