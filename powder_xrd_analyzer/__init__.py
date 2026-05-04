from .io import read_bruker_xrd, read_cif, read_two_column_text, auto_read_xrd
from .pattern_calculator import calculate_powder_pattern, get_xrd_calculator, print_pattern_summary
from .peak_finding import subtract_background, find_xrd_peaks, preprocess_xrd_data, smooth_data
from .peak_matching import match_peaks, print_indexed_peaks, get_unique_miller_indices
from .orientation import analyze_slab_orientation, print_orientation_results
from .visualization import plot_comparison, plot_peaks, plot_peak_matching_summary, save_figure

__version__ = "0.1.0"
