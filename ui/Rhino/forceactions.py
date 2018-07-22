from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_tna.rhino import ForceArtist

from rhinoforce import RhinoForce

try:
    import Rhino
    from Rhino.Geometry import Point3d
except ImportError:
    import sys
    if 'ironpython' in sys.version.lower():
        raise


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class ForceActions(object):

    # ==========================================================================
    # construct
    # ==========================================================================

    def force_from_form(self):
        self.force = RhinoForce.from_formdiagram(self.form)
        self.force.draw()

    # ==========================================================================
    # select
    # ==========================================================================

    def force_select_parallel_edges(self):
        pass

    def force_select_continuous_edges(self):
        pass

    def force_select_boundary_vertices(self):
        pass

    def force_select_boundary_edges(self):
        pass

    # ==========================================================================
    # update
    # ==========================================================================

    def force_update_attributes(self):
        compas_rhino.update_settings(self.force.attributes)

    def force_update_vertex_attributes(self):
        keys = self.force.select_vertices() or list(self.force.vertices())
        self.force.update_vertex_attributes(keys)

    def force_update_edge_attributes(self):
        keys = self.force.select_edges() or list(self.force.edges())
        self.force.update_edge_attributes(keys)

    # ==========================================================================
    # modify
    # ==========================================================================

    def force_move(self):
        color  = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor

        key_index = self.force.key_index()
        origin = self.force.get_vertices_attributes('xyz')
        vertices = self.force.get_vertices_attributes('xyz')
        edges = [(key_index[u], key_index[v]) for u, v in self.force.edges()]
        start = compas_rhino.pick_point('Point to move from?')

        if not start:
            return

        def OnDynamicDraw(sender, e):
            current = list(e.CurrentPoint)
            vec = [current[i] - start[i] for i in range(3)]
            for index, xyz in enumerate(vertices):
                xyz[0] = origin[index][0] + vec[0]
                xyz[1] = origin[index][1] + vec[1]
                xyz[2] = origin[index][2] + vec[2]
            for u, v in iter(edges):
                sp = vertices[u]
                ep = vertices[v]
                sp = Point3d(*sp)
                ep = Point3d(*ep)
                e.Display.DrawDottedLine(sp, ep, color)

        guids = compas_rhino.get_objects(name='{0}.*'.format(self.force.attributes['name']))
        compas_rhino.delete_objects(guids)

        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Point to move to?')
        gp.DynamicDraw += OnDynamicDraw
        gp.Get()

        if gp.CommandResult() == Rhino.Commands.Result.Success:
            end = list(gp.Point())
            vec = [end[i] - start[i] for i in range(3)]
            for key, attr in self.force.vertices(True):
                attr['x'] += vec[0]
                attr['y'] += vec[1]
                attr['z'] += vec[2]

        self.force.draw()

    def force_move_vertices(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
