import numpy as np
import pandas as pd
from io import StringIO
from pymatgen.io.cif import CifParser


def read_two_column_text(filename):
    """
    Read a simple two-column text file with 2θ and intensity.

    Args:
        filename: Path to text file

    Returns:
        tuple: (two_theta, intensity) as numpy arrays
    """
    data = np.loadtxt(filename)
    if data.ndim == 1:
        raise ValueError("File must have at least two columns")
    return data[:, 0], data[:, 1]


def read_bruker_xrd(filename):
    """
    Read Bruker .txt XRD file with [Data] section.

    The file format typically has:
    - Header lines with metadata
    - A [Data] marker
    - CSV data: "Angle","Intensity"

    Args:
        filename: Path to Bruker .txt file

    Returns:
        tuple: (two_theta, intensity) as numpy arrays
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    data_start = None
    for i, line in enumerate(lines):
        if '[Data]' in line:
            data_start = i + 2
            break

    if data_start is None:
        raise ValueError(f"Could not find [Data] section in {filename}")

    data_str = ''.join(lines[data_start:])
    df = pd.read_csv(StringIO(data_str), header=None, names=['Angle', 'Intensity'])

    return df['Angle'].values, df['Intensity'].values


def read_cif(filename, primitive=False):
    """
    Read a CIF file and return the Structure object.

    Args:
        filename: Path to CIF file
        primitive: If True, return primitive cell instead of conventional

    Returns:
        pymatgen.core.structure.Structure
    """
    parser = CifParser(filename)
    structures = parser.get_structures(primitive=primitive)

    if parser.warnings:
        for warning in parser.warnings:
            print(f"CIF Warning: {warning}")

    return structures[0]


def auto_read_xrd(filename):
    """
    Automatically detect and read XRD data file format.

    Tries Bruker format first, then falls back to two-column text.

    Args:
        filename: Path to XRD data file

    Returns:
        tuple: (two_theta, intensity) as numpy arrays
    """
    try:
        return read_bruker_xrd(filename)
    except (ValueError, Exception):
        try:
            return read_two_column_text(filename)
        except Exception as e:
            raise ValueError(f"Could not read {filename} as either Bruker or two-column format: {e}")
