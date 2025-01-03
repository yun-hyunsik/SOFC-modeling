# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 01:57:32 2024

@author: 82108
"""

import numpy as np

def sofc_map_gen(T_initial=900, rv=8.5, bore=0.145, stroke=0.145, con_len=0.145*0.2025/0.152, RPM=1800, n_cyl=8):
    """
    Generates map of SOFC operating conditions based on given parameters.

    Parameters:
    -----------
    T_initial : float
        Initial charge temperature (K), default is 900 for SOFC.
    rv : float
        Compression ratio, default is 8.5 for SOFC.
    bore : float
        Cylinder bore (m).
    stroke : float
        Cylinder stroke (m).
    con_len : float
        Connecting rod length (m).
    RPM : int
        Engine RPM, default is 1800.
    n_cyl : int
        Number of cylinders, default is 8.

    Returns:
    --------
    results : dict
        Dictionary containing calculated SOFC operating parameters.
    """
    # Initialize parameters specific to SOFC
    phi = 1  # Equivalence ratio
    T_clr = 1000  # Residual clearance temperature (K)
    y_exh = [0.75, 0.2, 0.05]  # Example exhaust composition: H2O, CO2, trace gases
    
    # Derived quantities
    displacement_volume = n_cyl * (np.pi / 4) * bore**2 * stroke
    
    # Initialize results container
    results = {
        "T_initial": T_initial,
        "rv": rv,
        "bore": bore,
        "stroke": stroke,
        "con_len": con_len,
        "RPM": RPM,
        "n_cyl": n_cyl,
        "displacement_volume": displacement_volume,
        "T_clr": T_clr,
        "y_exh": y_exh,
    }

    # Example calculation: piston speed
    piston_speed = 2 * stroke * (RPM / 60)
    results["piston_speed"] = piston_speed

    # Example calculation: thermal efficiency approximation
    gamma = 1.3  # Ratio of specific heats for typical SOFC conditions
    thermal_efficiency = 1 - (1 / rv**(gamma - 1))
    results["thermal_efficiency"] = thermal_efficiency

    return results

# Example usage
if __name__ == "__main__":
    results = sofc_map_gen()
    for key, value in results.items():
        print(f"{key}: {value}")