#!/usr/bin/env python3
"""Find peaks in experimental XRD data."""

import argparse
import sys
sys.path.insert(0, '.')

import matplotlib.pyplot as plt
from powder_xrd_analyzer.io import auto_read_xrd
from powder_xrd_analyzer.peak_finding import preprocess_xrd_data, find_xrd_peaks
from powder_xrd_analyzer.visualization import plot_peaks, save_figure


def main():
    parser = argparse.ArgumentParser(description='Find peaks in XRD data')
    parser.add_argument('--data', required=True, help='Path to XRD data file')
    parser.add_argument('--height-pct', type=float, default=1.0, help='Min peak height as % of max (default: 1.0)')
    parser.add_argument('--prominence', type=float, default=5.0, help='Peak prominence (default: 5.0)')
    parser.add_argument('--min-distance', type=int, default=5, help='Min peak separation (data points, default: 5)')
    parser.add_argument('--no-bg-sub', action='store_true', help='Skip background subtraction')
    parser.add_argument('--output', help='Save plot to file (e.g., peaks.png)')
    args = parser.parse_args()

    print(f"Reading XRD data: {args.data}")
    tt, intensity = auto_read_xrd(args.data)
    print(f"Data range: {tt[0]:.2f}° - {tt[-1]:.2f}° ({len(tt)} points)")

    if not args.no_bg_sub:
        print("Preprocessing: smoothing and background subtraction...")
        processed = preprocess_xrd_data(tt, intensity)
    else:
        processed = intensity

    print(f"\nFinding peaks (height={args.height_pct}%, prominence={args.prominence})...")
    peak_tt, peak_int, peak_idx = find_xrd_peaks(
        tt,
        processed,
        height_pct=args.height_pct,
        min_distance=args.min_distance,
        prominence=args.prominence
    )

    print(f"\nFound {len(peak_tt)} peaks:")
    print(f"{'Peak':>6}  {'2θ (°)':>10}  {'Intensity':>12}")
    print("-" * 35)
    for i, (p_tt, p_int) in enumerate(zip(peak_tt, peak_int)):
        print(f"{i+1:>6}  {p_tt:>10.3f}  {p_int:>12.2f}")

    fig = plot_peaks(tt, processed, peak_tt, peak_int, title=f"Peak Detection: {args.data}")

    if args.output:
        save_figure(fig, args.output)
        print(f"\nPlot saved to: {args.output}")
    else:
        plt.show()


if __name__ == '__main__':
    main()
