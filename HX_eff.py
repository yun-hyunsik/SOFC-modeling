# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 02:23:15 2024

@author: 82108
"""

def Hx_eff_SOFC(eff_HX, T2, T3, P2, P3, x2, x3, m2, m3):
    from cantera import Solution

    # Cantera SOFC specific gas file
    gas = Solution('gri30.yaml')  # Ensure you have the correct Cantera input file
    N = gas.n_species
    iH2 = gas.species_index('H2')
    iH2O = gas.species_index('H2O')
    iO2 = gas.species_index('O2')
    iN2 = gas.species_index('N2')
    M = gas.molecular_weights

    # Set properties for stream 2
    gas.TPX = T2, P2, x2
    cp_h = gas.cp_mass
    Ch = m2 * cp_h
    h2 = gas.enthalpy_mass
    H2 = h2 * m2

    # Set properties for stream 3
    gas.TPX = T3, P3, x3
    cp_c = gas.cp_mass
    Cc = m3 * cp_c
    h3 = gas.enthalpy_mass
    H3 = h3 * m3

    # Calculate C_min
    if Ch > Cc:
        C_min = Cc
    else:
        C_min = Ch

    q_max = C_min * (T2 - T3)
    q = q_max * eff_HX

    # Energy balance for T1 and T4
    H1 = H2 - q
    h1 = H1 / m2
    gas.HP = h1, P2
    T1 = [gas.T]

    H4 = H3 + q
    h4 = H4 / m3
    gas.HP = h4, P3
    T4 = [gas.T]

    # Iterative solution for temperature updates
    i = 0
    while True:
        Tm1 = (T1[i] + T2) / 2
        Tm2 = (T3 + T4[i]) / 2

        gas.TPX = Tm1, gas.P, x2
        cp_m1 = gas.cp_mass
        Ch_m = m2 * cp_m1

        gas.TPX = Tm2, gas.P, x3
        cp_m2 = gas.cp_mass
        Cc_m = m3 * cp_m2

        if Ch_m > Cc_m:
            C_min = Cc_m
        else:
            C_min = Ch_m

        Q_max_temp = C_min * (T2 - T3)
        Q_temp = Q_max_temp * eff_HX

        i += 1

        H1 = H2 - Q_temp
        h1 = H1 / m2
        gas.HP = h1, P2
        T1.append(gas.T)

        H4 = H3 + Q_temp
        h4 = H4 / m3
        gas.HP = h4, P3
        T4.append(gas.T)

        if abs((T1[i] - T1[i-1]) / T1[i]) < 0.001 and abs((T4[i] - T4[i-1]) / T4[i]) < 0.001:
            break

    T1_f = T1[-1]
    T4_f = T4[-1]

    return T1_f, T4_f, Cc, Ch, C_min
