from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import compas
import compas_rhino
import compas_tna

from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import ForceArtist

from compas_rhino.helpers.selectors import VertexSelector
from compas_rhino.helpers.selectors import EdgeSelector
from compas_rhino.helpers.selectors import FaceSelector

from compas_rhino.helpers.modifiers import VertexModifier
from compas_rhino.helpers.modifiers import EdgeModifier

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['RhinoForce', ]


class RhinoForce(ForceDiagram):

    select_vertex = VertexSelector.select_vertex
    select_vertices = VertexSelector.select_vertices
    update_vertex_attributes = VertexModifier.update_vertex_attributes

    select_edge = EdgeSelector.select_edge
    select_edges = EdgeSelector.select_edges
    update_edge_attributes = EdgeModifier.update_edge_attributes

    def draw(self):
        artist = ForceArtist(self, layer=self.attributes['layer'])
        artist.clear_layer()
        artist.draw_vertices()
        artist.draw_edges()
        artist.redraw()

    def update_edge_attributes(self, keys, names=None):
        if not names:
            names = self.default_edge_attributes.keys()
        names = sorted(names)

        key = keys[0]
        values = self.get_edge_attributes(key, names)

        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != self.get_edge_attribute(key, name):
                        values[i] = '-'
                        break

        values = map(str, values)
        values = compas_rhino.update_named_values(names, values)

        if values:
            for name, value in zip(names, values):
                if value != '-':
                    for key in keys:
                        try:
                            value = literal_eval(value)
                        except (SyntaxError, ValueError, TypeError):
                            pass
                        self.set_edge_attribute(key, name, value)

            return True
        return False


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
