import hoomd
from hoomd import hpmc
from hoomd.data.parameterdicts import ParameterDict, TypeParameterDict
from hoomd.data.typeparam import TypeParameter
from hoomd.data.converter import OnlyIf, to_type_converter

from .pair import Pair


@hoomd.logging.modify_namespace(('hpmc', 'pair', 'Union'))
class Union(Pair):
    """Potential of a set of points surrounding a particle body.

    `Union` computes the potential energy of a set of constituent points rigidly
    attached to a particle body. The constituent points on one particle interact
    with consituent points on other particles in a pairwise fashion defined by
    the constituent potential.

    The position and orientation of the constituent points are defined relative to
    the position and orientation of the particle (i.e. in the particle reference frame).

    .. py:attribute:: body

        - ``constituent_types`` (`list` [`str`]): List of types of constituent
          particles.

        - ``positions`` (`list` [`tuple` [`float`, `float`, `float`]]): List of
          relative positions of constituent points.

        - ``orientations`` (`list` [`tuple` [`float`, `float`, `float`,
          `float`]]): List of orientations (as quaternions) of constituent points.

        - ``charges`` (`list` [`float`]): List of charges of constituent points.

        Type: `TypeParameter` [``particle_type``, `dict`]

    Attributes:
        consituent_potential (`hpmc.pair.Pair`):
            Pair potential class defining the interactions of consituent points.
        leaf_capacity (int):
            Maximum number of leaf nodes in the tree data structure used by this
            class.

    """

    def __init__(self, constituent_potential):
        body = TypeParameter('body', 'particle_types', TypeParameterDict(
            OnlyIf(to_type_converter(dict(constituent_types=[str],
                                          positions=[(float,) * 3],
                                          orientations=[(float,) * 4],
                                          charges=[float])),
                   allow_none=True),
            len_keys=1)
        )
        self._add_typeparam(body)

        param_dict = ParameterDict(constituent_potential=OnlyTypes(hpmc.pair.Pair,
                                                                   allow_none=True),
                                   leaf_capacity=int)
        param_dict.update(dict(constituent_potential=constituent_potential))
        param_dict.update(param_dict)

    def _attach_hook(self):
        # no gpu implementation right now, error in that case
        if isinstance(self._simulation.device. hoomd.device.GPU):
            raise RuntimeError("Union Pair Potential is not supported on the GPU")

        # attach the constituent potential
        self.constituent_potential._attach(self._simulation)

        # attach the union potential
        cls = _hpmc.PairPotentialUnion
        cpp_sys_def = self._simulation.state._cpp_sys_def
        self._cpp_obj = cls(cpp_sys_def, self.constituent_potential._cpp_obj)
        super()._attach_hook()

