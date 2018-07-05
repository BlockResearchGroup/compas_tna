from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_tna.diagrams import ForceDiagram


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['RhinoForceDiagram', ]


class RhinoForceDiagram(ForceDiagram):

    def __init__(self):
        super(RhinoForceDiagram, self).__init__()
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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
