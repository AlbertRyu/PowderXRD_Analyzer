"""Visualization functions for XRD data."""

import matplotlib.pyplot as plt
import numpy as np


def plot_brml(two_theta, intensity, figsize=(12, 5), title="XRD Pattern", **kwargs):
    """
    Plot XRD pattern from BRML file data.

    Args:
        two_theta: numpy array of 2θ angles (degrees)
        intensity: numpy array of intensity values
        figsize: Figure size tuple
        title: Plot title
        **kwargs: Additional arguments passed to plt.plot()

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(two_theta, intensity, **kwargs)
    ax.set_xlabel('2θ (degrees)', fontsize=12)
    ax.set_ylabel('Intensity', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    return fig


def plot_pattern(pattern, figsize=(12, 5), title="Calculated XRD Pattern",
                 color='red', linewidth=2):
    """
    Plot calculated powder XRD pattern as vertical lines (VESTA style).

    Args:
        pattern: DiffractionPattern from calculate_powder_pattern()
        figsize: Figure size tuple
        title: Plot title
        color: Color of the peak lines
        linewidth: Width of the peak lines

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    for i, (tt, inten) in enumerate(zip(pattern.x, pattern.y)):
        ax.vlines(tt, 0, inten, color=color, linewidth=linewidth)

    ax.set_xlabel('2θ (degrees)', fontsize=12)
    ax.set_ylabel('Relative Intensity', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    return fig


def plot_pattern_with_hkl(pattern, figsize=(14, 6), title="Calculated XRD Pattern",
                          color='red', linewidth=2, label_intensity_threshold=5):
    """
    Plot calculated powder XRD pattern with hkl indices labeled above peaks (VESTA style).

    Args:
        pattern: DiffractionPattern from calculate_powder_pattern()
        figsize: Figure size tuple
        title: Plot title
        color: Color of the peak lines
        linewidth: Width of the peak lines
        label_intensity_threshold: Minimum intensity to show hkl label

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    for i, (tt, inten) in enumerate(zip(pattern.x, pattern.y)):
        ax.vlines(tt, 0, inten, color=color, linewidth=linewidth)

        if inten >= label_intensity_threshold and pattern.hkls[i]:
            hkl = pattern.hkls[i][0]['hkl']
            hkl_str = str(hkl[0]) + ' ' + str(hkl[1]) + ' ' + str(hkl[2])
            ax.text(tt, inten + 2, hkl_str, rotation=90,
                    ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('2θ (degrees)', fontsize=12)
    ax.set_ylabel('Relative Intensity', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    return fig


def plot_selected_hkl(pattern, hkl_list, figsize=(14, 6), title="Selected XRD Peaks",
                      color='blue', linewidth=3, show_labels=True, dpi=None):
    """
    Plot only specific hkl peaks from the calculated pattern.

    Args:
        pattern: DiffractionPattern from calculate_powder_pattern()
        hkl_list: List of hkl tuples to plot, e.g., [(0,0,2), (0,0,4), (0,2,0)]
        figsize: Figure size tuple
        title: Plot title
        color: Color of the peak lines
        linewidth: Width of the peak lines
        show_labels: If True, show hkl labels above peaks
        dpi: DPI for the figure (optional)

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    hkl_set = set(hkl_list)
    max_inten = 0

    for i, (tt, inten) in enumerate(zip(pattern.x, pattern.y)):
        if pattern.hkls[i]:
            hkl = pattern.hkls[i][0]['hkl']
            if hkl in hkl_set:
                ax.vlines(tt, 0, inten, color=color, linewidth=linewidth)
                max_inten = max(max_inten, inten)

                if show_labels:
                    hkl_str = str(hkl[0]) + ' ' + str(hkl[1]) + ' ' + str(hkl[2])
                    ax.text(tt, inten + 2, hkl_str, rotation=90,
                            ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('2θ (degrees)', fontsize=12)
    ax.set_ylabel('Relative Intensity', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(pattern.x.min(), pattern.x.max())
    ax.set_ylim(bottom=0, top=max_inten * 1.15 if max_inten > 0 else None)
    plt.tight_layout()
    return fig
