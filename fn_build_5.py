# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 13:38:56 2024

@author: 82108
"""

def build_filename(rv, phi, rmf, T_initial, y_prev, cycle_num, HT_ver_string):
    """
    Generate a filename based on SOFC parameters.

    Args:
        rv (float): Residual volume.
        phi (float): Equivalence ratio.
        rmf (float): Reactant molar fraction.
        T_initial (int): Initial temperature. Use 0 for 'AMM' model.
        y_prev (list): List representing previous cycle assumptions.
        cycle_num (int): Current cycle number.
        HT_ver_string (str): Heat transfer version string.

    Returns:
        str: Generated filename.
    """
    # Determine string for initial temperature
    T_initial_string = 'AMM' if T_initial == 0 else str(T_initial)

    # Determine string for assumption regarding exhaust residual
    y_prev_string = 'MP' if y_prev[0] == 0 else 'PC'

    # Assemble the parts of the filename
    filename = f"hsd_{int(rv * 10)}_{int(phi * 100)}_{int(rmf * 100)}_{T_initial_string}_{y_prev_string}_{cycle_num}_{HT_ver_string}"

    return filename

# Example usage
if __name__ == "__main__":
    rv = 0.1
    phi = 0.85
    rmf = 0.75
    T_initial = 1000
    y_prev = [0, 0, 1]
    cycle_num = 1
    HT_ver_string = "SOFC2024"

    filename = build_filename(rv, phi, rmf, T_initial, y_prev, cycle_num, HT_ver_string)
    print("Generated filename:", filename)
