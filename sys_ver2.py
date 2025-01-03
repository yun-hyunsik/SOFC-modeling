# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 13:51:22 2024

@author: 82108
"""

import cantera as ct
import numpy as np

def SOFC_model(m_H2, m_H2O, T_in, P_in, x_ca_in):
    """
    Simulates the operation of a Solid Oxide Fuel Cell (SOFC).

    Parameters:
    m_H2 : float
        Mass flow rate of hydrogen (kg/s).
    m_H2O : float
        Mass flow rate of water (kg/s).
    T_in : float
        Inlet temperature (K).
    P_in : float
        Inlet pressure (Pa).
    x_ca_in : list
        Cathode gas composition (mole fractions).

    Returns:
    dict
        Results including power, efficiency, and outlet conditions.
    """
    # Load SOFC gas mixture
    gas = ct.Solution('gri30.yaml')
    N = gas.n_species

    # Species indices
    iH2 = gas.species_index('H2')
    iH2O = gas.species_index('H2O')
    iO2 = gas.species_index('O2')
    iN2 = gas.species_index('N2')

    # Set anode inlet conditions
    x_an = np.zeros(N)
    x_an[iH2] = 1.0
    x_an = x_an / np.sum(x_an)
    gas.TPX = T_in, P_in, x_an
    h_an = gas.enthalpy_mass
    m_an = m_H2 + m_H2O

    # Set cathode inlet conditions
    x_ca = np.zeros(N)
    x_ca[iO2] = x_ca_in[0]  # O2 mole fraction
    x_ca[iN2] = x_ca_in[1]  # N2 mole fraction
    x_ca = x_ca / np.sum(x_ca)
    gas.TPX = T_in, P_in, x_ca
    h_ca = gas.enthalpy_mass
    m_ca = np.sum(x_ca_in)  # Adjust for actual mass flow

    # Calculate electrochemical reactions
    utilization = 0.8  # Assume 80% fuel utilization
    m_H2_reacted = m_H2 * utilization
    h_reacted = m_H2_reacted * gas.enthalpy_mass

    # Calculate power output
    V_cell = 1.1  # Open-circuit voltage, adjust for SOFC specifics
    W_cell = m_H2_reacted * V_cell * ct.faraday / gas.molecular_weights[iH2]

    # Update outlet conditions (anode)
    m_H2_out = m_H2 - m_H2_reacted
    x_an_out = np.zeros(N)
    x_an_out[iH2] = m_H2_out / m_an
    x_an_out[iH2O] = 1.0 - x_an_out[iH2]
    x_an_out = x_an_out / np.sum(x_an_out)

    # Set outlet conditions for gas object
    gas.TPX = T_in, P_in, x_an_out
    h_an_out = gas.enthalpy_mass

    # Efficiency calculation
    LHV_H2 = 120e6  # Lower heating value of hydrogen (J/kg)
    efficiency = W_cell / (m_H2 * LHV_H2)

    # Return results
    results = {
        "power_output": W_cell,
        "efficiency": efficiency,
        "anode_outlet": {
            "temperature": gas.T,
            "pressure": gas.P,
            "composition": gas.X
        },
        "cathode_outlet": {
            "temperature": T_in,  # Assume unchanged
            "pressure": P_in,
            "composition": x_ca
        }
    }

    return results
