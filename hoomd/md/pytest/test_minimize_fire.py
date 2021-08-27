import numpy as np
import pytest

import hoomd
from hoomd.conftest import pickling_check
from hoomd import md


def _assert_correct_params(fire, param_dict):
    """Make sure the parameters in the dictionary match with fire."""
    for param in param_dict:
        assert getattr(fire, param) == param_dict[param]


def _make_random_params():
    """Get random values for the fire parameters."""
    params = {
        'dt': np.random.rand(),
        'aniso': 'auto',
        'min_steps_adapt': np.random.randint(1, 25),
        'finc_dt': 1 + np.random.rand(),
        'fdec_dt': np.random.rand(),
        'alpha_start': np.random.rand(),
        'fdec_alpha': np.random.rand(),
        'force_tol': np.random.rand(),
        'angmom_tol': np.random.rand(),
        'energy_tol': np.random.rand(),
        'min_steps_conv': np.random.randint(1, 15)
    }
    return params


def _set_and_check_new_params(fire):
    """Set params to random values, then assert they are correct."""
    # set the parameters to random values
    new_params = _make_random_params()
    for param in new_params:
        setattr(fire, param, new_params[param])

    # make sure they were set right
    _assert_correct_params(fire, new_params)
    return new_params


def _assert_error_if_nonpositive(fire):
    """Make sure error is raised if properties set to nonpositive values."""
    negative_value = -np.random.randint(0, 26)
    with pytest.raises(ValueError):
        fire.min_steps_adapt = negative_value

    with pytest.raises(ValueError):
        fire.min_steps_conv = negative_value


def test_get_set_params(simulation_factory, two_particle_snapshot_factory):
    """Assert we can get/set params when not attached and when attached."""
    fire = md.minimize.FIRE(dt=0.01)
    default_params = {
        'dt': 0.01,
        'aniso': 'auto',
        'min_steps_adapt': 5,
        'finc_dt': 1.1,
        'fdec_dt': 0.5,
        'alpha_start': 0.1,
        'fdec_alpha': 0.99,
        'force_tol': 0.1,
        'angmom_tol': 0.1,
        'energy_tol': 1e-5,
        'min_steps_conv': 10
    }
    _assert_correct_params(fire, default_params)

    new_params = _set_and_check_new_params(fire)

    _assert_error_if_nonpositive(fire)

    # attach to simulation
    snap = two_particle_snapshot_factory(d=2.34)
    sim = simulation_factory(snap)
    sim.operations.integrator = fire
    sim.run(0)

    # make sure the params are still right after attaching
    _assert_correct_params(fire, new_params)

    _set_and_check_new_params(fire)

    _assert_error_if_nonpositive(fire)


def test_run_minimization(lattice_snapshot_factory, simulation_factory):
    """Run a short minimization simulation."""


def test_pickling(lattice_snapshot_factory, simulation_factory):
    """Assert the minimizer can be pickled when attached/unattached."""
    snap = lattice_snapshot_factory(a=1.5, n=5)
    sim = simulation_factory(snap)

    nve = md.methods.NVE(hoomd.filter.All())

    fire = md.minimize.FIRE(dt=0.0025, methods=[nve])

    pickling_check(fire)
    sim.operations.integrator = fire
    sim.run(0)
    pickling_check(fire)


def _try_attach_to_fire(sim, method, should_error=False):
    """Try attaching the given method to FIRE."""
    fire = md.minimize.FIRE(dt=0.0025)
    sim.operations.integrator = fire
    fire.methods.append(method)
    if should_error:
        print(method.__class__.__name__)
        with pytest.raises(RuntimeError):
            sim.run(0)
    else:
        sim.run(0)


def test_validate_methods(lattice_snapshot_factory, simulation_factory):
    """Make sure only certain methods can be attached to FIRE."""
    snap = lattice_snapshot_factory(a=1.5, n=5)

    nve = md.methods.NVE(hoomd.filter.All())
    nph = md.methods.NPH(hoomd.filter.All(), S=1, tauS=1, couple='none')
    brownian = md.methods.Brownian(hoomd.filter.All(), kT=1)
    methods = [(nve, False), (nph, False), (brownian, True)]
    for method, should_error in methods:
        sim = simulation_factory(snap)
        _try_attach_to_fire(sim, method, should_error)

