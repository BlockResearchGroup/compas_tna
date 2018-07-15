from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_tna.rhino import ForceArtist

from rhinoforce import RhinoForce


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class ForceActions(object):

    def force_from_form(self):
        self.force = RhinoForce.from_formdiagram(self.form)
        self.force.draw()

    def force_update_attributes(self):
        compas_rhino.update_settings(self.force.attributes)

    def force_update_vertex_attributes(self):
        keys = self.force.select_vertices() or list(self.force.vertices())
        self.force.update_vertex_attributes(keys)

    def force_update_edge_attributes(self):
        keys = self.force.select_edges() or list(self.force.edges())
        self.force.update_edge_attributes(keys)

    def force_move(self):
        pass

    def force_move_vertex(self):
        pass

    def force_move_vertices(self):
        pass

    def force_smooth(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
