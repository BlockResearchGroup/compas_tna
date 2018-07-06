from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rhino import MeshArtist
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

    def draw(self):
        artist = MeshArtist(self, layer=self.attributes['layer'])
        artist.clear_layer()
        artist.draw_vertices()
        artist.draw_edges()
        artist.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
