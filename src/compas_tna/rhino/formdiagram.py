from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_tna.diagrams import FormDiagram


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['RhinoFormDiagram', ]


class RhinoFormDiagram(FormDiagram):

    def __init__(self):
        super(RhinoFormDiagram, self).__init__()
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
        if show_vertices:
            compas_rhino.xdraw_points(points, layer=self.layer, clear=clear, redraw=False)
        if show_edges:
            compas_rhino.xdraw_lines(lines, layer=self.layer, clear=False, redraw=True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
