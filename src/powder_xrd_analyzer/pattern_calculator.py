"""Calculate powder XRD patterns from CIF files (VESTA-style)."""

from pymatgen.analysis.diffraction.xrd import XRDCalculator


def get_xrd_calculator(wavelength="CuKa", symprec=0.1, debye_waller_factors=None):
    """
    Create an XRDCalculator instance with specified parameters.

    Args:
        wavelength: X-ray wavelength. Can be string ("CuKa", "CuKa1", "MoKa")
                    or float in angstroms
        symprec: Symmetry precision for space group determination
        debye_waller_factors: Dict of {element: factor} for Debye-Waller correction

    Returns:
        pymatgen.analysis.diffraction.xrd.XRDCalculator
    """
    return XRDCalculator(
        wavelength=wavelength,
        symprec=symprec,
        debye_waller_factors=debye_waller_factors
    )


def calculate_powder_pattern(
    structure,
    wavelength="CuKa1",
    two_theta_range=(5, 90),
    scaled=True,
    symprec=None
):
    """
    Calculate powder XRD pattern from a Structure object (VESTA-style).

    This function uses pymatgen's XRDCalculator to compute diffraction peaks
    with the same approach used by VESTA (preserves original CIF axis order).

    Args:
        structure: pymatgen Structure object
        wavelength: X-ray wavelength (string or float in angstroms).
                    Default "CuKa1" (1.54056Å) matches VESTA's default.
                    Use "CuKa" (1.54184Å) for weighted average of Kα1+Kα2.
        two_theta_range: Tuple of (min, max) 2θ in degrees, or None for all
        scaled: If True, scale maximum intensity to 100
        symprec: Symmetry precision. Default None = no space group normalization
                 (preserves original CIF axis order, matches VESTA indexing)

    Returns:
        pymatgen.analysis.diffraction.xrd.DiffractionPattern with attributes:
            - x: numpy array of 2θ angles (degrees)
            - y: numpy array of relative intensities
            - hkls: List of hkl info: [{'hkl': (h,k,l), 'multiplicity': N}, ...]
            - d_hkls: numpy array of d-spacings in angstroms
    """
    calc = get_xrd_calculator(wavelength=wavelength, symprec=symprec)
    pattern = calc.get_pattern(
        structure,
        scaled=scaled,
        two_theta_range=two_theta_range
    )
    return pattern


def print_pattern_summary(pattern, n_peaks=None):
    """
    Print a summary of the calculated powder pattern (VESTA style).

    Args:
        pattern: DiffractionPattern from calculate_powder_pattern
        n_peaks: Number of peaks to print (print all if None)
    """
    n = n_peaks if n_peaks is not None else len(pattern.x)
    print(f"{'No.':>4}  {'h':>4}  {'k':>4}  {'l':>4}  {'d (Å)':>10}  {'2θ (°)':>10}  {'I':>8}")
    print("-" * 65)

    for i in range(min(n, len(pattern.x))):
        hkl = pattern.hkls[i][0]['hkl'] if pattern.hkls[i] else (0, 0, 0)
        print(f"{i+1:4d}  {hkl[0]:4d}  {hkl[1]:4d}  {hkl[2]:4d}  {pattern.d_hkls[i]:>10.5f}  {pattern.x[i]:>10.4f}  {pattern.y[i]:>8.4f}")

    if n_peaks is not None and n_peaks < len(pattern.x):
        print(f"... and {len(pattern.x) - n_peaks} more peaks")
