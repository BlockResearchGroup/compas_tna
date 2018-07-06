from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rhino import MeshArtist
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

    def draw(self):
        artist = MeshArtist(self, layer=self.attributes['layer'])
        artist.clear_layer()
        artist.draw_vertices()
        artist.draw_edges(keys=list(self.edges_where({'is_edge': True})))
        artist.draw_faces(fkeys=list(self.faces_where({'is_unloaded': False})))
        artist.redraw()

    # ==========================================================================
    # modify
    # ==========================================================================

    # anchor vertex
    # move vertex
    # ...

    # ==========================================================================
    # visualisation
    # ==========================================================================

    def show_reactions(self):
        pass

    def hide_reactions(self):
        pass

    def show_selfweight(self):
        pass

    def hide_selfweight(self):
        pass

    def show_loads(self):
        pass

    def hide_loads(self):
        pass

    def show_residuals(self):
        pass

    def hide_residuals(self):
        pass

    def show_axial(self):
        pass

    def hide_axial(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
