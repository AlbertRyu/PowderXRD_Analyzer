"""Example usage of Powder XRD Analyzer."""

from powder_xrd_analyzer import read_cif, read_brml
from powder_xrd_analyzer import calculate_powder_pattern, print_pattern_summary
from powder_xrd_analyzer import plot_brml, plot_pattern_with_hkl

# Example 1: Read CIF and calculate peaks
structure = read_cif("cif_files/4H-Mn-BA_mo_0m_a.cif")
pattern = calculate_powder_pattern(structure, two_theta_range=(5, 80))
print_pattern_summary(pattern, n_peaks=10)
fig = plot_pattern_with_hkl(pattern)
fig.savefig("calculated_pattern.png", dpi=150)
print("Saved calculated_pattern.png")

# Example 2: Read BRML and plot
two_theta, intensity = read_brml("20260422/D2-210721_3619_260422_132758.brml")
print(f"\nLoaded BRML data: {len(two_theta)} points from {two_theta.min():.1f}° to {two_theta.max():.1f}°")
fig2 = plot_brml(two_theta, intensity)
fig2.savefig("brml_pattern.png", dpi=150)
print("Saved brml_pattern.png")
