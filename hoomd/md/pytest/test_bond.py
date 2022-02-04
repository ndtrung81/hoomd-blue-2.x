# Copyright (c) 2009-2022 The Regents of the University of Michigan.
# Part of HOOMD-blue, released under the BSD 3-Clause License.

import hoomd
import pytest
import numpy as np

# Test parameters include the class, bond params, force, and energy.
bond_test_parameters = [
    (
        hoomd.md.bond.Harmonic,
        dict(k=30.0, r0=1.6),
        -18.9300,
        5.9724,
    ),
    (
        hoomd.md.bond.Harmonic,
        dict(k=25.0, r0=1.7),
        -18.2750,
        6.6795,
    ),
    (
        hoomd.md.bond.Harmonic,
        dict(k=20.0, r0=1.8),
        -16.6200,
        6.9056,
    ),
    (
        hoomd.md.bond.FENEWCA,
        dict(k=30.0, r0=1.6, epsilon=0.9, sigma=1.1, delta=-0.5),
        282.296,
        70.5638,
    ),
    (
        hoomd.md.bond.FENEWCA,
        dict(k=25.0, r0=1.7, epsilon=1.0, sigma=1.0, delta=-0.5),
        146.288,
        49.2476,
    ),
    (
        hoomd.md.bond.FENEWCA,
        dict(k=20.0, r0=1.8, epsilon=1.1, sigma=0.9, delta=-0.5),
        88.8238,
        35.3135,
    ),
    (
        hoomd.md.bond.Tether,
        dict(k_b=5.0, l_min=0.7, l_c1=0.9, l_c0=1.1, l_max=1.3),
        0,
        0,
    ),
    (
        hoomd.md.bond.Tether,
        dict(k_b=6.0, l_min=0.8, l_c1=1.05, l_c0=1.1, l_max=1.3),
        -0.0244441,
        0.000154384,
    ),
    (
        hoomd.md.bond.Tether,
        dict(k_b=7.0, l_min=0.9, l_c1=1.1, l_c0=1.3, l_max=1.5),
        -3.57225,
        0.0490934,
    ),
]


@pytest.mark.parametrize('bond_cls, params, force, energy', bond_test_parameters)
def test_before_attaching(bond_cls, params, force, energy):
    potential = bond_cls()
    potential.params['A-A'] = params
    for key in params:
        assert potential.params['A-A'][key] == pytest.approx(params[key])


@pytest.fixture(scope='session')
def snapshot_factory(two_particle_snapshot_factory):

    def make_snapshot():
        snapshot = two_particle_snapshot_factory(d=0.969, L=5)
        if snapshot.communicator.rank == 0:
            snapshot.bonds.N = 1
            snapshot.bonds.types = ['A-A']
            snapshot.bonds.typeid[0] = 0
            snapshot.bonds.group[0] = (0, 1)

        return snapshot

    return make_snapshot


@pytest.mark.parametrize('bond_cls, params, force, energy', bond_test_parameters)
def test_after_attaching(snapshot_factory, simulation_factory, bond_cls, params, force, energy):
    sim = simulation_factory(snapshot_factory())

    potential = bond_cls()
    potential.params['A-A'] = params

    sim.operations.integrator = hoomd.md.Integrator(dt=0.005, forces=[potential])
    sim.run(0)

    for key in params:
        assert potential.params['A-A'][key] == pytest.approx(params[key])


@pytest.mark.parametrize('bond_cls, params, force, energy', bond_test_parameters)
def test_forces_and_energies(snapshot_factory, simulation_factory, bond_cls, params, force, energy):
    sim = simulation_factory(snapshot_factory())

    potential = bond_cls()
    potential.params['A-A'] = params

    sim.operations.integrator = hoomd.md.Integrator(dt=0.005, forces=[potential])

    sim.run(0)

    sim_energies = potential.energies
    sim_forces = potential.forces
    if sim.device.communicator.rank == 0:
        assert sum(sim_energies) == pytest.approx(energy, rel=1e-2)
        np.testing.assert_allclose(sim_forces[0], [force, 0.0, 0.0],
                                   rtol=1e-2,
                                   atol=1e-5)
        np.testing.assert_allclose(sim_forces[1], [-1 * force, 0.0, 0.0],
                                   rtol=1e-2,
                                   atol=1e-5)
