# -*- coding: utf-8 -*-
# @Date         : 2016-03-21 09:50:20
# @Author       : Tom Van Mele (vanmelet@ethz.ch)
# @Contributors : ...
# @Version      : $Id$
# @Copyright    : 'Copyright 2014, BLOCK Research Group - ETH Zurich'
# @License      : 'Apache License, Version 2.0'


from compas_rhino.datastructures.mixins import EditAttributes
from compas_rhino.datastructures.mixins import Descriptors
from compas_rhino.datastructures.mixins import GetKeys
from compas_rhino.datastructures.mixins import DisplayLabels

import compas_rhino.utilities as rhino

from compas_tna.forcediagram import ForceDiagram


@rhino.add_gui_helpers((EditAttributes, Descriptors, GetKeys, DisplayLabels, ))
class ForceDiagramRhino(ForceDiagram):

    def __init__(self):
        super(ForceDiagramRhino, self).__init__()
        self.attributes.update({
            'layer': 'ForceDiagram'
        })

    def points(self):
        points = []
        for key in self.vertices_iter():
            points.append({
                'pos'   : self.vertex_coordinates(key),
                'name'  : self.vertex_name(key),
                'color' : self.color['vertex'],
            })
        return points

    def lines(self):
        lines  = []
        for u, v, attr in self.edges_iter(True):
            lines.append({
                'start' : self.vertex_coordinates(u),
                'end'   : self.vertex_coordinates(v),
                'name'  : self.edge_name(u, v),
                'color' : self.color['edge'],
            })
        return lines

    def draw(self):
        rhino.xdraw_points(self.points(), layer=self.layer, redraw=False, clear=True)
        rhino.xdraw_lines(self.lines(), layer=self.layer)
