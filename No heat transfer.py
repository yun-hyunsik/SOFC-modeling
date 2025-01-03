import cantera as ct
import numpy as np

# Define the function for SOFC modeling
def sofc_modeling(m_H2, m_H2O, m_O2, T_reform_in, T_reform_out, P_reform, x_O2_in):
    # Initialize gas properties with a YAML database
    gas = ct.Solution('gri30.yaml')  # Replace with the correct YAML file for SOFC
    
    # Define species indices for key components
    iH2 = gas.species_index('H2')
    iO2 = gas.species_index('O2')
    iH2O = gas.species_index('H2O')
    
    # Set inlet conditions for the reformer
    gas.TPX = T_reform_in, P_reform, {'H2': m_H2, 'H2O': m_H2O}
    h_reform_in = gas.enthalpy_mass
    
    # Simulate reformer outlet
    gas.TP = T_reform_out, P_reform
    h_reform_out = gas.enthalpy_mass
    
    # Cathode side calculations
    gas.TPX = T_reform_in, P_reform, x_O2_in
    h_cathode_in = gas.enthalpy_mass

    # Calculate LHV manually for H2
    gas.TPX = 298.15, ct.one_atm, {'H2': 1.0, 'O2': 0.5}
    h_reactants = gas.enthalpy_mass
    gas.TPX = 298.15, ct.one_atm, {'H2O': 1.0}
    h_products = gas.enthalpy_mass
    LHV_H2 = h_reactants - h_products  # Lower Heating Value for H2

    # Simulate SOFC electrochemical reactions
    fuel_utilization = 0.85
    m_fuel_used = m_H2 * fuel_utilization
    
    # Energy balance for SOFC
    w_net = m_fuel_used * LHV_H2
    efficiency = w_net / (m_H2 * LHV_H2)

    return {
        'h_reform_in': h_reform_in,
        'h_reform_out': h_reform_out,
        'h_cathode_in': h_cathode_in,
        'w_net': w_net,
        'efficiency': efficiency
    }

# Example call to the function
result = sofc_modeling(
    m_H2=0.1, 
    m_H2O=0.2, 
    m_O2=0.15, 
    T_reform_in=900 + 273.15, 
    T_reform_out=1000 + 273.15, 
    P_reform=ct.one_atm, 
    x_O2_in={'O2': 0.21, 'N2': 0.79}
)

# Output the results
for key, value in result.items():
    print(f"{key}: {value}")
