import cantera as ct

def create_gas_structure():
    """
    Initialize a gas object for SOFC modeling.
    """
    filename = 'gri30.yaml'  # GRI 3.0 mechanism
    phasename = 'gri30'
    try:
        gas = ct.Solution(filename, phasename)
        NSP = gas.n_species
        nrxn = gas.n_reactions
        print(f"Gas structure created with {NSP} species and {nrxn} reactions.")
        return gas
    except Exception as e:
        print(f"Error while creating gas structure: {e}")
        return None

# Example usage
if __name__ == "__main__":
    gas = create_gas_structure()
    if gas:
        print("Gas object successfully created.")
        print("smile")
        