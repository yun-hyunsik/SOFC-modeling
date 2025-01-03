# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:25:04 2024

@author: 82108
"""

import cantera as ct

def MicroSOFC(x_ci, P_ci, m_ci):
    # Ideal gas mixture setup
    gas = ct.Solution('gri30.xml')  # SOFC의 연료 조성에 맞게 사용
    N = gas.n_species
    M = gas.molecular_weights
    
    # Component indices
    iCO2 = gas.species_index('CO2')
    iCH4 = gas.species_index('CH4')
    iH2O = gas.species_index('H2O')
    iH2 = gas.species_index('H2')
    iO2 = gas.species_index('O2')
    iN2 = gas.species_index('N2')
    
    # Compressor
    x_co = x_ci
    m_co = m_ci
    rp_c = 4.8  # 압축비
    P_co = rp_c * P_ci

    # Turbine inlet conditions
    T_ti = 1200  # SOFC의 높은 작동 온도 반영 (K)
    P_ti = P_co
    P_to = P_ci
    
    x_ti = x_co.copy()
    x_ti[iH2O] = x_co[iH2]
    x_ti[iH2] = 0
    x_ti[iCO2] += x_co[iCO]
    x_ti[iCO] = 0

    x_ti /= sum(x_ti)

    gas.TPX = T_ti, P_ti, x_ti
    h_ti = gas.enthalpy_mass
    s_ti = gas.entropy_mass

    gas.SPX = s_ti, P_to, x_ti
    h_to_s = gas.enthalpy_mass

    h_to = h_ti - (h_ti - h_to_s) * 0.84
    gas.HPX = h_to, P_to, x_ti
    T_to = gas.T

    W_turb = m_co * (h_ti - h_to)

    # Compressor outlet conditions
    gas.HPX = h_ti, P_co, x_co
    T_co = gas.T

    # Iteratively find T_ci
    h_ci_temp = []
    err = []
    T_ci_range = range(250, int(T_co))  # T_ci range (K)
    
    for T_ci_temp in T_ci_range:
        gas.TPX = T_ci_temp, P_ci, x_ci
        h_ci = gas.enthalpy_mass
        s_ci = gas.entropy_mass

        gas.SPX = s_ci, P_co, x_co
        h_co_s = gas.enthalpy_mass

        eff_temp = (h_co_s - h_ci) / (h_ti - h_ci)
        h_ci_temp.append(h_ci)
        err.append(abs(eff_temp - 0.8))

    T_ci = T_ci_range[err.index(min(err))]
    h_ci = h_ci_temp[err.index(min(err))]

    W_comp = m_ci * (h_ti - h_ci)
    LHV_ci = m_ci * gas.standard_enthalpy_reaction
    W_gt = W_turb - W_comp
    eff_gt = W_gt / LHV_ci

    return T_ci, T_to, W_gt, eff_gt, W_turb, W_comp, T_co
