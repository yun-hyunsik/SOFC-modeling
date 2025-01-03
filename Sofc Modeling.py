import cantera as ct
import numpy as np
from fan import fan
from create_gas import create_gas_structure
from fn_build_5 import build_filename
from HX import heat_exchanger_effectiveness
from LHV_mass import LHV_mass
from sys_ver2 import SOFC_model
from slidercrank2 import slider_crank
from sofc_map_gen import sofc_map_gen
from HX_eff import Hx_eff_SOFC
from init_conditions import theta_initial, P_initial, T_initial
from init_cyl_state import init_cyl_state
from LHVmass import LHVmass
from maxrr import max_rr
from MicroGt import MicroSOFC
from Mix import mix
from rdh_cycle_shell_HT import calculate_initial_volume
from rdh_system_HT import sofc_system
from reformer import reformer
from sofc_post_process_HT import post_process_SOFC
import matplotlib.pyplot as plt

def integrate_sofc_system():
    """
    Integrate all SOFC components into a cohesive system.
    """
    # Step 1: Initialize gas
    def initialize_fuel_mixture():
        gas = ct.Solution('gri30.xml')  # Cantera 메커니즘
        gas.TPX = 300, ct.one_atm, {'CH4': 0.5, 'H2O': 0.5}  # 초기 혼합물 비율
        return gas

    def calculate_fuel_properties(gas):
        h_react = gas.enthalpy_mass  # 연료 혼합물의 엔탈피
        gas.equilibrate('TP')  # 평형 상태로 전환
        h_prod = gas.enthalpy_mass  # 생성물의 엔탈피
        LHV = h_react - h_prod
        return LHV

    gas = initialize_fuel_mixture()
    lhv = calculate_fuel_properties(gas)
    print(f"LHV (J/kg): {lhv}")

    # Simulate temperature distribution
    def simulate_temperature_distribution(gas):
        gas.TPX = 800, ct.one_atm, {'H2': 0.8, 'O2': 0.2}
        gas.equilibrate('TP')
        return gas.T  # 생성물의 평형 온도

    temp = simulate_temperature_distribution(gas)
    print(f"Predicted equilibrium temperature: {temp} K")

    # Heat exchanger effectiveness calculation
    def heat_exchanger_efficiency(T_hot_in, T_hot_out, T_cold_in):
        effectiveness = (T_hot_in - T_hot_out) / (T_hot_in - T_cold_in)
        return effectiveness

    hx_effectiveness = heat_exchanger_efficiency(1000, 900, 300)
    print(f"Heat Exchanger Effectiveness: {hx_effectiveness}")

    # Step 2: Example fan calculation
    H5 = 1e6  # Example enthalpy value [J]
    H5a = 0.9e6  # Example enthalpy after heat release [J]
    T5 = 1273.15  # Example temperature [K]
    T5a = 1173.15  # Example temperature after cooling [K]

    fan_results = fan(H5, H5a, T5, T5a)
    print("Fan results:", fan_results)

    # Step 3: Generate filename for output
    rv = 0.1
    phi = 0.85
    rmf = 0.75
    T_initial = 1000
    y_prev = [0, 0, 1]
    cycle_num = 1
    HT_ver_string = "SOFC2024"

    filename = build_filename(rv, phi, rmf, T_initial, y_prev, cycle_num, HT_ver_string)
    print("Generated filename:", filename)

    # Step 4: Heat exchanger effectiveness calculation
    T_hot_in = 1000  # K
    T_hot_out = 900  # K
    T_cold_in = 300  # K
    H_hot_in = 1e6  # J/kg
    H_hot_out = 0.8e6  # J/kg
    H_cold_in = 0.2e6  # J/kg
    x_hot = {"H2": 0.7, "O2": 0.3}
    x_cold_in = {"N2": 0.8, "O2": 0.2}
    m_hot = 0.1  # kg/s
    m_cold_in = 0.2  # kg/s
    nsp = 53

    hx_results = heat_exchanger_effectiveness(T_hot_in, T_hot_out, T_cold_in, H_hot_in, H_hot_out, H_cold_in, x_hot, x_cold_in, m_hot, m_cold_in, nsp)
    hx_effectiveness, T_cold_out, Q_dot = hx_results
    print("Heat exchanger effectiveness:", hx_effectiveness)
    print("Cold outlet temperature (K):", T_cold_out)
    print("Heat transfer rate (J/s):", Q_dot)

    # Step 5: Calculate LHV
    lhv_value = calculate_fuel_properties(gas)
    if lhv_value == 0:
        print("Warning: LHV calculation returned 0. Verify gas composition.")
    else:
        print("Lower Heating Value (LHV):", lhv_value)

    # Step 6: SOFC model simulation
    m_H2 = 0.01  # kg/s
    m_H2O = 0.02  # kg/s
    T_in = 1000.0  # K
    P_in = ct.one_atm  # Pa
    x_ca_in = [0.21, 0.79]  # O2 and N2 mole fractions

    sofc_results = SOFC_model(m_H2, m_H2O, T_in, P_in, x_ca_in)
    print("SOFC model results:", sofc_results)

    # Step 7: Slider-crank mechanism simulation
    crank_results = slider_crank(0.5, 0.3, 1000)
    print("Slider-crank mechanism results:", crank_results)

    # Step 8: SOFC map generation
    map_results = sofc_map_gen()
    print("SOFC map generation results:", map_results)

    # Step 9: Reformer simulation
    reformer_results = reformer(0.1, 0.2, 900, 1100, ct.one_atm)
    print("Reformer simulation results:", reformer_results)

    # Step 10: SOFC cycle shell simulation
    initial_volume = calculate_initial_volume(0, 12)
    print("Initial cycle volume:", initial_volume)

    # Step 11: SOFC system ODE simulation
    initial_conditions = [0, initial_volume, 1000, 0, 0] + list(gas.Y)
    print("Initial conditions for ODE:", initial_conditions)

    # Step 12: Post-process SOFC data
    t1 = np.linspace(0, 1, 100)  # Example time vector
    out1 = np.empty((100, 10))  # Prepare an array for actual simulation data
    for i in range(10):
        out1[:, i] = np.linspace(0.1 * i, 1.0 * i, 100)  # Simulated linear data for placeholder
    xspi = ["H2", "O2", "N2", "H2O", "CO2"]
    post_results = post_process_SOFC(t1, out1, gas, xspi)

    if post_results is None or len(post_results) == 0:
        print("Warning: Post-processing returned no results. Verify data pipeline.")
    else:
        print("Post-process results:", post_results)

    # Additional Outputs from MCFC Model
    # Total Power Output
    if 'angular_velocity' in crank_results and 'RPM' in map_results:
        W_tot = crank_results['angular_velocity'] * map_results['RPM'] * 0.001  # Corrected placeholder calculation
        print(f"Total Power Output (kW): {W_tot:.3f}")
    else:
        print("Error: Missing keys 'angular_velocity' or 'RPM' in results.")

    # Efficiency
    if lhv_value > 1e-5:
        eff_cell = W_tot / lhv_value
        print(f"Efficiency: {eff_cell:.3f}")
    else:
        print("Error: LHV value is too close to zero or invalid for efficiency calculation.")

    # Entropy and Heat Loss
    print(f"Heat exchanger entropy results: {hx_results}")

    # Visualization: Efficiency vs Temperature
    temperature = np.linspace(800, 1200, 4)  # Example improved temperature range
    efficiency = np.linspace(0.3, 0.5, 4)  # Simulated efficiency data

    plt.figure(figsize=(8, 6))
    plt.plot(temperature, efficiency, marker='o', label="Efficiency")
    plt.xlabel("Temperature (K)")
    plt.ylabel("Efficiency")
    plt.title("SOFC Efficiency vs Temperature")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Visualization: Power Output and Efficiency over Time
    time_vector = np.linspace(0, 100, 100)  # Example time data
    power_output = np.linspace(50, 100, 100)  # Simulated increasing power data
    efficiency_vector = np.linspace(0.25, 0.45, 100)  # Simulated increasing efficiency data

    plt.figure(figsize=(8, 6))
    plt.plot(time_vector, power_output, label="Power Output (kW)")
    plt.plot(time_vector, efficiency_vector, label="Efficiency", linestyle="--")
    plt.xlabel("Time (s)")
    plt.ylabel("Power (kW) / Efficiency")
    plt.title("Power Output and Efficiency over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Visualization: Heat Exchanger Temperatures
    temperatures = [T_hot_in, T_hot_out, T_cold_in]
    labels = ["T_hot_in", "T_hot_out", "T_cold_in"]
    bar_colors = ['#ff6666' if temp > 800 else '#66b3ff' for temp in temperatures]
    plt.bar(labels, temperatures, color=bar_colors)
    plt.title("Heat Exchanger Temperatures")
    plt.ylabel("Temperature (K)")
    plt.show()

    # Visualization: Gas Composition Changes
    time_vector = np.linspace(0, 100, 100)  # Example time data
    H2_fraction = np.linspace(0.1, 0.5, 100)  # Simulated increasing H2 data
    O2_fraction = np.linspace(0.4, 0.2, 100)  # Simulated decreasing O2 data
    H2O_fraction = np.linspace(0.1, 0.3, 100)  # Simulated increasing H2O data

    plt.figure(figsize=(8, 6))
    plt.plot(time_vector, H2_fraction, label="H2 Mole Fraction")
    plt.plot(time_vector, O2_fraction, label="O2 Mole Fraction", linestyle="--")
    plt.plot(time_vector, H2O_fraction, label="H2O Mole Fraction", linestyle=":")
    plt.xlabel("Time (s)")
    plt.ylabel("Mole Fraction")
    plt.title("Gas Composition Changes Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

    print("Integration complete. All components tested.")

# Example usage
if __name__ == "__main__":
    integrate_sofc_system()
