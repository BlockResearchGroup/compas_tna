from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import zeros

from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.numerical import face_matrix


__all__ = ['LoadUpdater']


class LoadUpdater(object):
    """Class for constructing a callable for updating loads when geometry and selfweight change.

    Parameters
    ----------
    mesh : :class:`compas_tna.diagrams.FormDiagram`
        A form diagram mesh.
    p0 : ndarray (number_of_vertices x 3)
        The additional (fixed) loads at the vertices.
    thickness : ndarray (number_of_vertices x 1) or float, optional
        A thickness value per vertex.
        Or a single constant thickness value.
        Default is a constant thickness of ``1.0``.
    density : float, optional
        The density for selfweight calculations.
        Default is ``1.0``.

    Examples
    --------
    >>> import numpy
    >>> xyz = numpy.array(form.vertices_attributes('xyz'))
    >>> p = numpy.array(form.vertices_attributes(['px', 'py', 'pz']))
    >>> p0 = p.copy()

    Construct a load updater with the (additional) point loads applied at the vertices.
    Note that these additional loads are often zero.

    >>> updateloads = LoadUpdater(form, p0)

    After the geometry changes, update the loads by recomputing selfweight.

    >>> updateloads(p, xyz)
    """

    def __init__(self, mesh, p0, thickness=1.0, density=1.0, live=0.0):
        self.mesh = mesh
        self.p0 = p0
        self.thickness = thickness
        self.density = density
        self.live = live
        self.key_index = mesh.key_index()
        self.fkey_index = {fkey: index for index, fkey in enumerate(mesh.faces())}
        self.is_loaded = {fkey: mesh.face_attribute(fkey, '_is_loaded') for fkey in mesh.faces()}
        self.F = self._face_matrix()

    def __call__(self, p, xyz):
        ta = self._tributary_areas(xyz)
        sw = ta * self.thickness * self.density + ta * self.live
        p[:, 2] = self.p0[:, 2] + sw[:, 0]

    def _face_matrix(self):
        face_vertices = [None] * self.mesh.number_of_faces()
        for fkey in self.mesh.faces():
            face_vertices[self.fkey_index[fkey]] = [self.key_index[key] for key in self.mesh.face_vertices(fkey)]
        return face_matrix(face_vertices, rtype='csr', normalize=True)

    def _tributary_areas(self, xyz):
        mesh = self.mesh
        key_index = self.key_index
        fkey_index = self.fkey_index
        is_loaded = self.is_loaded
        C = self.F.dot(xyz)
        areas = zeros((xyz.shape[0], 1))
        for u in mesh.vertices():
            p0 = xyz[key_index[u]]
            a = 0
            for v in mesh.halfedge[u]:
                p1 = xyz[key_index[v]]
                p01 = p1 - p0
                fkey = mesh.halfedge[u][v]
                if fkey is not None and is_loaded[fkey]:
                    p2 = C[fkey_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p2 - p0))
                fkey = mesh.halfedge[v][u]
                if fkey is not None and is_loaded[fkey]:
                    p3 = C[fkey_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p3 - p0))
            areas[key_index[u]] = a
        return areas


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
