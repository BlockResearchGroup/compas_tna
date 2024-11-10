from typing import Generator
from typing import Type

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Vector
from compas.itertools import pairwise
from compas_tna.diagrams import Diagram


class FormDiagram(Diagram):
    r"""Class representing a TNA form diagram.

    Notes
    -----
    A FormDiagram has the following constructor functions

    * ``from_obj`` : Construct a diagram from the geometry described in an OBJ file.
      Only points, lines, and faces are taken into account.
    * ``from_json`` : Construct a diagram from a JSON file containing a serialised "data" dictionary.
    * ``from_lines`` : Construct a diagram from pairs of line start and end points.

    Default vertex/edge/face attributes can be "public" or "protected".
    Protected attributes are usually only for internal use
    and should only be modified by the algorithms that rely on them.
    If you do change them, do so with care...
    Protected vertex attributes are: ``_sw, _rx, _ry, _rz``.
    Protected edge attributes are: ``_h, _f, _a, _is_edge, _is_tension``.
    Protected face attributes are: ``_is_loaded``.

    The FormDiagram is a mesh.
    Since edges are implicit objects in COMPAS meshes,
    those edges that are not relevant from a TNA perspective have to be marked as ``_is_edge=False``.
    Usually, the user should not have to worry about this.
    Furthermore, changing an edge to ``_is_edge=False`` requires an equivalent change in the force diagram.
    Therefore, the attribute ``_is_edge`` is marked as "protected".

    The FormDiagram holds the information of the form diagram as well as the corresponding thrust surface.
    This means that the form diagram contains both 2D and 3D geometry and force information.
    During calculations and manipulations related to horizontal equilibrium, only the 2D information is used.
    The relationship between force density, length, axial force, horizontal force of form diagram edges
    and length of the corresponding force edges is the following:

    .. math::

        Q_{i} &= \frac{F_{i}}{L_{i, thrust}} \\
              &= \frac{H_{i}}{L_{i, form}} \\
              &= scale * \frac{L_{i, force}}{L_{i, form}}

    """

    def __init__(self, *args, name="FormDiagram", **kwargs):
        super().__init__(*args, name=name, **kwargs)

        self.dual = None

        self.default_vertex_attributes.update(
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "px": 0.0,
                "py": 0.0,
                "pz": 0.0,
                "t": 1.0,
                "is_support": False,
                "is_fixed": False,
                "_rx": 0.0,
                "_ry": 0.0,
                "_rz": 0.0,
            }
        )
        self.default_edge_attributes.update(
            {
                "q": 1.0,
                "lmin": 0.0,
                "lmax": 1e7,
                "hmin": 0.0,
                "hmax": 1e7,
                "_h": 0.0,
                "_f": 0.0,
                "_l": 0.0,
                "_a": 0.0,
                "_is_edge": True,
                "_is_tension": False,
            }
        )
        self.default_face_attributes.update({"_is_loaded": True})

    def __str__(self):
        """Compile a mesh summary of the form diagram."""
        numv = self.number_of_vertices()
        nume = len(list(self.edges_where(_is_edge=True)))
        numf = self.number_of_faces()
        vmin = self.vertex_min_degree()
        vmax = self.vertex_max_degree()
        fmin = self.face_min_degree()
        fmax = self.face_max_degree()
        return """
Form Diagram
============
name: {}
number of vertices: {}
number of (real) edges: {}
number of faces: {}
vertex degree: {}/{}
face degree: {}/{}
""".format(
            self.name, numv, nume, numf, vmin, vmax, fmin, fmax
        )

    @classmethod
    def from_lines(
        cls,
        lines: list[list[list[float]]],
        delete_boundary_face: bool = True,
        precision: int = None,
        **kwargs,
    ) -> "FormDiagram":
        """Construct a FormDiagram from a list of lines described by start and end point coordinates.

        Parameters
        ----------
        lines : list
            A list of pairs of point coordinates.
        delete_boundary_face : bool, optional
            Set ``True`` to delete the face on the outside of the boundary, ``False`` to keep it.
            Default is ``True``.
        precision: int, optional
            The precision of the geometric map that is used to connect the lines.
            If not specified, `compas.geometry.TOL.precision` will be used.

        Returns
        -------
        FormDiagram
            A FormDiagram object.

        Examples
        --------
        >>> import compas
        >>> from compas.files import OBJ
        >>> from compas_tna.diagrams import FormDiagram
        >>> obj = OBJ(compas.get("lines.obj"))
        >>> vertices = obj.parser.vertices
        >>> edges = obj.parser.lines
        >>> lines = [(vertices[u], vertices[v]) for u, v in edges]
        >>> form = FormDiagram.from_lines(lines)

        """
        graph = Graph.from_lines(lines, precision=precision)
        points = graph.to_points()
        cycles = graph.find_cycles(breakpoints=graph.leaves())
        form = cls.from_vertices_and_faces(points, cycles)
        if delete_boundary_face:
            form.delete_face(0)
        if "name" in kwargs:
            form.name = kwargs["name"]
        return form

    @classmethod
    def from_mesh(cls, mesh: Mesh) -> "FormDiagram":
        """Construct a Form Diagram from another mesh.

        Parameters
        ----------
        mesh : :class:`compas.datastructures.Mesh`
            The other mesh.

        Returns
        -------
        :class:`compas_tna.diagrams.FormDiagram`

        """
        return mesh.copy(cls=cls)

    def uv_index(self) -> dict[tuple[int, int], int]:
        """Returns a dictionary that maps edge keys (i.e. pairs of vertex keys)
        to the corresponding edge index in a list or array of edges.

        Returns
        -------
        dict
            A dictionary of uv-index pairs.

        """
        return {(u, v): index for index, (u, v) in enumerate(self.edges_where(_is_edge=True))}

    def index_uv(self) -> dict[int, tuple[int, int]]:
        """Returns a dictionary that maps edges in a list to the corresponding
        vertex key pairs.

        Returns
        -------
        dict
            A dictionary of index-uv pairs.

        """
        return dict(enumerate(self.edges_where(_is_edge=True)))

    # --------------------------------------------------------------------------
    # dual and reciprocal
    # --------------------------------------------------------------------------

    def dual_diagram(self, cls: Type[Mesh]) -> Mesh:
        """Construct the dual of the FormDiagram.

        Parameters
        ----------
        cls : Mesh
            The type of the dual.

        Returns
        -------
        Mesh
            The dual as an instance of type ``cls``.

        Notes
        -----
        Construction of the dual diagram is based on the faces around the inner, free vertices of the form diagram.
        This means not only the vertices on the boundary are ignored, but also the vertices that are supported.

        """
        dual = cls()
        fkey_centroid = {fkey: self.face_centroid(fkey) for fkey in self.faces()}
        inner = list(set(self.vertices()) - set(self.vertices_on_boundary()) - set(self.supports()))
        vertices = {}
        faces = {}
        for key in inner:
            fkeys = self.vertex_faces(key, ordered=True)
            for fkey in fkeys:
                if fkey not in vertices:
                    vertices[fkey] = fkey_centroid[fkey]
            faces[key] = fkeys
        for key, (x, y, z) in vertices.items():
            dual.add_vertex(key, x=x, y=y, z=z)
        for fkey, vertices in faces.items():
            dual.add_face(vertices, fkey=fkey)
        return dual

    # --------------------------------------------------------------------------
    # vertices
    # --------------------------------------------------------------------------

    def leaves(self) -> Generator[int, None, None]:
        """Find vertices with degree 1.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are leaves.

        """
        return self.vertices_where(vertex_degree=1)

    def corners(self) -> Generator[int, None, None]:
        """Find vertices with degree 2.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are corners.

        """
        return self.vertices_where(vertex_degree=2)

    def supports(self) -> Generator[int, None, None]:
        """Find vertices with ``is_support`` set to ``True``.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are supports.

        """
        return self.vertices_where(is_support=True)

    def fixed(self) -> Generator[int, None, None]:
        """Find vertices with ``is_fixed`` set to ``True``.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are fixed.

        """
        return self.vertices_where(is_fixed=True)

    def vertex_load(self, vertex: int) -> Vector:
        """Get the load of a vertex.

        Parameters
        ----------
        vertex : int
            The identifier of the vertex.

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
        px, py, pz = self.vertex_attributes(vertex, ["px", "py", "pz"])
        return Vector(px, py, pz)

    def vertex_selfweight(self, vertex: int) -> Vector:
        """Get the selfweight of a vertex.

        Parameters
        ----------
        vertex : int
            The identifier of the vertex.

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
        t = self.vertex_attribute(vertex, "t")
        a = self.vertex_area(vertex)
        return Vector(0, 0, -t * a)

    def vertex_reaction(self, vertex: int) -> Vector:
        """Get the reaction force at a vertex.

        Parameters
        ----------
        vertex : int
            The identifier of the vertex.

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
        rx, ry, rz = self.vertex_attributes(vertex, ["rx", "ry", "rz"])
        return Vector(-rx, -ry, -rz)

    def vertex_residual(self, vertex: int) -> Vector:
        """Get the residual force at a vertex.

        Parameters
        ----------
        vertex : int
            The identifier of the vertex.

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
        rx, ry, rz = self.vertex_attributes(vertex, ["rx", "ry", "rz"])
        return Vector(rx, ry, rz)

    # --------------------------------------------------------------------------
    # boundary conditions
    # --------------------------------------------------------------------------

    def update_boundaries(self):
        """Update the boundaries to add outside faces."""
        # reset edges: set all edges _is_edge=True
        self.edges_attribute(name="_is_edge", value=True)
        # reset faces: delete all faces where _is_loaded=False
        for face in list(self.faces_where(_is_loaded=False)):
            if self.has_face(face):
                self.delete_face(face)
        self.remove_unused_vertices()
        # mark all "supported edges" as '_is_edge=False'
        # they will be ignored in any futher steps
        # this is what indierectly creates isolated vertices
        # and for example the corner cutoffs in orthogonal grids
        for edge in self.edges():
            if all(self.vertices_attribute("is_support", keys=edge)):
                if self.is_edge_on_boundary(edge):
                    self.edge_attribute(edge, "_is_edge", False)
        # delete isolated (corner) vertices
        # technically this can happen for vertices with degree of any kind
        for vertex in list(self.vertices_where(vertex_degree=2)):
            nbrs = self.vertex_neighbors(vertex)
            if all(not self.edge_attribute((vertex, nbr), "_is_edge") for nbr in nbrs):
                for nbr in nbrs:
                    face = self.halfedge[vertex][nbr]
                    if face is not None:
                        break
                vertices = self.face_vertices(face)
                after = nbr
                before = vertices[vertices.index(after) - 2]
                self.split_face(face, before, after)
                self.edge_attribute((before, after), "_is_edge", False)
                self.delete_vertex(vertex)
        # boundaries
        for boundary in self.vertices_on_boundaries():
            supports = [vertex for vertex in boundary if self.vertex_attribute(vertex, "is_support")]
            if len(supports) == 0:
                # if the boundary contains no supports
                # only an additional face has to be added
                # this tends to only be the case with openings/holes
                vertices = boundary
                self.add_face(vertices, _is_loaded=False)
            elif len(supports) == 1:
                # if the boundary has exactly 1 support
                # the boundary just has to be cut at the support and pasted back together
                # and then a face has to be added
                i = boundary.index(supports[0])
                vertices = boundary[i:] + boundary[:i]
                self.add_face(vertices, _is_loaded=False)
            else:
                # if the boundary has more than 1 support
                # split the boundary into segments between the supports
                # and add a boundary face for every segment
                segments = []
                for start, end in pairwise(supports + supports[:1]):
                    i = boundary.index(start)
                    j = boundary.index(end)
                    if i < j:
                        segment = boundary[i : j + 1]  # noqa: E203
                    elif i > j:
                        segment = boundary[i:] + boundary[: j + 1]
                    else:
                        continue
                    segments.append(segment)
                # add outer faces
                for vertices in segments:
                    if len(vertices) < 3:
                        continue
                    self.add_face(vertices, _is_loaded=False)
                    self.edge_attribute((vertices[0], vertices[-1]), "_is_edge", False)
