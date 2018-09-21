from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh
from compas.utilities import geometric_key


__author__  = 'Tom Van Mele'
__email__   = 'vanmelet@ethz.ch'


__all__ = ['Diagram']


class Diagram(Mesh):

    # --------------------------------------------------------------------------
    # selections
    # --------------------------------------------------------------------------

    def get_edges_of_opening(self, key):
        edges = []
        for uv in self.face_halfedges(key):
            is_edge, is_external = self.get_edge_attributes(uv, ('is_edge', 'is_external'))
            if is_edge and not is_external:
                edges.append(uv)
        return edges

    def get_continuous_edges(self, uv, stop=None):
        a, b = uv

        ab = self.halfedge[a][b]
        ba = self.halfedge[b][a]

        if ab is None or ba is None:
            return []

        if not self.facedata[ab]['is_loaded']:
            return self.get_edges_of_opening(ab)

        if not self.facedata[ba]['is_loaded']:
            return self.get_edges_of_opening(ba)

        edges = [uv]

        end = b
        while True:
            if self.vertex_degree(a) != 4:
                break
            if a == end:
                break
            if stop is not None and a == stop:
                break 
            if self.get_vertex_attribute(a, 'is_anchor', False):
                break
            nbrs = self.vertex_neighbors(a, ordered=True)
            i = nbrs.index(b)
            b = nbrs[i - 2]
            edges.append((a, b))
            a, b = b, a

        b, a = uv
        end = b
        while True:
            if self.vertex_degree(a) != 4:
                break
            if a == end:
                break
            if stop is not None and a == stop:
                break 
            if self.get_vertex_attribute(a, 'is_anchor', False):
                break
            nbrs = self.vertex_neighbors(a, ordered=True)
            i = nbrs.index(b)
            b = nbrs[i - 2]
            edges.append((a, b))
            a, b = b, a

        edgeset = set(list(self.edges()))
        return [(u, v) if (u, v) in edgeset else (v, u) for u, v in edges]


    def get_parallel_edges(self, uv):
        edges = [uv]

        a, b = a0, b0 = uv
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
            if a in (a0, b0) and b in (a0, b0):
                break
            edges.append((a, b))

        edges[:] = edges[::-1]

        b, a = b0, a0 = uv
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
            if a in (a0, b0) and b in (a0, b0):
                break
            edges.append((a, b))

        edgeset = set(list(self.edges()))
        return [(u, v) if (u, v) in edgeset else (v, u) for u, v in edges]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
