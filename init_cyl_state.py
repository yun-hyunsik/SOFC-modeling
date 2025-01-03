# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 02:40:20 2024

@author: 82108
"""

import cantera as ct

def init_cyl_state(gas, phi, rmf, rv, T_int, T_exh, T_clr, y_exh):
    # Small value to avoid zeros
    zv = 1e-8

    # Determine species indices for SOFC-relevant species
    x_H2_index = gas.species_index('H2')
    x_O2_index = gas.species_index('O2')
    x_N2_index = gas.species_index('N2')
    x_H2O_index = gas.species_index('H2O')
    x_CO_index = gas.species_index('CO')
    x_CO2_index = gas.species_index('CO2')

    xspi = [x_H2_index, x_O2_index, x_N2_index, x_H2O_index, x_CO_index, x_CO2_index]

    # Initialize the composition
    if y_exh[0] == 0:
        print("Assuming MAJOR PRODUCTS for residual, not using previous cycle data.")
        if phi == 0:
            initX = [zv] * gas.n_species
            initX[x_O2_index] = 0.21
            initX[x_N2_index] = 0.79
            gas.TPX = T_int, ct.one_atm, initX
            y_init = gas.Y
        else:
            # Set intake composition based on equivalence ratio phi
            initX = [zv] * gas.n_species
            react_total = 1 + (4 / phi) * 4.76
            x_H2 = 1 / react_total
            x_O2 = 4 / (phi * react_total)
            x_N2 = (4 * 3.76) / (phi * react_total)
            initX[x_H2_index] = x_H2
            initX[x_O2_index] = x_O2
            initX[x_N2_index] = x_N2
            gas.TPX = T_int, ct.one_atm, initX
            y_int = gas.Y

            # Set exhaust composition
            initX = [zv] * gas.n_species
            prod_total = 2 + 1 + (4 * 3.76 / phi)
            x_H2O = 2 / prod_total
            x_CO2 = 1 / prod_total
            x_N2 = (4 * 3.76 / phi) / prod_total
            initX[x_H2O_index] = x_H2O
            initX[x_CO2_index] = x_CO2
            initX[x_N2_index] = x_N2
            gas.TPX = T_exh, ct.one_atm, initX
            y_exh = gas.Y

            # Mixture composition
            y_init = (1 - rmf) * y_int + rmf * y_exh

    else:
        print("Using previous cycle data for exhaust residual.")
        if phi == 0:
            initX = [zv] * gas.n_species
            initX[x_O2_index] = 0.21
            initX[x_N2_index] = 0.79
            gas.TPX = T_int, ct.one_atm, initX
            y_init = gas.Y
        else:
            initX = [zv] * gas.n_species
            react_total = 1 + (4 / phi) * 4.76
            x_H2 = 1 / react_total
            x_O2 = 4 / (phi * react_total)
            x_N2 = (4 * 3.76) / (phi * react_total)
            initX[x_H2_index] = x_H2
            initX[x_O2_index] = x_O2
            initX[x_N2_index] = x_N2
            gas.TPX = T_int, ct.one_atm, initX
            y_int = gas.Y

            # Mixture composition
            y_init = (1 - rmf) * y_int + rmf * y_exh

    # Initial temperature calculation
    if T_exh == 0:
        T_init = T_int
        m_init_vec = [0, 0, 0]
    else:
        T_init = 300
        T_step = 1
        P_cyl = ct.one_atm

        gas.TPY = T_clr, ct.one_atm, y_exh
        u_clr = gas.u
        R_clr = ct.gas_constant / gas.mean_molecular_weight
        V_clr = (1 / rv) * 1e-3  # Example clearance volume in m^3
        m_clr = (P_cyl * V_clr) / (R_clr * T_clr)
        gas.Y = y_init
        R = ct.gas_constant / gas.mean_molecular_weight
        V = (1 / rv) * 1e-3

        while True:
            T_init += T_step
            m_init = (P_cyl * V) / (R * T_init)
            gas.TPY = T_init, ct.one_atm, y_init
            u_calc = gas.u
            m_exh = (rmf * m_init) - m_clr
            m_int = m_init - m_exh - m_clr
            u_test = ((m_int * gas.h) + (m_exh * gas.h) + (m_clr * u_clr) - (P_cyl * V)) / m_init
            if abs(u_test - u_calc) < 1e-6:
                break

        print(f"Initial cylinder temperature calculated: {T_init} K")
        m_init_vec = [m_int, m_exh, m_clr]

    return y_init, T_init, m_init_vec, xspi
