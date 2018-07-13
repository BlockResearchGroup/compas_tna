from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import compas
import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import FormArtist
from compas_tna.rhino import ForceArtist

from compas_rhino.helpers.selectors import VertexSelector
from compas_rhino.helpers.selectors import EdgeSelector
from compas_rhino.helpers.selectors import FaceSelector

from compas_rhino.helpers.modifiers import VertexModifier
from compas_rhino.helpers.modifiers import EdgeModifier
from compas_rhino.helpers.modifiers import FaceModifier

from compas_tna.equilibrium import horizontal_rhino as horizontal
from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical_from_zmax
from compas_tna.equilibrium import vertical_from_formforce_rhino as vertical_from_formforce

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


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

    @classmethod
    def from_mesh(cls, guid):
        return compas_rhino.mesh_from_guid(cls, guid)

    @classmethod
    def from_surface(cls, guid):
        return compas_rhino.mesh_from_surface_uv(cls, guid)

    def draw(self):
        artist = FormArtist(self, layer=self.attributes['layer'])
        artist.clear_layer()
        artist.draw_vertices(
            keys=list(self.vertices_where({'is_external': False})),
            color={key: '#ff0000' for key in self.vertices_where({'is_anchor': True})}
        )
        artist.draw_edges(
            keys=list(self.edges_where({'is_edge': True, 'is_external': False}))
        )
        artist.draw_faces(
            fkeys=list(self.faces_where({'is_loaded': True})),
            join_faces=True
        )
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

    def match_vertices(self, keys):
        temp = compas_rhino.get_objects(name="{}.vertex.*".format(self.name))
        names = compas_rhino.get_object_names(temp)

        guids = []
        for guid, name in zip(temp, names):
            parts = name.split('.')
            key = literal_eval(parts[2])
            if key in keys:
                guids.append(guid)

        return guids

    def match_edges(self, keys):
        temp = compas_rhino.get_objects(name="{}.edge.*".format(self.name))
        names = compas_rhino.get_object_names(temp)

        guids = []
        for guid, name in zip(temp, names):
            parts = name.split('.')[2].split('-')
            u = literal_eval(parts[0])
            v = literal_eval(parts[1])
            if (u, v) in keys or (v, u) in keys:
                guids.append(guid)

        return guids

    def match_faces(self, keys):
        temp = compas_rhino.get_objects(name="{}.face.*".format(self.name))
        names = compas_rhino.get_object_names(temp)

        guids = []
        for guid, name in zip(temp, names):
            parts = name.split('.')
            key = literal_eval(parts[2])
            if key in keys:
                guids.append(guid)

        return guids

    def highlight_vertices(self, keys):
        guids = self.match_vertices(keys)

        rs.EnableRedraw(False)
        rs.SelectObjects(guids)
        rs.EnableRedraw(True)

    def highlight_edges(self, keys):
        guids = self.match_edges(keys)

        rs.EnableRedraw(False)
        rs.SelectObjects(guids)
        rs.EnableRedraw(True)

    def highlight_faces(self, keys):
        guids = self.match_faces(keys)

        rs.EnableRedraw(False)
        rs.SelectObjects(guids)
        rs.EnableRedraw(True)

    def get_parallel_edges(self, uv):
        edges = [uv]

        a, b = uv
        while True:
            f = self.halfedge[a][b]
            if f is None:
                break
            vertices = self.face_vertices(f)
            if len(vertices) != 4:
                break
            i = vertices.index(a)
            a = vertices[i - 1]
            b = vertices[i - 2]
            edges.append((a, b))

        edges[:] = edges[::-1]

        b, a = uv
        while True:
            f = self.halfedge[a][b]
            if f is None:
                break
            vertices = self.face_vertices(f)
            if len(vertices) != 4:
                break
            i = vertices.index(a)
            a = vertices[i - 1]
            b = vertices[i - 2]
            edges.append((a, b))

        edgeset = set(list(self.edges()))

        return [(u, v) if (u, v) in edgeset else (v, u) for u, v in edges]

    def get_continuous_edges(self, uv):
        edges = [uv]

        a, b = uv
        while True:
            if self.vertex_degree(a) != 4:
                break
            nbrs = self.vertex_neighbours(a, ordered=True)
            i = nbrs.index(b)
            b = nbrs[i - 2]
            edges.append((a, b))
            a, b = b, a

        b, a = uv
        while True:
            if self.vertex_degree(a) != 4:
                break
            nbrs = self.vertex_neighbours(a, ordered=True)
            i = nbrs.index(b)
            b = nbrs[i - 2]
            edges.append((a, b))
            a, b = b, a

        edgeset = set(list(self.edges()))

        return [(u, v) if (u, v) in edgeset else (v, u) for u, v in edges]


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


class TNAFrontController(object):

    instancename = 'tna'

    def __init__(self):
        self.settings = {
            'forward.vertical.zmax' : None,

        }
        self.form = None
        self.force = None

    def init(self):
        pass

    def update_settings(self):
        compas_rhino.update_settings(self.settings)

    # ==========================================================================
    # forward
    # ==========================================================================

    def forward_update_settings(self):
        settings = {key: value for key, value in self.settings.items() if key.startswith('forward')}
        compas_rhino.update_settings(settings)
        self.settings.update(settings)

    def forward_horizontal(self):
        horizontal(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def forward_vertical_zmax(self):
        vertical_from_zmax(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def forward_vertical_formforce(self):
        vertical_from_formforce(self.form, self.force)
        self.form.draw()
        self.force.draw()

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
        guid = compas_rhino.select_mesh()
        if not guid:
            return
        self.form = RhinoForm.from_mesh(guid)
        self.form.draw()

    def form_from_surface(self):
        guid = compas_rhino.select_surface()
        if not guid:
            return
        self.form = RhinoForm.from_surface(guid)
        self.form.draw()

    def form_from_boundaries(self):
        pass

    def form_from_lines(self):
        guids = compas_rhino.select_lines()
        if not guids:
            return
        lines = compas_rhino.get_line_coordinates(guids)
        self.form = RhinoForm.from_lines(lines)
        self.form.draw()

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

    def form_relax(self):
        keys = self.form.select_vertices()
        self.form.relax(keys)
        self.form.draw()

    def form_update_boundaries(self):
        boundaries = self.form.vertices_on_boundaries()
        exterior = boundaries[0]
        interior = boundaries[1:]
        self.form.update_exterior(exterior, feet=1)
        self.form.update_interior(interior)

    def form_show_reactions(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.draw_reactions()
        artist.redraw()

    def form_hide_reactions(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_reactions()
        artist.redraw()

    def form_show_residuals(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.draw_residuals()
        artist.redraw()

    def form_hide_residuals(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_residuals()
        artist.redraw()

    def form_show_loads(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.draw_loads()
        artist.redraw()

    def form_hide_loads(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_loads()
        artist.redraw()

    def form_show_selfweight(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.draw_selfweight()
        artist.redraw()

    def form_hide_selfweight(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_selfweight()
        artist.redraw()

    def form_show_forces(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.draw_forces()
        artist.redraw()

    def form_hide_forces(self):
        artist = FormArtist(self.form, layer=self.form.attributes['layer'])
        artist.clear_forces()
        artist.redraw()

    def form_select_parallel_edges(self):
        uv = self.form.select_edge()
        if not uv:
            return

        keys = self.form.get_parallel_edges(uv)
        self.form.highlight_edges(keys)

    def form_select_continuous_edges(self):
        uv = self.form.select_edge()
        if not uv:
            return

        keys = self.form.get_continuous_edges(uv)
        self.form.highlight_edges(keys)

    def form_select_boundary_vertices(self):
        keys = set(self.form.vertices_on_boundary())
        self.form.highlight_vertices(keys)

    def form_select_boundary_edges(self):
        keys = set(self.form.edges_on_boundary())
        self.form.highlight_edges(keys)

    def form_select_boundary_faces(self):
        keys = set(self.form.faces_on_boundary())
        self.form.highlight_faces(keys)

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
