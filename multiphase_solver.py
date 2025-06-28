import sys
import cantera as ct


def run_solver(gas_mech, solid_mech, t_end=1.0, dt=1e-5):
    """Run a zero-dimensional multiphase reactor simulation.

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
    # Create gas and solid phase objects
    gas = ct.Solution(gas_mech)
    solid = ct.Solution(solid_mech)

    # Combine them into a multiphase mixture
    mix = ct.MultiPhase([gas, solid])

    # Create the reactor. Cantera's MultiPhase reactor handles multiple phases
    # with possible reactions between them (e.g., heterogeneous chemistry).
    reactor = ct.MultiPhaseReactor(mix)

    sim = ct.ReactorNet([reactor])

    states = ct.SolutionArray(mix, extra=['time'])

    time = 0.0
    while time < t_end:
        time = sim.step()
        states.append(mix.state, time=time)

    return states


def main():
    if len(sys.argv) < 3:
        print("Usage: python multiphase_solver.py GAS_MECH SOLID_MECH [END_TIME]")
        sys.exit(1)

    gas_mech = sys.argv[1]
    solid_mech = sys.argv[2]
    t_end = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    data = run_solver(gas_mech, solid_mech, t_end=t_end)

    # Print final state of each phase
    print('Final gas state:')
    gas = data[-1].solution
    print(gas())

    print('\nFinal solid state:')
    solid = data[-1].adjacent[1]
    print(solid())


if __name__ == '__main__':
    main()
