# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 13:50:45 2024

@author: 82108
"""

import cantera as ct

def LHV_mass(gas):
    """
    Calculate the Lower Heating Value (LHV) based on the mass of the input gas.

    Parameters:
    gas (Cantera.Solution): Cantera gas object with fuel composition.

    Returns:
    float: LHV in J/kg.
    """
    # Save initial state
    initial_state = (gas.T, gas.P, gas.X)

    # Reference state
    T_ref = 298.15  # K
    P_ref = ct.one_atm

    # Set reference state
    gas.TP = T_ref, P_ref
    h_react = gas.enthalpy_mass

    # Equilibrate to find products
    gas.equilibrate('TP')
    h_prod = gas.enthalpy_mass

    # Calculate LHV
    LHV = h_react - h_prod

    # Restore initial state
    gas.TPX = initial_state

    return LHV
