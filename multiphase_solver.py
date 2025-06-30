import sys
import cantera as ct


def run_solver(gas_mech, solid_mech, t_end=1.0, dt=1e-5):
    """Run a zero-dimensional multiphase reactor simulation with support for
    coupled solid/gas chemistry (e.g. pyrolysis).

    Parameters
    ----------
    gas_mech : str
        Path to the gas mechanism (YAML or CTI file).
    solid_mech : str
        Path to the solid mechanism (YAML or CTI file).
    t_end : float, optional
        End time for the simulation [s]. Default is 1 second.
    dt : float, optional
        Time step for saving data [s]. Default is 1e-5 seconds.
    """
    # Create gas and solid phase objects. Both phases are coupled through a
    # ``MultiPhase`` object so that they share the same temperature while
    # allowing separate sets of species.
    gas = ct.Solution(gas_mech)
    solid = ct.Solution(solid_mech)

    # Combine them into a multiphase mixture
    mix = ct.MultiPhase([gas, solid])

    # Create the reactor. Cantera's MultiPhase reactor handles multiple phases
    # with possible reactions between them (e.g., heterogeneous chemistry).
    reactor = ct.MultiPhaseReactor(mix)

    sim = ct.ReactorNet([reactor])

    # Store the state of each phase separately so that species mass fractions
    # can be analysed for the gas and solid individually.
    gas_states = ct.SolutionArray(gas, extra=['time'])
    solid_states = ct.SolutionArray(solid, extra=['time'])

    time = 0.0
    while time < t_end:
        time = sim.step()
        gas_states.append(gas.state, time=time)
        solid_states.append(solid.state, time=time)

    return gas_states, solid_states


def main():
    if len(sys.argv) < 3:
        print("Usage: python multiphase_solver.py GAS_MECH SOLID_MECH [END_TIME]")
        sys.exit(1)

    gas_mech = sys.argv[1]
    solid_mech = sys.argv[2]
    t_end = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    gas_states, solid_states = run_solver(gas_mech, solid_mech, t_end=t_end)

    # Print final state of each phase. Accessing the last entry of the arrays
    # yields the solution objects for each phase.
    print('Final gas state:')
    print(gas_states[-1]())

    print('\nFinal solid state:')
    print(solid_states[-1]())


if __name__ == '__main__':
    main()
