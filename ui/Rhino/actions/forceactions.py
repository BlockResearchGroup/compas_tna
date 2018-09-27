from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import compas
import compas_rhino
import compas_tna

from compas.geometry import mesh_smooth_area

from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import ForceArtist
from compas_tna.rhino import DiagramHelper

HERE = os.path.abspath(os.path.dirname(__file__))

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__all__ = ['ForceActions']


class ForceActions(object):

    def force_update_attributes(self):
        compas_rhino.update_settings(self.force.attributes)

    def force_from_form(self):
        self.force = ForceDiagram.from_formdiagram(self.form)
        self.force.draw(layer=self.settings['force.layer'])

    def force_update_vertex_attr(self):
        keys = DiagramHelper.select_vertices(self.force)
        if not keys:
            return
        if DiagramHelper.update_vertex_attributes(self.force, keys):
            self.force.draw(layer=self.settings['force.layer'])

    def force_update_edge_attr(self):
        keys = DiagramHelper.select_edges(self.force)
        if not keys:
            return
        if DiagramHelper.update_edge_attributes(self.force, keys):
            self.force.draw(layer=self.settings['force.layer'])

    def force_move(self):
        if DiagramHelper.move(self.force):
            self.force.draw(layer=self.settings['force.layer'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
