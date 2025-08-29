from compas.datastructures import Mesh
from compas.geometry import angle_vectors


class Diagram(Mesh):
    """Base diagram implementing attributes shared between the form and force diagram."""

    def corner_vertices(self, tol=160):
        """Identify the corner vertices on the boundary.

        Parameters
        ----------
        tol : float, optional
            The threshold value for the angle in degrees formed between two edges
            at a vertex on the boundary for it to be considered a corner.
            Vertices with smaller angles than the threshold are considered a corner.

        Returns
        -------
        vertices : list[int]
            The list of vertices filtered as corners.

        """
        vertices = []
        for vertex in self.vertices_on_boundary():
            if self.vertex_degree(vertex) == 2:
                vertices.append(vertex)
            else:
                nbrs = []
                for nbr in self.vertex_neighbors(vertex):
                    if self.is_edge_on_boundary((vertex, nbr)):
                        nbrs.append(nbr)
                u = self.edge_vector((vertex, nbrs[0]))
                v = self.edge_vector((vertex, nbrs[1]))
                if angle_vectors(u, v, deg=True) < tol:
                    vertices.append(vertex)
        return vertices
