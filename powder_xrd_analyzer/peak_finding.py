import numpy as np
from scipy.signal import find_peaks, savgol_filter


def subtract_background_snip(intensity, iterations=20, window=2):
    """
    Subtract background using the SNIP algorithm.

    Statistics-sensitive Non-linear Iterative Peak-clipping (SNIP) algorithm
    iteratively estimates the background by taking the minimum of neighboring points.

    Args:
        intensity: numpy array of intensity values
        iterations: Number of iterations (more = more aggressive background removal)
        window: Window size for the minimum filter

    Returns:
        numpy array: background-subtracted intensity
    """
    bg = intensity.copy().astype(float)

    for _ in range(iterations):
        bg_new = bg.copy()
        for i in range(window, len(bg) - window):
            bg_new[i] = min(bg[i], (bg[i - window] + bg[i + window]) / 2)
        bg = bg_new

    return intensity - bg


def subtract_background_poly(two_theta, intensity, order=6, n_lowest=50):
    """
    Subtract background by fitting a polynomial to the lowest intensity points.

    Args:
        two_theta: numpy array of 2θ angles
        intensity: numpy array of intensity values
        order: polynomial order for background fitting
        n_lowest: number of lowest intensity points to use for background fit

    Returns:
        numpy array: background-subtracted intensity
    """
    idx = np.argsort(intensity)[:n_lowest]
    coeffs = np.polyfit(two_theta[idx], intensity[idx], order)
    bg = np.polyval(coeffs, two_theta)
    return intensity - bg


def subtract_background(intensity, method='snip', **kwargs):
    """
    Subtract background from XRD data.

    Args:
        intensity: numpy array of intensity values
        method: 'snip' or 'poly'
        **kwargs: Additional arguments for the background method

    Returns:
        numpy array: background-subtracted intensity
    """
    if method == 'snip':
        return subtract_background_snip(intensity, **kwargs)
    elif method == 'poly':
        if 'two_theta' not in kwargs:
            raise ValueError("two_theta must be provided for poly method")
        return subtract_background_poly(intensity=intensity, **kwargs)
    else:
        raise ValueError(f"Unknown background method: {method}")


def find_xrd_peaks(
    two_theta,
    intensity,
    height_pct=1.0,
    min_distance=5,
    prominence=5.0,
    width=None
):
    """
    Find peaks in XRD data using scipy's find_peaks.

    Args:
        two_theta: numpy array of 2θ angles
        intensity: numpy array of intensity values
        height_pct: minimum peak height as percentage of maximum intensity
        min_distance: minimum peak separation (number of data points)
        prominence: peak prominence for noise rejection
        width: minimum peak width (number of data points)

    Returns:
        tuple: (peak_tt, peak_int, peak_indices) - 2θ positions, intensities, and indices
    """
    height_threshold = height_pct * np.max(intensity) / 100.0

    peaks, props = find_peaks(
        intensity,
        height=height_threshold,
        distance=min_distance,
        prominence=prominence,
        width=width
    )

    return two_theta[peaks], intensity[peaks], peaks


def smooth_data(intensity, window_length=11, polyorder=3):
    """
    Smooth intensity data using Savitzky-Golay filter.

    Args:
        intensity: numpy array of intensity values
        window_length: window size for smoothing (must be odd)
        polyorder: polynomial order for smoothing

    Returns:
        numpy array: smoothed intensity
    """
    if window_length % 2 == 0:
        window_length += 1

    return savgol_filter(intensity, window_length=window_length, polyorder=polyorder)


def preprocess_xrd_data(
    two_theta,
    intensity,
    smooth=True,
    smooth_window=11,
    bg_method='snip',
    bg_iterations=20
):
    """
    Preprocess XRD data: smoothing and background subtraction.

    Args:
        two_theta: numpy array of 2θ angles
        intensity: numpy array of intensity values
        smooth: If True, apply Savitzky-Golay smoothing
        smooth_window: window size for smoothing
        bg_method: background subtraction method ('snip' or 'poly')
        bg_iterations: iterations for SNIP background subtraction

    Returns:
        tuple: (processed_intensity) - background-subtracted, smoothed intensity
    """
    processed = intensity.copy()

    if smooth:
        processed = smooth_data(processed, window_length=smooth_window)

    if bg_method == 'snip':
        processed = subtract_background_snip(processed, iterations=bg_iterations)
    elif bg_method == 'poly':
        processed = subtract_background_poly(two_theta, processed)

    return processed
