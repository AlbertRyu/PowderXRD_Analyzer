import numpy as np
from pymatgen.core.surface import SlabGenerator, get_symmetrically_distinct_miller_indices
from pymatgen.analysis.diffraction.xrd import XRDCalculator


def analyze_slab_orientation(
    structure,
    experimental_peaks,
    max_index=3,
    tolerance=0.15,
    wavelength="CuKa",
    two_theta_range=(5, 90),
    min_slab_size=10,
    min_vacuum_size=15
):
    """
    Determine the orientation of a single crystal slab by matching XRD peak patterns.

    Generates symmetrically-distinct slab orientations, calculates the XRD pattern
    for each, and scores based on how many experimental peaks match.

    Args:
        structure: pymatgen Structure object (bulk crystal)
        experimental_peaks: numpy array of observed 2θ peak positions
        max_index: maximum Miller index to consider (e.g., 3 = up to (333))
        tolerance: 2θ matching tolerance in degrees
        wavelength: X-ray wavelength for XRD calculation
        two_theta_range: 2θ range for calculation
        min_slab_size: minimum slab thickness in Angstroms
        min_vacuum_size: minimum vacuum layer thickness in Angstroms

    Returns:
        list: Sorted list of orientation dictionaries (best match first):
            - miller_index: (h,k,l) tuple
            - n_matched: number of matched peaks
            - total_peaks: total number of experimental peaks
            - match_ratio: fraction of peaks matched
            - matched_peaks: list of matched peak 2θ values
    """
    miller_indices = get_symmetrically_distinct_miller_indices(structure, max_index)

    xrd_calc = XRDCalculator(wavelength=wavelength)
    results = []

    for hkl in miller_indices:
        try:
            slab_gen = SlabGenerator(
                structure,
                miller_index=hkl,
                min_slab_size=min_slab_size,
                min_vacuum_size=min_vacuum_size,
                lll_reduce=True
            )

            slabs = slab_gen.get_slabs()

            for j, slab in enumerate(slabs):
                pattern = xrd_calc.get_pattern(slab, two_theta_range=two_theta_range)

                matched_peaks = []
                for obs in experimental_peaks:
                    if np.any(np.abs(pattern.x - obs) < tolerance):
                        matched_peaks.append(float(obs))

                results.append({
                    'miller_index': hkl,
                    'termination': j,
                    'slab': slab,
                    'n_matched': len(matched_peaks),
                    'total_peaks': len(experimental_peaks),
                    'match_ratio': len(matched_peaks) / len(experimental_peaks) if len(experimental_peaks) > 0 else 0,
                    'matched_peaks': matched_peaks
                })

        except Exception as e:
            print(f"Warning: Could not process orientation {hkl}: {e}")
            continue

    return sorted(results, key=lambda x: x['match_ratio'], reverse=True)


def print_orientation_results(results, n_top=5):
    """
    Print orientation analysis results.

    Args:
        results: List of orientation results from analyze_slab_orientation()
        n_top: Number of top results to print
    """
    if not results:
        print("No orientation results found!")
        return

    print(f"{'Rank':>5}  {'Miller':>8}  {'Term.':>5}  {'Matched':>8}  {'Total':>6}  {'Ratio':>8}")
    print("-" * 60)

    for i, result in enumerate(results[:n_top]):
        hkl_str = f"({result['miller_index'][0]}{result['miller_index'][1]}{result['miller_index'][2]})"
        print(
            f"{i+1:>5}  "
            f"{hkl_str:>8}  "
            f"{result['termination']:>5}  "
            f"{result['n_matched']:>8}  "
            f"{result['total_peaks']:>6}  "
            f"{result['match_ratio']:>8.1%}"
        )

    print(f"\nBest candidate orientation: {results[0]['miller_index']} "
          f"({results[0]['match_ratio']:.1%} peaks matched)")


def get_orientation_hkl_likelihood(results):
    """
    Get a dictionary of Miller index -> likelihood based on peak matching.

    Args:
        results: List of orientation results

    Returns:
        dict: {(h,k,l): match_ratio}
    """
    hkl_likelihood = {}
    for r in results:
        hkl = r['miller_index']
        if hkl not in hkl_likelihood or r['match_ratio'] > hkl_likelihood[hkl]:
            hkl_likelihood[hkl] = r['match_ratio']
    return hkl_likelihood
