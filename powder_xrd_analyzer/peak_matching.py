import numpy as np


def match_peaks(observed_tt, calculated_pattern, tolerance=0.1):
    """
    Match observed peak positions with calculated pattern peaks.

    Args:
        observed_tt: numpy array of observed 2θ peak positions (degrees)
        calculated_pattern: DiffractionPattern from calculate_powder_pattern()
        tolerance: maximum 2θ difference for a match (degrees)

    Returns:
        list: List of match dictionaries with:
            - observed_2theta: observed 2θ position
            - calculated_2theta: matched calculated 2θ position
            - hkl: list of hkl dicts for this peak
            - d_spacing: d-spacing of the calculated peak
            - intensity_calc: calculated intensity
            - delta_2theta: 2θ difference between observed and calculated
    """
    matches = []

    for obs in observed_tt:
        diff = np.abs(calculated_pattern.x - obs)
        min_idx = np.argmin(diff)

        if diff[min_idx] < tolerance:
            matches.append({
                'observed_2theta': float(obs),
                'calculated_2theta': float(calculated_pattern.x[min_idx]),
                'hkl': calculated_pattern.hkls[min_idx],
                'd_spacing': float(calculated_pattern.d_hkls[min_idx]),
                'intensity_calc': float(calculated_pattern.y[min_idx]),
                'delta_2theta': float(diff[min_idx])
            })

    return matches


def hkl_to_string(hkl_dict):
    """Convert an hkl dict to a string like "(1,1,0)" -> "(110)"."""
    hkl = hkl_dict['hkl']
    return f"({hkl[0]}{hkl[1]}{hkl[2]})"


def print_indexed_peaks(matches, show_unmatched=True, observed_peaks=None):
    """
    Print a formatted table of indexed peaks.

    Args:
        matches: List of match dictionaries from match_peaks()
        show_unmatched: If True, also print unmatched peaks
        observed_peaks: Full list of observed peak 2θ positions (required for unmatched)
    """
    if not matches:
        print("No peaks matched!")
        return

    print(f"{'Obs. 2θ (°)':>12}  {'Calc. 2θ (°)':>12}  {'Δ2θ':>6}  {'d (Å)':>8}  {'Int.':>8}  {'hkl'}")
    print("-" * 80)

    for m in matches:
        hkl_str = ", ".join([hkl_to_string(h) for h in m['hkl']])
        print(
            f"{m['observed_2theta']:>12.3f}  "
            f"{m['calculated_2theta']:>12.3f}  "
            f"{m['delta_2theta']:>6.3f}  "
            f"{m['d_spacing']:>8.4f}  "
            f"{m['intensity_calc']:>8.1f}  "
            f"{hkl_str}"
        )

    print(f"\nTotal: {len(matches)} indexed peaks")

    if show_unmatched and observed_peaks is not None:
        matched_tt = {m['observed_2theta'] for m in matches}
        unmatched = [tt for tt in observed_peaks if tt not in matched_tt]
        if unmatched:
            print(f"\nUnmatched peaks ({len(unmatched)}):")
            for tt in unmatched:
                print(f"  {tt:>12.3f}")


def get_unique_miller_indices(matches):
    """
    Extract unique Miller indices from matched peaks.

    Args:
        matches: List of match dictionaries

    Returns:
        list: Unique (h,k,l) tuples
    """
    hkls = set()
    for m in matches:
        for hkl_dict in m['hkl']:
            hkls.add(hkl_dict['hkl'])
    return sorted(list(hkls))
