from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from compas_rhino.artists import MeshArtist


__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):

    @property
    def force(self):
        return self.datastructure


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
