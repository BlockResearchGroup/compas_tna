from typing import Annotated
from typing import Literal

import numpy
import numpy.typing as npt
import scipy.sparse

from compas.datastructures import Mesh
from compas.geometry import cross_vectors
from compas.geometry import length_vector
from compas.matrices import face_matrix


class LoadUpdater:
    """Class for constructing a callable for updating loads when geometry and selfweight change.

    Parameters
    ----------
    mesh : :class:`Mesh`
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
    >>> xyz = numpy.array(form.vertices_attributes("xyz"))
    >>> p = numpy.array(form.vertices_attributes(["px", "py", "pz"]))
    >>> p0 = p.copy()

    Construct a load updater with the (additional) point loads applied at the vertices.
    Note that these additional loads are often zero.

    >>> updateloads = LoadUpdater(form, p0)

    After the geometry changes, update the loads by recomputing selfweight.

    >>> updateloads(p, xyz)

    """

    def __init__(
        self,
        mesh: Mesh,
        p0: Annotated[npt.NDArray[numpy.float64], Literal["*, 3"]],
        thickness: float = 1.0,
        density: float = 1.0,
        live: float = 0.0,
    ):
        self.mesh = mesh
        self.p0 = p0
        self.thickness = thickness
        self.density = density
        self.live = live
        self.vertex_index = mesh.vertex_index()
        self.fvertex_index = {face: index for index, face in enumerate(mesh.faces())}
        self.is_loaded = {face: mesh.face_attribute(face, "_is_loaded") for face in mesh.faces()}
        self.F = self.face_matrix()

    def __call__(
        self,
        p: Annotated[npt.NDArray[numpy.float64], Literal["*, 3"]],
        xyz: Annotated[npt.NDArray[numpy.float64], Literal["*, 3"]],
    ) -> None:
        """Update the vertex loads using the current vertex coordinates.

        Returns
        -------
        None
            The loads are updated in place.

        """
        ta = self.tributary_areas(xyz)
        sw = ta * self.thickness * self.density + ta * self.live
        p[:, 2] = self.p0[:, 2] + sw[:, 0]

    def face_matrix(self) -> scipy.sparse.csr_matrix:
        """Compute the face matrix of the mesh.

        The face matrix can be used to efficiently compute the centroid of each face.

        Returns
        -------
        scipy.sparse.csr_matrix

        """
        face_vertices = [None] * self.mesh.number_of_faces()
        for fkey in self.mesh.faces():
            face_vertices[self.fvertex_index[fkey]] = [self.vertex_index[key] for key in self.mesh.face_vertices(fkey)]
        return face_matrix(face_vertices, rtype="csr", normalize=True)

    def tributary_areas(
        self,
        xyz: Annotated[npt.NDArray[numpy.float64], Literal["*, 3"]],
    ) -> Annotated[npt.NDArray[numpy.float64], Literal["*, 1"]]:
        """Compute the tributary area per vertex.

        Parameters
        ----------
        xyz : ndarray (number_of_vertices x 3)
            The current vertex coordinates.

        Returns
        -------
        ndarray (number_of_vertices x 1)

        """
        mesh = self.mesh
        vertex_index = self.vertex_index
        fvertex_index = self.fvertex_index
        is_loaded = self.is_loaded
        C = self.F.dot(xyz)
        areas = numpy.zeros((xyz.shape[0], 1))
        for u in mesh.vertices():
            p0 = xyz[vertex_index[u]]
            a = 0
            for v in mesh.halfedge[u]:
                p1 = xyz[vertex_index[v]]
                p01 = p1 - p0
                fkey = mesh.halfedge[u][v]
                if fkey is not None and is_loaded[fkey]:
                    p2 = C[fvertex_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p2 - p0))
                fkey = mesh.halfedge[v][u]
                if fkey is not None and is_loaded[fkey]:
                    p3 = C[fvertex_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p3 - p0))
            areas[vertex_index[u]] = a
        return areas
