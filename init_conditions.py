# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 02:29:32 2024

@author: 82108
"""

# init_conditions_sofc.py
# -----------------
# Initial conditions for SOFC cycle simulation.

# Adjustments made to adapt from MCFC to SOFC:
# 1. SOFC operates at higher temperatures (~800-1000 K).
# 2. Removed components specific to internal combustion engines.
# 3. Adjusted for gas-phase modeling relevant to SOFC fuel and oxidant.

import numpy as np

global MASS, NSP, MW, FP, FD, ST, TW, SADH, HT, bore, stroke, con_len, RPM
# MASS = trapped mass in the system (kg)
# NSP = number of species in the gas
# MW = vector of molecular weights for each of the species in the gas
# FP = user-set constant for production of turbulent KE
# FD = user-set constant for dissipation of turbulent KE
# ST = user-set Stanton number for heat transfer
# HT = heat transfer control

# **** Data Save ****
HT_ver_string = 'SOFC2024'  # Heat transfer/version flag for filename
wd = '.'  # Base directory
dd = wd  # Data directory in which to save files
capture_data_flag = 1  # 1=save data in file, 0=do not save data
duplicate_check_flag = 0  # 1=check for duplicate files, 0=simulate regardless of duplicates

# **** Initial Conditions for Cycle Simulation ****
theta_initial = -np.pi  # Initial angle (rad)
P_initial = 1  # atm
T_initial = 1000  # SOFC operating temperature (K)

# **** Heat Transfer Control ****
# 0 = no heat transfer
# 1 = User-defined correlation
HT = 1
SFC = 1  # Scaling factor for heat transfer adjustments

# **** Fuel Cell Specific Constants ****
fuel = 'H2'  # SOFC typically uses H2 as fuel
oxidant = 'O2'  # Oxidant used in the air electrode

# **** Integration Time Limits and Steps ****
t_initial = 0
t_final = 0.5  # Simulation time in seconds
steps = 1000
t_vec = np.linspace(t_initial, t_final, steps)

# **** Calculations Based on Initial Conditions ****
bore = 0.2  # Dummy value, replace with SOFC-specific dimensions (m)
stroke = 0.3  # Placeholder stroke length (m)
a = stroke / 2  # Crank radius (m)
swept_volume = (np.pi / 4) * (bore ** 2) * (2 * a)  # m^3

dome_height = 0.1  # Placeholder dome height for SOFC geometry (m)
SA_dome = np.pi * ((dome_height ** 2) + ((bore ** 2) / 4))  # m^2
SADH = SA_dome  # Surface area relevant to heat transfer

# **** Turbulent KE/Heat Transfer Parameters ****
TW = 1000  # Wall temperature (K), assuming near operating temperature
k_initial = 0
Q_initial = 0
FP = 0.002  # Adjusted for fuel cell-specific conditions
FD = 0.1  # Adjusted for fuel cell-specific conditions
ST = 0.02

# Additional SOFC-specific parameters
fuel_utilization = 0.85  # Fuel utilization factor
oxidant_utilization = 0.8  # Oxidant utilization factor
cell_area = 1.0  # Active cell area (m^2)

# Placeholder for additional SOFC-specific functions and calculations
