import hoomd
import hoomd.hpmc
from hoomd.hpmc import _hpmc
import pytest
import copy

polyhedron_args_1 = {'vertices': [(0, 5, 0), (1, 1, 1), (1, 0, 1),
                                  (0, 1, 1), (1, 1, 0), (0, 0, 1)],
                     'ignore_statistics': 1,
                     'sweep_radius': 0}
polyhedron_args_2 = {'vertices': [(1, 0, 0), (1, 1, 0), (1, 2, 1),
                                  (0, 1, 1), (1, 1, 2), (0, 0, 1)],
                     'ignore_statistics': 0,
                     'sweep_radius': 1}
polyhedron_args_3 = {'vertices': [(0, 0, 0), (1, 1, 1),
                                  (1, 0, 2), (2, 1, 1)],
                     'ignore_statistics': 1,
                     'sweep_radius': 3.125}
polyhedron_args_4 = {'vertices' :[(0, 1, 0), (1, 1, 1), (1, 0, 1),
                                  (0, 1, 1), (1, 1, 0), (0, 0, 1),
                                  (0, 0, 1), (0, 0, 1)],
                     'ignore_statistics': 0,
                     'sweep_radius': 5.5}
polyhedron_args_5 = {'vertices': [(0, 10, 3), (3, 2, 1), (1, 2, 1),
                                  (0, 1, 1), (1, 1, 0), (5, 0, 1),
                                  (0, 10, 1), (9, 5, 1), (0, 0, 1)],
                     'ignore_statistics': 1,
                     'sweep_radius': 6.25}

polyhedron_union_args1 = {'shapes': [polyhedron_args_1, polyhedron_args_2],
                          'positions': [(0, 0, 0), (0, 0, 1)],
                          'orientations': [(1, 0, 0, 0), (1, 0, 0, 0)],
                          'overlap': [1, 1],
                          'capacity': 4,
                          'ignore_statistics': 1}
polyhedron_union_args2 = {'shapes': [polyhedron_args_3, polyhedron_args_2],
                          'positions': [(1, 0, 0), (0, 0, 1)],
                          'orientations': [(1, 1, 0, 0), (1, 0, 0, 0)],
                          'overlap': [1, 2],
                          'capacity': 3,
                          'ignore_statistics': 0}
polyhedron_union_args3 = {'shapes': [polyhedron_args_4, polyhedron_args_2],
                          'positions': [(1, 1, 0), (0, 0, 1)],
                          'orientations': [(1, 0, 1, 0), (1, 0, 0, 0)],
                          'overlap': [1, 3],
                          'capacity': 2,
                          'ignore_statistics': 1}
polyhedron_union_args4 = {'shapes': [polyhedron_args_5, polyhedron_args_2],
                          'positions': [(1, 1, 1), (0, 0, 0)],
                          'orientations': [(1, 0, 0, 1), (1, 0, 0, 0)],
                          'overlap': [1, 0],
                          'capacity': 1,
                          'ignore_statistics': 0}
polyhedron_union_args5 = {'shapes': [polyhedron_args_1, polyhedron_args_3],
                          'positions': [(1, 0, 1), (0, 0, 0)],
                          'orientations': [(1, 0, 0, 0), (1, 1, 0, 0)],
                          'overlap': [0, 1],
                          'capacity': 5,
                          'ignore_statistics': 1}
polyhedron_union_args6 = {'shapes': [polyhedron_args_1, polyhedron_args_4],
                          'positions': [(1, 0, 0), (0, 1, 1)],
                          'orientations': [(1, 0, 0, 0), (1, 0, 1, 0)],
                          'overlap': [2, 1],
                          'capacity': 6,
                          'ignore_statistics': 0}
polyhedron_union_args7 = {'shapes': [polyhedron_args_1, polyhedron_args_5],
                          'positions': [(0, 1, 1), (0, 0, 1)],
                          'orientations': [(1, 0, 0, 0), (1, 0, 0, 1)],
                          'overlap': [3, 1],
                          'capacity': 4,
                          'ignore_statistics': 1}
polyhedron_union_args8 = {'shapes': [polyhedron_args_3, polyhedron_args_4],
                          'positions': [(0, 0, 0), (1, 0, 1)],
                          'orientations': [(1, 0, 0, 1), (1, 1, 0, 0)],
                          'overlap': [0, 0],
                          'capacity': 4,
                          'ignore_statistics': 0}
polyhedron_union_args9 = {'shapes': [polyhedron_args_3, polyhedron_args_5],
                          'positions': [(0, 0, 1), (0, 0, 0)],
                          'orientations': [(1, 0, 1, 0), (1, 0, 1, 0)],
                          'overlap': [2, 2],
                          'capacity': 4,
                          'ignore_statistics': 1}
polyhedron_union_args10 = {'shapes': [polyhedron_args_4, polyhedron_args_5],
                           'positions': [(0, 1, 0), (1, 0, 1)],
                           'orientations': [(1, 1, 0, 1), (1, 0, 0, 0)],
                           'overlap': [3, 3],
                           'capacity': 4,
                           'ignore_statistics': 0}
polyhedron_union_args11 = {'shapes': [polyhedron_args_1, polyhedron_args_2,
                                      polyhedron_args_3],
                           'positions': [(0, 0, 0), (0, 0, 1), (1, 1, 1)],
                           'orientations': [(1, 0, 0, 0), (1, 0, 0, 0),
                                            (1, 0, 0, 1)],
                           'overlap': [1, 1, 1],
                           'capacity': 4,
                           'ignore_statistics': 1}
polyhedron_union_args12 = {'shapes': [polyhedron_args_1, polyhedron_args_3,
                                      polyhedron_args_4],
                           'positions': [(1, 0, 0), (0, 0, 1), (1, 0, 1)],
                           'orientations': [(1, 1, 0, 0), (1, 0, 0, 0),
                                            (1, 0, 1, 0)],
                           'overlap': [1, 2, 1],
                           'capacity': 3,
                           'ignore_statistics': 0}
polyhedron_union_args13 = {'shapes': [polyhedron_args_1, polyhedron_args_4,
                                      polyhedron_args_5],
                           'positions': [(1, 1, 0), (0, 0, 1), (0, 1, 1)],
                           'orientations': [(1, 0, 1, 0), (1, 0, 0, 0),
                                            (1, 1, 0, 0)],
                           'overlap': [1, 3, 0],
                           'capacity': 2, 'ignore_statistics': 1}
polyhedron_union_args14 = {'shapes': [polyhedron_args_2, polyhedron_args_3,
                                      polyhedron_args_4],
                           'positions': [(1, 1, 1), (0, 0, 0), (0, 0, 1)],
                           'orientations': [(1, 0, 0, 1), (1, 0, 0, 0),
                                            (1, 0, 0, 0)],
                           'overlap': [1, 0, 2],
                           'capacity': 4, 'ignore_statistics': 0}
polyhedron_union_args15 = {'shapes': [polyhedron_args_2, polyhedron_args_4,
                                      polyhedron_args_5],
                           'positions': [(0, 0, 0), (0, 1, 1), (1, 0, 1)],
                           'orientations': [(1, 0, 0, 0), (1, 1, 0, 0),
                                            (1, 1, 0, 0)],
                           'overlap': [0, 1, 1],
                           'capacity': 4, 'ignore_statistics': 1}
polyhedron_union_args16 = {'shapes': [polyhedron_args_3, polyhedron_args_4,
                                      polyhedron_args_5],
                           'positions': [(0, 1, 0), (1, 0, 1), (0, 0, 1)],
                           'orientations': [(1, 0, 0, 0), (1, 0, 1, 0),
                                            (1, 0, 0, 0)],
                           'overlap': [2, 1, 0],
                           'capacity': 4, 'ignore_statistics': 0}
polyhedron_union_args17 = {'shapes': [polyhedron_args_1, polyhedron_args_2,
                                      polyhedron_args_3, polyhedron_args_4],
                           'positions': [(0, 0, 0), (0, 0, 1), (1, 1, 1),
                                         (1, 1, 0)],
                           'orientations': [(1, 0, 0, 0), (1, 0, 0, 0),
                                            (1, 0, 0, 0), (1, 0, 0, 0)],
                           'overlap': [1, 1, 1, 1],
                           'capacity': 4, 'ignore_statistics': 1}
polyhedron_union_args18 = {'shapes': [polyhedron_args_1, polyhedron_args_2,
                                      polyhedron_args_3, polyhedron_args_5],
                           'positions': [(1, 0, 0), (0, 0, 1), (1, 0, 1),
                                         (0, 1, 1)],
                           'orientations': [(1, 1, 0, 0), (1, 0, 0, 0),
                                            (1, 0, 0, 0), (1, 0, 0, 1)],
                           'overlap': [1, 1, 2, 0],
                           'capacity': 3, 'ignore_statistics': 0}
polyhedron_union_args19 = {'shapes': [polyhedron_args_1, polyhedron_args_2,
                                      polyhedron_args_4, polyhedron_args_5],
                           'positions': [(1, 1, 0), (1, 0, 1), (0, 0, 0),
                                         (1, 1, 1)],
                           'orientations': [(1, 0, 1, 0), (1, 0, 0, 0),
                                            (1, 0, 0, 0), (1, 0, 1, 0)],
                           'overlap': [1, 2, 1, 1],
                           'capacity': 2, 'ignore_statistics': 1}
polyhedron_union_args20 = {'shapes': [polyhedron_args_1, polyhedron_args_3,
                                      polyhedron_args_4, polyhedron_args_5],
                           'positions': [(1, 1, 1), (0, 0, 1), (0, 0, 0),
                                         (1, 1, 0)],
                           'orientations': [(1, 0, 0, 1), (1, 0, 0, 0),
                                            (1, 0, 0, 0), (1, 1, 0, 0)],
                           'overlap': [0, 1, 1, 0],
                           'capacity': 4, 'ignore_statistics': 0}
polyhedron_union_args21 = {'shapes': [polyhedron_args_2, polyhedron_args_3,
                                      polyhedron_args_4, polyhedron_args_5],
                           'positions': [(0, 0, 0), (0, 1, 1), (1, 1, 1),
                                         (1, 0, 0)],
                           'orientations': [(1, 0, 0, 0), (1, 1, 0, 0),
                                            (1, 0, 0, 1), (1, 0, 0, 0)],
                           'overlap': [1, 2, 2, 2],
                           'capacity': 4, 'ignore_statistics': 1}
polyhedron_union_args22 = {'shapes': [polyhedron_args_1, polyhedron_args_2,
                                      polyhedron_args_3, polyhedron_args_4,
                                      polyhedron_args_5],
                           'positions': [(0, 0, 0), (0, 0, 1), (1, 1, 1),
                                         (1, 1, 0), (2, 2, 0)],
                           'orientations': [(1, 0, 0, 0), (1, 0, 0, 0),
                                            (1, 1, 0, 0), (0, 0, 1, 1),
                                            (1, 0, 0, 0)],
                           'overlap': [1, 1, 0, 0, 1],
                           'capacity': 4, 'ignore_statistics': 1}


def test_dict_conversions():

    polyhedron_args__union1 = _hpmc.mpoly3d_params(polyhedron_union_args1)
    polyhedron_args__dict1 = polyhedron_args__union1.asDict()
    polyhedron_args__union2 = _hpmc.mpoly3d_params(polyhedron_union_args2)
    polyhedron_args__dict2 = polyhedron_args__union2.asDict()
    polyhedron_args__union3 = _hpmc.mpoly3d_params(polyhedron_union_args3)
    polyhedron_args__dict3 = polyhedron_args__union3.asDict()
    polyhedron_args__union4 = _hpmc.mpoly3d_params(polyhedron_union_args4)
    polyhedron_args__dict4 = polyhedron_args__union4.asDict()
    polyhedron_args__union5 = _hpmc.mpoly3d_params(polyhedron_union_args5)
    polyhedron_args__dict5 = polyhedron_args__union5.asDict()
    polyhedron_args__union6 = _hpmc.mpoly3d_params(polyhedron_union_args6)
    polyhedron_args__dict6 = polyhedron_args__union6.asDict()
    polyhedron_args__union7 = _hpmc.mpoly3d_params(polyhedron_union_args7)
    polyhedron_args__dict7 = polyhedron_args__union7.asDict()
    polyhedron_args__union8 = _hpmc.mpoly3d_params(polyhedron_union_args8)
    polyhedron_args__dict8 = polyhedron_args__union8.asDict()
    polyhedron_args__union9 = _hpmc.mpoly3d_params(polyhedron_union_args9)
    polyhedron_args__dict9 = polyhedron_args__union9.asDict()
    polyhedron_args__union10 = _hpmc.mpoly3d_params(polyhedron_union_args10)
    polyhedron_args__dict10 = polyhedron_args__union10.asDict()
    polyhedron_args__union11 = _hpmc.mpoly3d_params(polyhedron_union_args11)
    polyhedron_args__dict11 = polyhedron_args__union11.asDict()
    polyhedron_args__union12 = _hpmc.mpoly3d_params(polyhedron_union_args12)
    polyhedron_args__dict12 = polyhedron_args__union12.asDict()
    polyhedron_args__union13 = _hpmc.mpoly3d_params(polyhedron_union_args13)
    polyhedron_args__dict13 = polyhedron_args__union13.asDict()
    polyhedron_args__union14 = _hpmc.mpoly3d_params(polyhedron_union_args14)
    polyhedron_args__dict14 = polyhedron_args__union14.asDict()
    polyhedron_args__union15 = _hpmc.mpoly3d_params(polyhedron_union_args15)
    polyhedron_args__dict15 = polyhedron_args__union15.asDict()
    polyhedron_args__union16 = _hpmc.mpoly3d_params(polyhedron_union_args16)
    polyhedron_args__dict16 = polyhedron_args__union16.asDict()
    polyhedron_args__union17 = _hpmc.mpoly3d_params(polyhedron_union_args17)
    polyhedron_args__dict17 = polyhedron_args__union17.asDict()
    polyhedron_args__union18 = _hpmc.mpoly3d_params(polyhedron_union_args18)
    polyhedron_args__dict18 = polyhedron_args__union18.asDict()
    polyhedron_args__union19 = _hpmc.mpoly3d_params(polyhedron_union_args19)
    polyhedron_args__dict19 = polyhedron_args__union19.asDict()
    polyhedron_args__union20 = _hpmc.mpoly3d_params(polyhedron_union_args20)
    polyhedron_args__dict20 = polyhedron_args__union20.asDict()
    polyhedron_args__union21 = _hpmc.mpoly3d_params(polyhedron_union_args21)
    polyhedron_args__dict21 = polyhedron_args__union21.asDict()
    polyhedron_args__union22 = _hpmc.mpoly3d_params(polyhedron_union_args22)
    polyhedron_args__dict22 = polyhedron_args__union22.asDict()

    assert polyhedron_args__dict1 == polyhedron_union_args1
    assert polyhedron_args__dict2 == polyhedron_union_args2
    assert polyhedron_args__dict3 == polyhedron_union_args3
    assert polyhedron_args__dict4 == polyhedron_union_args4
    assert polyhedron_args__dict5 == polyhedron_union_args5
    assert polyhedron_args__dict6 == polyhedron_union_args6
    assert polyhedron_args__dict7 == polyhedron_union_args7
    assert polyhedron_args__dict8 == polyhedron_union_args8
    assert polyhedron_args__dict9 == polyhedron_union_args9
    assert polyhedron_args__dict10 == polyhedron_union_args10
    assert polyhedron_args__dict11 == polyhedron_union_args11
    assert polyhedron_args__dict12 == polyhedron_union_args12
    assert polyhedron_args__dict13 == polyhedron_union_args13
    assert polyhedron_args__dict14 == polyhedron_union_args14
    assert polyhedron_args__dict15 == polyhedron_union_args15
    assert polyhedron_args__dict16 == polyhedron_union_args16
    assert polyhedron_args__dict17 == polyhedron_union_args17
    assert polyhedron_args__dict18 == polyhedron_union_args18
    assert polyhedron_args__dict19 == polyhedron_union_args19
    assert polyhedron_args__dict20 == polyhedron_union_args20
    assert polyhedron_args__dict21 == polyhedron_union_args21
    assert polyhedron_args__dict22 == polyhedron_union_args22


def test_shape_params():

    mc = hoomd.hpmc.integrate.ConvexSpheropolyhedronUnion(23456)

    mc.shape['A'] = dict()
    assert mc.shape['A']['shapes'] is None
    assert mc.shape['A']['positions'] is None
    assert mc.shape['A']['orientations'] is None
    assert mc.shape['A']['overlap'] == 1
    assert mc.shape['A']['capacity'] == 4
    assert mc.shape['A']['ignore_statistics'] is False

    mc.shape['A'] = dict(shapes=polyhedron_union_args1['shapes'])
    assert mc.shape['A']['shapes']  == polyhedron_union_args1['shapes']
    assert mc.shape['A']['positions'] is None
    assert mc.shape['A']['orientations'] is None
    assert mc.shape['A']['overlap'] == 1
    assert mc.shape['A']['capacity'] == 4
    assert mc.shape['A']['ignore_statistics'] is False

    mc.shape['A'] = dict(positions=polyhedron_union_args2['positions'],
                         ignore_statistics=True)
    assert mc.shape['A']['shapes'] is None
    assert mc.shape['A']['positions'] == polyhedron_union_args2['positions']
    assert mc.shape['A']['orientations'] is None
    assert mc.shape['A']['overlap'] == 1
    assert mc.shape['A']['capacity'] == 4
    assert mc.shape['A']['ignore_statistics'] is True

    mc.shape['A'] = polyhedron_union_args3
    assert mc.shape['A']['shapes'] == polyhedron_union_args3['shapes']
    assert mc.shape['A']['positions'] == polyhedron_union_args3['positions']
    assert mc.shape['A']['orientations'] == polyhedron_union_args3['orientations']
    assert mc.shape['A']['overlap'] == polyhedron_union_args3['overlap']
    assert mc.shape['A']['capacity'] == polyhedron_union_args3['capacity']
    assert mc.shape['A']['ignore_statistics'] == polyhedron_union_args3['ignore_statistics']



def test_shape_params_attached(device, dummy_simulation_factory):

    mc = hoomd.hpmc.integrate.ConvexSpheropolyhedronUnion(23456)
    mc.shape['A'] = polyhedron_union_args1
    mc.shape['B'] = polyhedron_union_args2
    mc.shape['C'] = polyhedron_union_args3
    mc.shape['D'] = polyhedron_union_args4
    mc.shape['E'] = polyhedron_union_args5
    mc.shape['F'] = polyhedron_union_args6
    mc.shape['G'] = polyhedron_union_args7
    mc.shape['H'] = polyhedron_union_args8
    mc.shape['I'] = polyhedron_union_args9
    mc.shape['J'] = polyhedron_union_args10
    mc.shape['K'] = polyhedron_union_args11

    sim = dummy_simulation_factory(particle_types=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])
    sim.operations.add(mc)
    sim.operations.schedule()


    assert mc.shape['A']['shapes'] == polyhedron_union_args1['shapes']
    assert mc.shape['A']['positions'] == polyhedron_union_args1['positions']
    assert mc.shape['A']['orientations'] == polyhedron_union_args1['orientations']
    assert mc.shape['A']['overlap'] == polyhedron_union_args1['overlap']
    assert mc.shape['A']['capacity'] == polyhedron_union_args1['capacity']
    assert mc.shape['A']['ignore_statistics'] == polyhedron_union_args1['ignore_statistics']

    assert mc.shape['B']['shapes'] == polyhedron_union_args2['shapes']
    assert mc.shape['B']['positions'] == polyhedron_union_args2['positions']
    assert mc.shape['B']['orientations'] == polyhedron_union_args2['orientations']
    assert mc.shape['B']['overlap'] == polyhedron_union_args2['overlap']
    assert mc.shape['B']['capacity'] == polyhedron_union_args2['capacity']
    assert mc.shape['B']['ignore_statistics'] == polyhedron_union_args2['ignore_statistics']

    assert mc.shape['C']['shapes'] == polyhedron_union_args3['shapes']
    assert mc.shape['C']['positions'] == polyhedron_union_args3['positions']
    assert mc.shape['C']['orientations'] == polyhedron_union_args3['orientations']
    assert mc.shape['C']['overlap'] == polyhedron_union_args3['overlap']
    assert mc.shape['C']['capacity'] == polyhedron_union_args3['capacity']
    assert mc.shape['C']['ignore_statistics'] == polyhedron_union_args3['ignore_statistics']

    assert mc.shape['D']['shapes'] == polyhedron_union_args4['shapes']
    assert mc.shape['D']['positions'] == polyhedron_union_args4['positions']
    assert mc.shape['D']['orientations'] == polyhedron_union_args4['orientations']
    assert mc.shape['D']['overlap'] == polyhedron_union_args4['overlap']
    assert mc.shape['D']['capacity'] == polyhedron_union_args4['capacity']
    assert mc.shape['D']['ignore_statistics'] == polyhedron_union_args4['ignore_statistics']

    assert mc.shape['E']['shapes'] == polyhedron_union_args5['shapes']
    assert mc.shape['E']['positions'] == polyhedron_union_args5['positions']
    assert mc.shape['E']['orientations'] == polyhedron_union_args5['orientations']
    assert mc.shape['E']['overlap'] == polyhedron_union_args5['overlap']
    assert mc.shape['E']['capacity'] == polyhedron_union_args5['capacity']
    assert mc.shape['E']['ignore_statistics'] == polyhedron_union_args5['ignore_statistics']

    assert mc.shape['F']['shapes'] == polyhedron_union_args6['shapes']
    assert mc.shape['F']['positions'] == polyhedron_union_args6['positions']
    assert mc.shape['F']['orientations'] == polyhedron_union_args6['orientations']
    assert mc.shape['F']['overlap'] == polyhedron_union_args6['overlap']
    assert mc.shape['F']['capacity'] == polyhedron_union_args6['capacity']
    assert mc.shape['F']['ignore_statistics'] == polyhedron_union_args6['ignore_statistics']

    assert mc.shape['G']['shapes'] == polyhedron_union_args7['shapes']
    assert mc.shape['G']['positions'] == polyhedron_union_args7['positions']
    assert mc.shape['G']['orientations'] == polyhedron_union_args7['orientations']
    assert mc.shape['G']['overlap'] == polyhedron_union_args7['overlap']
    assert mc.shape['G']['capacity'] == polyhedron_union_args7['capacity']
    assert mc.shape['G']['ignore_statistics'] == polyhedron_union_args7['ignore_statistics']

    assert mc.shape['H']['shapes'] == polyhedron_union_args8['shapes']
    assert mc.shape['H']['positions'] == polyhedron_union_args8['positions']
    assert mc.shape['H']['orientations'] == polyhedron_union_args8['orientations']
    assert mc.shape['H']['overlap'] == polyhedron_union_args8['overlap']
    assert mc.shape['H']['capacity'] == polyhedron_union_args8['capacity']
    assert mc.shape['H']['ignore_statistics'] == polyhedron_union_args8['ignore_statistics']

    assert mc.shape['I']['shapes'] == polyhedron_union_args9['shapes']
    assert mc.shape['I']['positions'] == polyhedron_union_args9['positions']
    assert mc.shape['I']['orientations'] == polyhedron_union_args9['orientations']
    assert mc.shape['I']['overlap'] == polyhedron_union_args9['overlap']
    assert mc.shape['I']['capacity'] == polyhedron_union_args9['capacity']
    assert mc.shape['I']['ignore_statistics'] == polyhedron_union_args9['ignore_statistics']

    assert mc.shape['J']['shapes'] == polyhedron_union_args10['shapes']
    assert mc.shape['J']['positions'] == polyhedron_union_args10['positions']
    assert mc.shape['J']['orientations'] == polyhedron_union_args10['orientations']
    assert mc.shape['J']['overlap'] == polyhedron_union_args10['overlap']
    assert mc.shape['J']['capacity'] == polyhedron_union_args10['capacity']
    assert mc.shape['J']['ignore_statistics'] == polyhedron_union_args10['ignore_statistics']

    assert mc.shape['K']['shapes'] == polyhedron_union_args11['shapes']
    assert mc.shape['K']['positions'] == polyhedron_union_args11['positions']
    assert mc.shape['K']['orientations'] == polyhedron_union_args11['orientations']
    assert mc.shape['K']['overlap'] == polyhedron_union_args11['overlap']
    assert mc.shape['K']['capacity'] == polyhedron_union_args11['capacity']
    assert mc.shape['K']['ignore_statistics'] == polyhedron_union_args11['ignore_statistics']

    polyhedron_union_args1_invalid = copy.deepcopy(polyhedron_union_args1)
    polyhedron_union_args2_invalid = copy.deepcopy(polyhedron_union_args2)
    polyhedron_union_args3_invalid = copy.deepcopy(polyhedron_union_args3)
    polyhedron_union_args4_invalid = copy.deepcopy(polyhedron_union_args4)
    polyhedron_union_args5_invalid = copy.deepcopy(polyhedron_union_args5)
    polyhedron_union_args6_invalid = copy.deepcopy(polyhedron_union_args6)
    polyhedron_union_args7_invalid = copy.deepcopy(polyhedron_union_args7)
    polyhedron_union_args8_invalid = copy.deepcopy(polyhedron_union_args8)
    polyhedron_union_args9_invalid = copy.deepcopy(polyhedron_union_args9)
    polyhedron_union_args10_invalid = copy.deepcopy(polyhedron_union_args10)
    polyhedron_union_args11_invalid = copy.deepcopy(polyhedron_union_args11)
    polyhedron_union_args12_invalid = copy.deepcopy(polyhedron_union_args12)

    polyhedron_union_args1_invalid['shapes'] = 'invalid'
    polyhedron_union_args2_invalid['shapes'] = 1
    polyhedron_union_args3_invalid['shapes'] = [1, 2, 3]
    polyhedron_union_args4_invalid['orientations'] = 'invalid'
    polyhedron_union_args5_invalid['orientations'] = 1
    polyhedron_union_args6_invalid['positions'] = 1
    polyhedron_union_args7_invalid['positions'] = [1, 2, 3]
    polyhedron_union_args8_invalid['positions'] = 'invalid'
    polyhedron_union_args9_invalid['overlap'] = 'invalid'
    polyhedron_union_args10_invalid['capacity'] = 'invalid'
    polyhedron_union_args11_invalid['capacity'] = [1, 2, 3]
    polyhedron_union_args12_invalid['ignore_statistics'] = 'invalid'

    # check for errors on invalid input
    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args1_invalid

    with pytest.raises(TypeError):
        mc.shape['A'] = polyhedron_union_args2_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args3_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args4_invalid

    with pytest.raises(TypeError):
        mc.shape['A'] = polyhedron_union_args5_invalid

    with pytest.raises(TypeError):
        mc.shape['A'] = polyhedron_union_args6_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args7_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args8_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args9_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args10_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args11_invalid

    with pytest.raises(RuntimeError):
        mc.shape['A'] = polyhedron_union_args12_invalid
