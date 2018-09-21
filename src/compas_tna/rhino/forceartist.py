from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from compas.geometry import scale_vector

from compas_rhino.artists import MeshArtist


__author__  = 'Tom Van Mele'
__email__   = 'vanmelet@ethz.ch'


__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):

    @property
    def force(self):
        return self.datastructure

    def clear(self):
        super(ForceArtist, self).clear()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
