#!/usr/bin/env python
"""Example usage of Powder XRD Analyzer."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for saving plots

from powder_xrd_analyzer import (
    read_cif,
    calculate_powder_pattern,
    print_pattern_summary,
    read_brml,
    plot_brml,
    plot_pattern_with_hkl,
    plot_selected_hkl,
)


def example_cif_calculation():
    """Example: Read CIF file and calculate theoretical powder pattern."""
    print("=" * 60)
    print("EXAMPLE 1: Calculate Pattern from CIF")
    print("=" * 60)

    # Read CIF file
    cif_file = "cif_files/4F-Mn-BA_centro_pbnm.cif"
    print(f"\nReading CIF file: {cif_file}")
    structure = read_cif(cif_file)
    print(f"Formula: {structure.composition.reduced_formula}")
    print(f"Space group: {structure.get_space_group_info()[0]}")
    print(f"Lattice: {structure.lattice}")

    # Calculate powder pattern
    print("\nCalculating powder pattern (Cu Ka radiation)...")
    pattern = calculate_powder_pattern(
        structure, wavelength="CuKa", two_theta_range=(5, 80)
    )

    # Print summary
    print(f"\nFound {len(pattern.x)} peaks:")
    print_pattern_summary(pattern, n_peaks=15)

    # Save full pattern plot
    print("\nSaving plot with hkl labels...")
    fig = plot_pattern_with_hkl(pattern, title="Calculated Powder XRD Pattern (Cu Ka1)")
    fig.savefig("calculated_pattern.png", dpi=150, bbox_inches="tight")
    print("Saved: calculated_pattern.png")

    # Plot only selected 00l peaks (layer stacking direction)
    print("\nPlotting only 00l series peaks...")
    selected_hkl = [(0,0,2), (0,0,4), (0,0,6), (0,0,8), (0,0,10)]
    fig2 = plot_selected_hkl(pattern, selected_hkl,
                            title="Selected (00l) Series Peaks",
                            color='darkred', linewidth=3)
    fig2.savefig("00l_peaks.png", dpi=150, bbox_inches="tight")
    print("Saved: 00l_peaks.png")


def example_brml_plotting():
    """Example: Read BRML file and plot experimental data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Plot BRML Data")
    print("=" * 60)

    # Read BRML file
    brml_file = "20260422/D2-210721_3620_260422_142117.brml"
    print(f"\nReading BRML file: {brml_file}")
    two_theta, intensity = read_brml(brml_file)

    print(f"Data points: {len(two_theta)}")
    print(f"2θ range: {two_theta.min():.1f}° - {two_theta.max():.1f}°")
    print(f"Intensity range: {intensity.min():.0f} - {intensity.max():.0f}")

    # Save plot
    print("\nSaving BRML plot...")
    fig = plot_brml(
        two_theta, intensity, title="Experimental XRD Pattern from BRML File"
    )
    fig.savefig("brml_pattern.png", dpi=150, bbox_inches="tight")
    print("Saved: brml_pattern.png")


if __name__ == "__main__":
    example_cif_calculation()
    example_brml_plotting()
    print("\n" + "=" * 60)
    print("Done! Check output images saved.")
    print("=" * 60)
