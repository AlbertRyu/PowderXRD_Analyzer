"""Input/output functions for CIF and BRML files."""

import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from pymatgen.io.cif import CifParser


def get_brml_wavelength(filename):
    """
    Extract X-ray wavelength information from a BRML file.

    Args:
        filename: Path to .brml file

    Returns:
        dict: Dictionary with tube material and wavelength info
              e.g., {'tube_material': 'Cu', 'wavelength_known': True}
    """
    with zipfile.ZipFile(filename, 'r') as zf:
        for name in zf.namelist():
            if 'InstructionContainer' in name or 'MeasurementContainer' in name:
                with zf.open(name) as f:
                    content = f.read().decode('utf-8')
                    if 'TubeMaterial Value="' in content:
                        idx = content.find('TubeMaterial Value="')
                        if idx >= 0:
                            end_idx = content.find('"', idx + len('TubeMaterial Value="'))
                            material = content[idx + len('TubeMaterial Value="'):end_idx]
                            return {
                                'tube_material': material,
                                'common_wavelengths': {
                                    'Cu': {'Ka1': 1.54056, 'Ka2': 1.54439, 'Ka_avg': 1.54184},
                                    'Mo': {'Ka1': 0.70930, 'Ka2': 0.71359, 'Ka_avg': 0.71073},
                                }[material] if material in ['Cu', 'Mo'] else None
                            }
    return {'tube_material': 'unknown'}


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
    structures = parser.parse_structures(primitive=primitive)

    if parser.warnings:
        for warning in parser.warnings:
            print(f"CIF Warning: {warning}")

    return structures[0]


def read_brml(filename):
    """
    Read a Bruker BRML file and extract XRD pattern data.

    BRML files are zip archives containing XML measurement data in RawDataN.xml files.
    Data is stored in <Datum> elements as CSV: time, ?, two_theta, theta, intensity

    Args:
        filename: Path to .brml file

    Returns:
        tuple: (two_theta, intensity) as numpy arrays
    """
    with zipfile.ZipFile(filename, 'r') as zf:
        raw_data_files = [name for name in zf.namelist() if 'RawData' in name and name.endswith('.xml')]

        for xml_file in raw_data_files:
            with zf.open(xml_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()

                two_theta_values = []
                intensity_values = []

                for datum in root.iter('Datum'):
                    parts = datum.text.split(',')
                    if len(parts) >= 5:
                        two_theta = float(parts[2])
                        intensity = float(parts[4])
                        two_theta_values.append(two_theta)
                        intensity_values.append(intensity)

                if two_theta_values and intensity_values:
                    return np.array(two_theta_values), np.array(intensity_values)

    raise ValueError(f"Could not extract XRD data from {filename}")
