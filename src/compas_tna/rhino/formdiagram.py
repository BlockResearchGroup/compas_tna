# -*- coding: utf-8 -*-
# @Date         : 2016-03-21 09:50:20
# @Author       : Tom Van Mele (vanmelet@ethz.ch)
# @Contributors : ...
# @Version      : $Id$
# @Copyright    : Block Research Group
# @License      : Apache License, Version 2.0


from compas_rhino.datastructures.mixins.attributes import EditAttributes
from compas_rhino.datastructures.mixins.descriptors import Descriptors
from compas_rhino.datastructures.mixins.keys import GetKeys
from compas_rhino.datastructures.mixins.labels import DisplayLabels
from compas_rhino.datastructures.mixins.geometry import DisplayGeometry
import compas_rhino.utilities.drawing as rhino
from compas_rhino.utilities.misc import add_gui_helpers

from compas_tna.diagrams.formdiagram import FormDiagram


#@rhino.add_gui_helpers((EditAttributes, GetKeys, DisplayLabels, Descriptors,DisplayGeometry ))
class FormDiagramRhino(FormDiagram):

    def __init__(self):
        super(FormDiagramRhino, self).__init__()
        self.attributes.update({
            'layer': 'FormDiagram'
        })

    def points(self):
        points = []
        for key, attr in self.vertices_iter(True):
            if attr['is_anchor']:
                color = self.color['vertex:is_anchor']
            else:
                color = self.color['vertex']
            points.append({
                'pos'   : self.vertex_coordinates(key),
                'name'  : self.vertex_name(key),
                'color' : color,
            })
        return points

    def lines(self):
        lines = []
        for u, v, attr in self.edges_iter(True):
            lines.append({
                'start' : self.vertex_coordinates(u),
                'end'   : self.vertex_coordinates(v),
                'name'  : self.edge_name(u, v),
                'color' : self.color['edge'],
            })
        return lines

    # def draw(self):
    #     rhino.xdraw_points(self.points(), layer=self.layer, redraw=False, clear=True)
    #     rhino.xdraw_lines(self.lines(), layer=self.layer)
    def draw(self,
             name=None,
             layer=None,
             clear=True,
             redraw=True,
             show_vertices=False,
             show_edges=True,
             vertex_color=None,
             edge_color=None):
        """"""
        self.name = name or self.name
        self.layer = layer or self.layer
        points = []
        color  = self.color['vertex']
        vcolor = vertex_color or {}
        for key in self.vertex:
            pos  = self.vertex_coordinates(key)
            name = '{0}.vertex.{1}'.format(self.name, key)
            points.append({
                'pos'   : pos,
                'name'  : name,
                'color' : vcolor.get(key, color),
            })
        lines  = []
        color  = self.color['edge']
        ecolor = edge_color or {}
        for u, v in self.edges_iter():
            start = self.vertex_coordinates(u)
            end   = self.vertex_coordinates(v)
            name  = '{0}.edge.{1}-{2}'.format(self.name, u, v)
            lines.append({
                'start' : start,
                'end'   : end,
                'name'  : name,
                'color' : ecolor.get((u, v), color),
                'arrow' : None,
            })
        #rhino.delete_objects(rhino.get_objects('{0}.vertex.*'.format(self.name)))
        #rhino.delete_objects(rhino.get_objects('{0}.edge.*'.format(self.name)))
        if show_vertices:
            rhino.xdraw_points(points, layer=self.layer, clear=clear, redraw=False)
        if show_edges:
            rhino.xdraw_lines(lines, layer=self.layer, clear=False, redraw=True)