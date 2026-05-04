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
    wavelength="CuKa",
    two_theta_range=(5, 90),
    scaled=True,
    symprec=0.1
):
    """
    Calculate powder XRD pattern from a Structure object.

    Args:
        structure: pymatgen Structure object
        wavelength: X-ray wavelength (string or float in angstroms)
        two_theta_range: Tuple of (min, max) 2θ in degrees, or None for all
        scaled: If True, scale maximum intensity to 100
        symprec: Symmetry precision

    Returns:
        pymatgen.analysis.diffraction.xrd.DiffractionPattern with attributes:
            - x: numpy array of 2θ angles (degrees)
            - y: numpy array of intensities
            - hkls: List of hkl info: [{'hkl': (h,k,l), 'multiplicity': N}, ...]
            - d_hkls: numpy array of d-spacings
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
    Print a summary of the calculated powder pattern.

    Args:
        pattern: DiffractionPattern from calculate_powder_pattern
        n_peaks: Number of peaks to print (print all if None)
    """
    n = n_peaks if n_peaks is not None else len(pattern.x)
    print(f"{'2θ (°)':>10}  {'Intensity':>10}  {'d (Å)':>8}  {'hkl'}")
    print("-" * 60)

    for i in range(min(n, len(pattern.x))):
        hkl_str = ", ".join([str(h['hkl']) for h in pattern.hkls[i]])
        print(f"{pattern.x[i]:>10.3f}  {pattern.y[i]:>10.2f}  {pattern.d_hkls[i]:>8.4f}  ({hkl_str})")

    if n_peaks is not None and n_peaks < len(pattern.x):
        print(f"... and {len(pattern.x) - n_peaks} more peaks")
