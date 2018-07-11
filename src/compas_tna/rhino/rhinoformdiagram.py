from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_rhino.helpers.selectors import VertexSelector
from compas_rhino.helpers.selectors import EdgeSelector
from compas_rhino.helpers.modifiers import VertexModifier
from compas_rhino.helpers.modifiers import EdgeModifier

from compas_rhino.utilities import XFunc

from compas_tna.diagrams import FormDiagram
from compas_tna.rhino import FormArtist


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['RhinoFormDiagram', ]


class RhinoFormDiagram(FormDiagram):

    select_vertex   = VertexSelector.select_vertex
    select_vertices = VertexSelector.select_vertices
    select_edge     = EdgeSelector.select_edge
    select_edges    = EdgeSelector.select_edges

    update_vertex_attributes = VertexModifier.update_vertex_attributes
    update_edge_attributes   = EdgeModifier.update_edge_attributes

    def __init__(self):
        super(RhinoFormDiagram, self).__init__()
        self.attributes.update({
            'layer': 'FormDiagram'
        })

    def draw(self):
        vertexcolor = {}
        for name in ('is_fixed', 'is_anchor'):
            a = 'color.vertex:{}'.format(name)
            vertexcolor.update({key: self.attributes[a] for key in self.vertices_where({name: True})})

        artist = FormArtist(self, layer=self.attributes['layer'])
        artist.clear_layer()
        artist.draw_vertices(color=vertexcolor)
        artist.draw_edges(keys=list(self.edges_where({'is_edge': True})))
        artist.draw_faces(fkeys=list(self.faces_where({'is_unloaded': False})))
        artist.redraw()

    # ==========================================================================
    # modify
    # ==========================================================================

    # anchor vertex
    # move vertex
    # pull down vertex
    # smooth pattern
    # subdivide
    # constrain vertex locations

    # --------------------------------------------------------------------------
    # postprocess
    # --------------------------------------------------------------------------

    # def relax(self, fixed):
    #     fd_numpy = XFunc('compas.numerical.fd_numpy')
    #     key_index = self.key_index()
    #     vertices = self.get_vertices_attributes('xyz')
    #     edges = list(self.edges_where({'is_edge': True}))
    #     edges = [(key_index[u], key_index[v]) for u, v in edges]
    #     fixed = list(fixed)
    #     fixed = [key_index[key] for key in fixed]
    #     qs = [self.get_edge_attribute(uv, 'q') for uv in edges]
    #     loads = self.get_vertices_attributes(('px', 'py', 'pz'), (0, 0, 0))
    #     xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, qs, loads)
    #     for key, attr in self.vertices(True):
    #         index = key_index[key]
    #         attr['x'] = xyz[index][0]
    #         attr['y'] = xyz[index][1]
    #         attr['z'] = xyz[index][2]

    # ==========================================================================
    # visualisation
    # ==========================================================================



# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
