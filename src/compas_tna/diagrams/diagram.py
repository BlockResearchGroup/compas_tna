from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh


__all__ = ['Diagram']


class Diagram(Mesh):
    """Base diagram implementing attributes shared between the form and force diagram."""

    __module__ = 'compas_tna.diagrams'

    # --------------------------------------------------------------------------
    # selections
    # --------------------------------------------------------------------------

    def get_edges_of_opening(self, key):
        """Get all the edges of an opening in the diagram.

        Parameters
        ----------
        key : hashable
            The identifier of the face forming the opening.

        Returns
        -------
        list
            The edges on the perimeter of the opening.

        """
        edges = []
        for uv in self.face_halfedges(key):
            is_edge, is_external = self.get_edge_attributes(uv, ('is_edge', 'is_external'))
            if is_edge and not is_external:
                edges.append(uv)
        return edges

    def get_continuous_edges(self, uv, stop=None):
        """Get all edges forming a continuous line with a given edge.

        Parameters
        ----------
        uv : tuple
            The pair of vertex keys identifying the base edge of the continuous line.
        stop : vertex identifier (None)
            The identifier of a vertex that marks the end of the line.
            If no stop is provided, the line continuous until hits the boundary of the diagram.

        Returns
        -------
        list
            The pairs of vertex keys identifying the edges forming the line.

        Notes
        -----
        This function only makes sense in a quad-dominant mesh.

        Given an edge, the connected edges forming a 'continuous line' with that edge
        can only be identified in a meaningful way if the vertices if the given edge
        have degree four.

        Therefore, in addition to reaching the boundary of the diagram, the end
        of the line is reached if a vertex is encountered with a vertex degree
        other than four.

        """
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
        """Get all edges forming a parallel strip with a given edge.

        Parameters
        ----------
        uv : tuple
            Pair of vertex identifiers identifying the edge.

        Returns
        -------
        list
            The pairs of vertex identifiers of the edges forming the parallel strip.

        Notes
        -----
        This function only makes sense in a quad-dominant mesh.

        Given a starting edge, the edges forming a parallel strip with that edge
        are identified as the opposite edges in the adjacent faces of the given edge.

        Therefore, the strip stops if a face with degree other than four is encountered.

        """
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
