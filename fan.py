# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 13:38:41 2024

@author: 82108
"""

import cantera as ct
import math

def fan(H5, H5a, T5, T5a):
    """
    Calculate fan parameters including mass flow rate, temperature differences, and power consumption.

    Parameters:
    H5 (float): Enthalpy before heat release (J).
    H5a (float): Enthalpy after heat release (J).
    T5 (float): Temperature before cooling (K).
    T5a (float): Temperature after cooling (K).

    Returns:
    tuple: Mass flow rate (kg/s), Log mean temperature difference (K), Fan power consumption (W), Inlet air temperature (K), Outlet air temperature (K).
    """
    # Set up the gas object for SOFC using GRI-Mech 3.0
    gas = ct.Solution('gri30.yaml')

    # Define species indices
    iN2 = gas.species_index('N2')
    iO2 = gas.species_index('O2')

    # Heat to be removed [J]
    Q_release = H5 - H5a

    # Overall heat transfer coefficient [W/m^2-K]
    Utot = 8.0  # Adjusted for SOFC typical ranges

    # Heat exchange area [m^2]
    Ab = 14.9  # Converted from ft^2 to m^2 (1 ft^2 = 0.092903 m^2)

    # Ambient temperature and pressure
    T_amb = 30 + 273.15  # [K]
    P_amb = ct.one_atm  # [Pa]

    # Inlet and outlet temperatures of the fan
    To_in = T_amb
    To_out = Q_release / (Utot * Ab) + To_in

    # Log mean temperature difference
    T_lm = ((T5 - To_out) - (T5a - To_in)) / math.log((T5 - To_out) / (T5a - To_in))

    # Set air composition for SOFC
    xair = [0] * gas.n_species
    xair[iN2] = 0.79
    xair[iO2] = 0.21
    gas.TPX = T_amb, P_amb, xair

    # Calculate air density and specific heat
    rho_o = gas.density
    cp_o = gas.cp_mass

    # Mass flow rate of external air [kg/s]
    m_dot_o = Q_release / (cp_o * (To_out - To_in))

    # Fan efficiency and pressure drop
    etha_fan = 0.85  # Adjusted for SOFC-specific fan efficiencies
    Dp = 300  # Pressure drop [Pa], adjusted for typical SOFC conditions

    # Ratio of specific heats
    gamma = gas.cp_mass / gas.cv_mass

    # Fan power consumption [W]
    P_fan = (m_dot_o * cp_o * T_amb / etha_fan) * (((((Dp + P_amb) / P_amb) ** ((gamma - 1) / gamma)) - 1))

    return m_dot_o, T_lm, P_fan, To_in, To_out

# Example usage
if __name__ == "__main__":
    H5 = 1e6  # Example enthalpy value [J]
    H5a = 0.9e6  # Example enthalpy after heat release [J]
    T5 = 1273.15  # Example temperature [K]
    T5a = 1173.15  # Example temperature after cooling [K]

    results = fan(H5, H5a, T5, T5a)
    print("Mass flow rate (kg/s):", results[0])
    print("Log mean temperature difference (K):", results[1])
    print("Fan power consumption (W):", results[2])
    print("Inlet air temperature (K):", results[3])
    print("Outlet air temperature (K):", results[4])
