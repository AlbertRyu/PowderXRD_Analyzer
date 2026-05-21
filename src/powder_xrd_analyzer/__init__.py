"""Powder XRD Analyzer - CIF peak calculation and BRML plotting."""

from .io import read_cif, read_brml, get_brml_wavelength
from .pattern_calculator import calculate_powder_pattern, print_pattern_summary
from .visualization import plot_brml, plot_pattern, plot_pattern_with_hkl, plot_selected_hkl, plot_multiple_brml
from .webapp import create_app

__version__ = "0.1.0"
