from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import compas
import compas_rhino

from compas_tna.diagrams import FormDiagram

from compas_tna.rhino import FormArtist

from compas_rhino.helpers.selectors import VertexSelector
from compas_rhino.helpers.selectors import EdgeSelector
from compas_rhino.helpers.selectors import FaceSelector

from compas_rhino.helpers.modifiers import VertexModifier

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['RhinoForm']


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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
