import numpy as np
import cantera as ct
import csv

# Constants (adjusted for SOFC specifics)
MASS = 1.0  # Example mass value (kg), replace with actual SOFC mass
LHV = 120e6  # Lower heating value for SOFC fuel (J/kg), adjust as needed
RPM = 1500  # Engine RPM
n_cyl = 6  # Number of cylinders
bore = 0.1  # Bore size in meters
stroke = 0.1  # Stroke length in meters
con_len = 0.15  # Connecting rod length in meters

# Function to calculate thermodynamic properties
def post_process_SOFC(t1, out1, gas, xspi):
    # Initialize output structures
    CAD_sim = out1[:, 0] * (180 / np.pi)
    V_sim = out1[:, 1]
    v_sim = V_sim / MASS
    T_sim = out1[:, 2]
    Q_sim = out1[:, 4]

    len_cycle = len(out1)
    avg_MW = np.zeros(len_cycle)
    avg_R = np.zeros(len_cycle)
    p_sim = np.zeros(len_cycle)
    u_sim = np.zeros(len_cycle)
    h_sim = np.zeros(len_cycle)
    s_sim = np.zeros(len_cycle)

    # Ensure species data length matches gas.n_species
    species_data = np.zeros((len_cycle, gas.n_species))
    for i, species in enumerate(xspi):
        if species in gas.species_names:
            species_index = gas.species_names.index(species)
            species_data[:, species_index] = out1[:, 5 + i]

    # Calculate mixture properties
    for i in range(len_cycle):
        gas.Y = species_data[i, :]
        avg_MW[i] = gas.mean_molecular_weight
        avg_R[i] = ct.gas_constant / avg_MW[i]
        gas.TP = T_sim[i], (1e5 * (avg_R[i] * T_sim[i] / v_sim[i]))  # Pressure in Pa
        p_sim[i] = gas.P / 1e5  # Convert to bar
        u_sim[i] = gas.u
        h_sim[i] = gas.h
        s_sim[i] = gas.s

    # Calculate performance metrics
    peakp_sim = np.max(p_sim)
    peakp_index = np.argmax(p_sim)
    aop_sim = CAD_sim[peakp_index]

    maxraterise_sim = np.max(np.gradient(p_sim))
    aomaxraterise_sim = CAD_sim[np.argmax(np.gradient(p_sim))]

    gross_work_sim = (u_sim[0] - u_sim[-1]) * MASS - Q_sim[-1]
    gmep_sim = (gross_work_sim / (np.pi * (bore / 2)**2 * stroke)) / 1e5  # in bar
    gross_eff_sim = gross_work_sim / (LHV * MASS)
    gross_power_sim = gross_work_sim * (RPM / 60 / 2) * n_cyl

    # Output structures
    cycle_props = np.column_stack((p_sim, V_sim, v_sim, T_sim, u_sim, h_sim, s_sim, Q_sim))
    cycle_stats = [gmep_sim, gross_eff_sim, peakp_sim, aop_sim, maxraterise_sim, aomaxraterise_sim, gross_power_sim]

    return CAD_sim, cycle_props, cycle_stats

# Example usage
def main():
    # Initialize Cantera gas object
    gas = ct.Solution("gri30.yaml")  # Replace with appropriate SOFC mechanism file

    # Load input data (example values)
    t1 = np.linspace(0, 1, 100)  # Time vector
    out1 = np.random.rand(100, 10)  # Replace with actual simulation data
    xspi = ["H2", "O2", "N2", "H2O", "CO2"]  # Species indices

    # Call post-processing function
    CAD_sim, cycle_props, cycle_stats = post_process_SOFC(t1, out1, gas, xspi)

    # Save results to CSV
    with open("sofc_cycle_properties.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Pressure (bar)", "Volume (m^3)", "Specific Volume (m^3/kg)", "Temperature (K)",
                         "Internal Energy (J/kg)", "Enthalpy (J/kg)", "Entropy (J/kg.K)", "Heat Transfer (J)"])
        writer.writerows(cycle_props)

    print("Cycle properties saved to sofc_cycle_properties.csv")

if __name__ == "__main__":
    main()