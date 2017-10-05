# Copyright (c) 2009-2017 The Regents of the University of Michigan
# This file is part of the HOOMD-blue project, released under the BSD 3-Clause License.

# Maintainer: mphoward

R""" Multiparticle collision dynamics.

Simulating complex fluids and soft matter using conventional molecular dynamics
methods (:py:mod:`hoomd.md`) can be computationally demanding due to large
disparities in the relevant length and time scales between molecular-scale
solvents and mesoscale solutes such as polymers, colloids, and deformable
materials like cells. One way to overcome this challenge is to simplify the model
for the solvent while retaining its most important interactions with the solute.
MPCD is a particle-based simulation method for resolving solvent-mediated
fluctuating hydrodynamic interactions with a microscopically detailed solute
model. This method has been successfully applied to a simulate a broad class
of problems, including polymer solutions and colloidal suspensions both in and
out of equilibrium.

.. rubric:: Algorithm

In MPCD, the solvent is represented by point particles having continuous
positions and velocities. The solvent particles propagate in alternating
streaming and collision steps. During the streaming step, particles evolve
according to Newton's equations of motion. Typically, no external forces are
applied to the solvent, and streaming is straightforward with a large time step.
Particles are then binned into local cells and undergo a stochastic multiparticle
collision within the cell. Collisions lead to the build up of hydrodynamic
interactions, and the frequency and nature of the collisions, along with the
solvent properties, determine the transport coefficients. All standard collision
rules conserve linear momentum within the cell and can optionally be made to
enforce angular-momentum conservation. Currently, we have implemented
the following collision rules with linear-momentum conservation only:

    * :py:obj:`~hoomd.mpcd.collide.srd` -- Stochastic rotation dynamics
    * :py:obj:`~hoomd.mpcd.collide.at` -- Andersen thermostat

Solute particles can be coupled to the solvent during the collision step. This
is particularly useful for soft materials like polymers. Standard molecular
dynamics integration can be applied to the solute. Coupling to the MPCD
solvent introduces both hydrodynamic interactions and a heat bath that acts as
a thermostat. In the future, fluid-solid coupling will also be introduced during
the streaming step to couple hard particles and boundaries.

Details of this implementation of the MPCD algorithm for HOOMD-blue can be found
in Howard et al. (2017).

.. rubric:: Getting started

MPCD is intended to be used as an add-on to the standard MD methods in
:py:mod:`hoomd.md`. To get started, take the following steps:

    1. Initialize any solute particles using standard methods (:py:mod:`hoomd.init`).
    2. Initialize the MPCD solvent particles using one of the methods in
       :py:mod:`.mpcd.init`. Additional details on how to manipulate the solvent
       particle data can be found in :py:mod:`.mpcd.data`.
    3. Create an MPCD :py:obj:`~hoomd.mpcd.integrator`.
    4. Choose the appropriate streaming method from :py:mod:`.mpcd.stream`.
    5. Choose the appropriate collision rule from :py:mod:`.mpcd.collide`, and set
       the collision rule parameters. If necessary, adjust the MPCD cell size.
    6. Setup an MD integrator and any interactions between solute particles.
    7. Optionally, configure the sorting frequency to improve performance (see
       :py:obj:`update.sort`).
    8. Run your simulation!

Example script for a pure bulk SRD fluid::

    import hoomd
    hoomd.context.initialize()
    from hoomd import mpcd

    # Initialize (empty) solute in box.
    box = hoomd.data.boxdim(L=100.)
    hoomd.init.read_snapshot(hoomd.data.make_snapshot(N=0, box=box))

    # Initialize MPCD particles and set sorting period.
    s = mpcd.init.make_random(N=int(10*box.get_volume()), kT=1.0, seed=7)
    s.sorter.set_period(period=25)

    # Create MPCD integrator with streaming and collision methods.
    mpcd.integrator(dt=0.1)
    mpcd.stream.bulk(period=1)
    mpcd.collide.srd(seed=42, period=1, angle=130., kT=1.0)

    hoomd.run(2000)

.. rubric:: Stability

:py:mod:`hoomd.mpcd` is currently **unstable**. (It is under development.) When
upgrading from version 2.x to 2.y (y > x), existing job scripts may need to be
updated.

**Maintainer:** Michael P. Howard, Princeton University.
"""

# these imports are necessary in order to link derived types between modules
import hoomd
from hoomd import _hoomd
from hoomd.md import _md

from hoomd.mpcd import collide
from hoomd.mpcd import data
from hoomd.mpcd import init
from hoomd.mpcd import stream
from hoomd.mpcd import update

class integrator(hoomd.integrate._integrator):
    """ MPCD integrator

    Args:
        dt (float): Each time step of the simulation :py:func:`hoomd.run()` will
                    advance the real time of the system forward by *dt* (in time units).
        aniso (bool): Whether to integrate rotational degrees of freedom (bool),
                      default None (autodetect).

    The MPCD integrator enables the MPCD algorithm concurrently with standard
    MD :py:mod:`~hoomd.md.integrate` methods. An integrator must be created
    in order for :py:mod:`~hoomd.mpcd.stream` and :py:mod:`~hoomd.mpcd.collide`
    methods to take effect. Embedded MD particles require the creation of an
    appropriate integration method. Typically, this will just be
    :py:class:`~hoomd.md.integrate.nve`.

    In MPCD simulations, *dt* defines the amount of time that the system is advanced
    forward every time step. MPCD streaming and collision steps can be defined to
    occur in multiples of *dt*. In these cases, any MD particle data will be updated
    every *dt*, while the MPCD particle data is updated asynchronously for performance.
    For example, if MPCD streaming happens every 5 steps, then the particle data will be
    updated as follows::

                0     1     2     3     4     5
        MD:     |---->|---->|---->|---->|---->|
        MPCD:   |---------------------------->|

    If the MPCD particle data is accessed via the snapshot interface at time
    step 3, it will actually contain the MPCD particle data for time step 5.
    The MD particles can be read at any time step because their positions
    are updated every step.

    Examples::

        mpcd.integrator(dt=0.1)
        mpcd.integrator(dt=0.01, aniso=True)

    """
    def __init__(self, dt, aniso=None):
        # check system is initialized
        if hoomd.context.current.mpcd is None:
            hoomd.context.msg.error('mpcd.integrate: an MPCD system must be initialized before the integrator\n')
            raise RuntimeError('MPCD system not initialized')

        hoomd.integrate._integrator.__init__(self)

        self.supports_methods = True
        self.dt = dt
        self.aniso = aniso
        self.metadata_fields = ['dt','aniso']

        # configure C++ integrator
        self.cpp_integrator = _mpcd.Integrator(hoomd.context.current.mpcd.data, self.dt)
        if hoomd.context.current.mpcd.comm is not None:
            self.cpp_integrator.setMPCDCommunicator(hoomd.context.current.mpcd.comm)
        hoomd.context.current.system.setIntegrator(self.cpp_integrator)

        if self.aniso is not None:
            hoomd.util.quiet_status()
            self.set_params(aniso=aniso)
            hoomd.util.unquiet_status()

    _aniso_modes = {
        None: _md.IntegratorAnisotropicMode.Automatic,
        True: _md.IntegratorAnisotropicMode.Anisotropic,
        False: _md.IntegratorAnisotropicMode.Isotropic}

    def set_params(self, dt=None, aniso=None):
        """ Changes parameters of an existing integration mode.

        Args:
            dt (float): New time step delta (if set) (in time units).
            aniso (bool): Anisotropic integration mode (bool), default None (autodetect).

        Examples::

            integrator.set_params(dt=0.007)
            integrator.set_params(dt=0.005, aniso=False)

        """
        hoomd.util.print_status_line()
        self.check_initialization()

        # change the parameters
        if dt is not None:
            self.dt = dt
            self.cpp_integrator.setDeltaT(dt)

        if aniso is not None:
            if aniso in self._aniso_modes:
                anisoMode = self._aniso_modes[aniso]
            else:
                hoomd.context.msg.error("mpcd.integrate: unknown anisotropic mode {}.\n".format(aniso))
                raise RuntimeError("Error setting anisotropic integration mode.")
            self.aniso = aniso
            self.cpp_integrator.setAnisotropicMode(anisoMode)

    def update_methods(self):
        self.check_initialization()

        # update the integration methods that are set
        self.cpp_integrator.removeAllIntegrationMethods()
        for m in hoomd.context.current.integration_methods:
            self.cpp_integrator.addIntegrationMethod(m.cpp_method)

        # ensure that the streaming and collision methods are up to date
        stream = hoomd.context.current.mpcd._stream
        if stream is not None:
            self.cpp_integrator.setStreamingMethod(stream._cpp)
        else:
            hoomd.context.msg.warning("Running mpcd without a streaming method!\n")
            self.cpp_integrator.removeStreamingMethod()

        collide = hoomd.context.current.mpcd._collide
        if collide is not None:
            if stream is not None and collide.period % stream.period != 0:
                hoomd.context.msg.error('mpcd.integrate: collision period must be multiple of integration period\n')
                raise ValueError('Collision period must be multiple of integration period')

            self.cpp_integrator.setCollisionMethod(collide._cpp)
        else:
            hoomd.context.msg.warning("Running mpcd without a collision method!\n")
            self.cpp_integrator.removeCollisionMethod()
