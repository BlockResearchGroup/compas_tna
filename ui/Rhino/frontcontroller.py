from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import FormArtist

from compas_rhino.helpers.selectors import VertexSelector
from compas_rhino.helpers.selectors import EdgeSelector
from compas_rhino.helpers.selectors import FaceSelector

from compas_rhino.helpers.modifiers import VertexModifier
from compas_rhino.helpers.modifiers import EdgeModifier
from compas_rhino.helpers.modifiers import FaceModifier


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class RhinoForm(FormDiagram):

    select_vertex = VertexSelector.select_vertex
    select_vertices = VertexSelector.select_vertices
    update_vertex_attributes = VertexModifier.update_vertex_attributes

    select_edge = EdgeSelector.select_edge
    select_edges = EdgeSelector.select_edges
    update_edge_attributes = EdgeModifier.update_edge_attributes

    def draw(self):
        artist = FormArtist(self, layer=self.attributes['layer'])
        artist.clear_layer()
        artist.draw_vertices(
            keys=list(self.vertices_where({'is_external': False}))
        )
        artist.draw_edges(
            keys=list(self.edges_where({'is_edge': True, 'is_external': False}))
        )
        artist.draw_faces(
            fkeys=list(self.faces_where({'is_loaded': True})),
            join_faces=True
        )
        artist.redraw()


class TNAFrontController(object):

    instancename = 'tna'

    def __init__(self):
        self.settings = {}
        self.form = None
        self.force = None

    def init(self):
        pass

    def update_settings(self):
        compas_rhino.update_settings(self.settings)

    # ==========================================================================
    # forward
    # ==========================================================================

    # ==========================================================================
    # form
    # ==========================================================================    

    def form_from_obj(self):
        path = compas_rhino.select_file(folder=compas_tna.DATA, filter='OBJ files (*.obj)|*.obj||')
        if not path:
            return
        self.form = RhinoForm.from_obj(path)
        self.form.draw()

    def form_from_mesh(self):
        pass

    def form_from_surface(self):
        pass

    def form_from_boundaries(self):
        pass

    def form_from_lines(self):
        pass

    def form_redraw(self):
        self.form.draw()

    def form_update_attributes(self):
        compas_rhino.update_settings(self.form.attributes)

    def form_update_vertex_attributes(self):
        keys = self.form.select_vertices() or list(self.form.vertices())
        self.form.update_vertex_attributes(keys)

    def form_update_edge_attributes(self):
        keys = self.form.select_edges() or list(self.form.edges())
        self.form.update_edge_attributes(keys)

    def form_update_face_attributes(self):
        keys = self.form.select_faces() or list(self.form.faces())
        self.form.update_face_attributes(keys)

    def form_move_vertex(self):
        pass

    def form_update_boundaries(self):
        # collapse short edges
        # add feet 0, 1, 2
        # close holes
        pass

    def form_show_reactions(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.draw_reactions()
        artist.redraw()

    def form_hide_reactions(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_reactions()
        artist.redraw()

    def form_show_loads(self):
        pass

    def form_hide_loads(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_loads()
        artist.redraw()

    def form_show_selfweight(self):
        pass

    def form_hide_selfweight(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_selfweight()
        artist.redraw()

    def form_show_forces(self):
        pass

    def form_hide_forces(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_forces()
        artist.redraw()

    # ==========================================================================
    # force
    # ==========================================================================

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

    def force_update_face_attributes(self):
        keys = self.force.select_faces() or list(self.force.faces())
        self.force.update_face_attributes(keys)

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
