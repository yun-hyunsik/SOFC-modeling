# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:27:43 2024

@author: 82108
"""

from cantera import Solution

def MicroSOFC(x_ci, P_ci, m_ci):
    # Load SOFC-specific gas model
    gas = Solution('sofc.cti')
    N = gas.n_species
    
    # Index for common species
    iH2 = gas.species_index('H2')
    iO2 = gas.species_index('O2')
    iCO = gas.species_index('CO')
    iCO2 = gas.species_index('CO2')
    iH2O = gas.species_index('H2O')
    iN2 = gas.species_index('N2')
    
    # Compressor
    x_co = x_ci
    m_co = m_ci
    rp_c = 3.5  # Adjusted for SOFC
    P_co = rp_c * P_ci
    T_co = 900 + 273.15  # SOFC pre-reformer output temperature
    
    gas.TPX = T_co, P_co, x_co
    h_co = gas.enthalpy_mass
    cp_co = gas.cp_mass
    cv_co = gas.cv_mass
    k = cp_co / cv_co
    
    T_ci = T_co / ((P_co / P_ci) ** ((k - 1) / k))
    gas.TPX = T_ci, P_ci, x_ci
    h_ci = gas.enthalpy_mass
    
    W_comp = m_ci * (h_co - h_ci)
    
    # Turbine
    T_ti = 1200 + 273.15  # SOFC operating temperature
    T_to = 600 + 273.15
    P_ti = P_co
    P_to = P_ci
    
    x_ti = x_co.copy()
    x_ti[iH2O] = x_co[iH2]
    x_ti[iH2] = 0
    x_ti[iCO2] += x_co[iCO]
    x_ti[iO2] -= 0.5 * x_co[iH2]
    
    x_ti = x_ti / sum(x_ti)
    gas.TPX = T_ti, P_ti, x_ti
    h_ti = gas.enthalpy_mass
    
    x_to = x_ti.copy()
    gas.TPX = T_to, P_to, x_to
    h_to = gas.enthalpy_mass
    
    W_turb = m_co * (h_ti - h_to)
    
    # Efficiency
    W_gt = W_turb - W_comp
    LHV_ci = m_ci * gas.enthalpy_mole(iH2)  # Assuming H2 as primary fuel
    eff_gt = W_gt / LHV_ci
    
    return T_ci, T_to, x_to, W_gt, eff_gt, W_turb, W_comp, T_co
