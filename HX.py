import cantera as ct

def heat_exchanger_effectiveness(T_hot_in, T_hot_out, T_cold_in, H_hot_in, H_hot_out, H_cold_in, x_hot, x_cold_in, m_hot, m_cold_in, nsp):
    """
    Calculate the effectiveness of a heat exchanger.

    Parameters:
    T_hot_in (float): Inlet temperature of the hot stream (K).
    T_hot_out (float): Outlet temperature of the hot stream (K).
    T_cold_in (float): Inlet temperature of the cold stream (K).
    H_hot_in (float): Enthalpy of the hot stream at inlet (J/kg).
    H_hot_out (float): Enthalpy of the hot stream at outlet (J/kg).
    H_cold_in (float): Enthalpy of the cold stream at inlet (J/kg).
    x_hot (dict): Composition of the hot stream (mole fractions).
    x_cold_in (dict): Composition of the cold stream (mole fractions).
    m_hot (float): Mass flow rate of the hot stream (kg/s).
    m_cold_in (float): Mass flow rate of the cold stream (kg/s).
    nsp (int): Number of species for the gas model.

    Returns:
    tuple: effectiveness, T_cold_out, H_cold_out
    """
    # Initialize Cantera gas object
    gas = ct.Solution('gri30.yaml')  # Using GRI-Mech 3.0

    # Calculate enthalpy change
    deltaH = H_hot_in - H_hot_out
    H_cold_out = H_cold_in + deltaH

    # Set properties for the cold stream
    gas.TPX = T_cold_in, ct.one_atm, x_cold_in
    h_cold_out = H_cold_out / m_cold_in  # Calculate enthalpy per unit mass
    gas.TP = None, ct.one_atm  # Reset state
    T_cold_out = gas.T  # Temperature of the cold outlet stream

    # Calculate heat capacity rates
    gas.TP = (T_cold_in + T_cold_out) / 2, ct.one_atm
    cp_cold = gas.cp_mass
    Ch_m = m_cold_in * cp_cold

    gas.TP = (T_hot_in + T_hot_out) / 2, ct.one_atm
    cp_hot = gas.cp_mass
    Cc_m = m_hot * cp_hot

    # Determine C_min and Q_max
    C_min = min(Ch_m, Cc_m)
    Q_max = C_min * abs(T_cold_in - T_hot_in)

    # Calculate effectiveness
    effectiveness = abs(deltaH / Q_max)

    return effectiveness, T_cold_out, H_cold_out
