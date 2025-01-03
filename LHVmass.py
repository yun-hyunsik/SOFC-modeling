# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:04:34 2024

@author: 82108
"""

import cantera as ct

def LHVmass(gas):
    """
    Calculate the Low Heating Value (LHV) based on mass for the input gas.

    Parameters:
        gas: Cantera.Solution object representing the input gas.

    Returns:
        LHVmass: Low Heating Value in J/kg.
    """
    # Reference state
    T_ref = 300  # K
    P_ref = 101325  # Pa

    # Create Oxygen gas
    O2 = ct.Solution('gri60.xml')  # Use gri60.xml for SOFC modeling
    N = O2.n_species
    iO2 = O2.species_index('O2')

    # Set oxygen composition
    xO2 = [0.0] * N
    xO2[iO2] = 1.0
    O2.X = xO2
    O2.TP = T_ref, P_ref

    # Mix input gas with Oxygen gas
    mix = ct.Solution('gri60.xml')
    mF_gas = gas.X
    mF_O2 = O2.X

    # Assume 1000 mole of O2 per 1 mole of gas
    mF_mix = mF_gas + 1001 * mF_O2
    mix.X = mF_mix
    mix.TP = T_ref, P_ref

    # Mass fraction of gas in mixture
    massF_gas = gas.mean_molecular_weight / (gas.mean_molecular_weight + 1000 * O2.mean_molecular_weight)

    # Enthalpy calculations
    h_react = mix.enthalpy_mass  # Enthalpy of reactants
    mix.equilibrate('TP')  # Equilibrate mixture (combustion)
    h_prod = mix.enthalpy_mass  # Enthalpy of products

    # Calculate LHV
    LHVmass = (h_react - h_prod) / massF_gas  # J/kg
    return LHVmass
