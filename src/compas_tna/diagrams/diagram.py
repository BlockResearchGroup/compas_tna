from compas.datastructures import Mesh
from compas.geometry import angle_vectors


class Diagram(Mesh):
    """Base diagram implementing attributes shared between the form and force diagram."""

    def corner_vertices(self, tol=160):
        """Identify the corner vertices.

        Parameters
        ----------
        tol : float, optional
            The threshold value for the angle formed between two edges at a vertex
            for it to be considered a corner.
            Vertices with smaller angles are considered a corner.

        Returns
        -------
        list[int]

        """
        vkeys = []
        for key in self.vertices_on_boundary():
            if self.vertex_degree(key) == 2:
                vkeys.append(key)
            else:
                nbrs = []
                for nkey in self.vertex_neighbors(key):
                    if self.is_edge_on_boundary((key, nkey)):
                        nbrs.append(nkey)
                u = self.edge_vector((key, nbrs[0]))
                v = self.edge_vector((key, nbrs[1]))
                if angle_vectors(u, v, deg=True) < tol:
                    vkeys.append(key)
        return vkeys
