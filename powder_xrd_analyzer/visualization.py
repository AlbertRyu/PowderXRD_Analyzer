import numpy as np
import matplotlib.pyplot as plt


def plot_comparison(
    obs_x,
    obs_y,
    calc_pattern,
    matches=None,
    figsize=(14, 8),
    title="Experimental vs Calculated XRD Pattern"
):
    """
    Plot experimental vs calculated XRD patterns with optional hkl labels.

    Args:
        obs_x: numpy array of experimental 2θ angles
        obs_y: numpy array of experimental intensities
        calc_pattern: DiffractionPattern from calculate_powder_pattern()
        matches: List of match dictionaries from match_peaks() (optional)
        figsize: Figure size tuple
        title: Plot title

    Returns:
        matplotlib Figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

    ax1.plot(obs_x, obs_y, 'b-', label='Experimental', linewidth=0.8)
    ax1.set_ylabel('Intensity', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(alpha=0.3, linestyle='--')
    ax1.set_title(title, fontsize=14, pad=15)

    ax2.vlines(calc_pattern.x, 0, calc_pattern.y, 'r', label='Calculated', linewidth=2)
    ax2.set_xlabel('2θ (degrees)', fontsize=12)
    ax2.set_ylabel('Relative Intensity', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(alpha=0.3, linestyle='--')

    if matches:
        matched_tt = set()
        for m in matches:
            ax1.axvline(m['observed_2theta'], color='g', alpha=0.3, linestyle='--')
            matched_tt.add(m['calculated_2theta'])

        for i, calc_tt in enumerate(calc_pattern.x):
            if calc_tt in matched_tt:
                hkl_str = ''.join([str(h['hkl'][j]) for j in range(3) for h in calc_pattern.hkls[i]][:3])
                ax2.text(
                    calc_tt,
                    calc_pattern.y[i] + 2,
                    f'({hkl_str})',
                    rotation=90,
                    ha='center',
                    va='bottom',
                    fontsize=8
                )

    plt.xlim(np.min(obs_x), np.max(obs_x))
    plt.tight_layout()

    return fig


def plot_peaks(
    two_theta,
    intensity,
    peak_tt=None,
    peak_int=None,
    figsize=(12, 5),
    title="XRD Pattern with Detected Peaks"
):
    """
    Plot XRD pattern with detected peak positions.

    Args:
        two_theta: numpy array of 2θ angles
        intensity: numpy array of intensity values
        peak_tt: numpy array of peak 2θ positions (optional)
        peak_int: numpy array of peak intensities (optional)
        figsize: Figure size tuple
        title: Plot title

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    ax.plot(two_theta, intensity, 'b-', label='Pattern', linewidth=0.8)

    if peak_tt is not None and peak_int is not None:
        ax.plot(peak_tt, peak_int, 'ro', markersize=6, label='Detected Peaks', zorder=5)

    ax.set_xlabel('2θ (degrees)', fontsize=12)
    ax.set_ylabel('Intensity', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()

    return fig


def plot_peak_matching_summary(
    matches,
    figsize=(10, 6),
    title="Peak Matching Summary"
):
    """
    Plot a bar chart showing the delta 2θ for each matched peak.

    Args:
        matches: List of match dictionaries from match_peaks()
        figsize: Figure size tuple
        title: Plot title

    Returns:
        matplotlib Figure
    """
    if not matches:
        raise ValueError("No matches to plot")

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    hkl_labels = []
    deltas = []
    for m in matches:
        hkl = m['hkl'][0]['hkl']
        hkl_labels.append(f"({hkl[0]}{hkl[1]}{hkl[2]})")
        deltas.append(m['delta_2theta'])

    x_pos = np.arange(len(deltas))
    bars = ax.bar(x_pos, deltas, align='center', alpha=0.7)

    ax.set_xlabel('hkl', fontsize=12)
    ax.set_ylabel('Δ 2θ (degrees)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(hkl_labels, rotation=90)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    for bar, delta in zip(bars, deltas):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{delta:.3f}",
            ha='center',
            va='bottom',
            fontsize=8
        )

    plt.tight_layout()

    return fig


def save_figure(fig, filename, dpi=300):
    """
    Save a figure to file.

    Args:
        fig: matplotlib Figure
        filename: Output filename
        dpi: Resolution in DPI
    """
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
