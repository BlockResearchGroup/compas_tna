from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import network_find_cycles
from compas.datastructures import Network
from compas.utilities import pairwise

from compas_tna.diagrams import Diagram


__all__ = ['FormDiagram']


class FormDiagram(Diagram):
    r"""The ``FormDiagram`` defines a TNA form diagram.

    Notes
    -----
    A ``FormDiagram`` has the following constructor functions

    *   ``from_obj`` : Construct a diagram from the geometry described in an OBJ file. Only points, lines, and faces are taken into account.
    *   ``from_json`` : Construct a diagram from a JSON file containing a serialised "data" dictionary.
    *   ``from_lines`` : Construct a diagram from pairs of line start and end points.
    *   ``from_mesh`` : Construct a diagram from a Mesh.
    *   ``from_rhinomesh`` : Construct a diagram from a Rhino mesh.
    *   ``from_rhinosurface`` : Construct a diagram from a Rhino surface, using the U and V isolines.
    *   ``from_rhinolines`` : Construct a diagram from a selection of Rhino lines (i.e. curves of degree 1).

    Default vertex/edge/face attributes can be "public" or "protected".
    Protected attributes are usually only for internal use and should only be modified by the algorithms that rely on them.
    If you do change them, do so with care...
    Protected vertex attributes are: ``_sw, _rx, _ry, _rz``.
    Protected edge attributes are: ``_h, _f, _a, _is_edge, _is_tension``.
    Protected face attributes are: ``_is_loaded``.

    The ``FormDiagram`` is a mesh.
    Since edges are implicit objects in COMPAS meshes, those edges that are not relevant from a TNA perspective have to be marked as ``_is_edge=False``.
    Usually, the user should not have to worry about this.
    Furthermore, changing an edge to ``_is_edge=False`` requires an equivalent change in the force diagram.
    Therefore, the attribute ``_is_edge`` is marked as "protected".

    The ``FormDiagram`` holds the information of the form diagram as well as the corresponding thrust surface.
    This means that the form diagram contains both 2D and 3D geometry and force information.
    During calculations and manipulations related to horizontal equilibrium, only the 2D information is used.
    The relationship between force density, length, axial force, horizontal force of form diagram edges
    and length of the corresponding force edges is the following:

    .. math::

        Q_{i} &= \frac{F_{i}}{L_{i, thrust}} \\
              &= \frac{H_{i}}{L_{i, form}} \\
              &= scale * \frac{L_{i, force}}{L_{i, form}}

    """

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.dual = None
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'px': 0.0,
            'py': 0.0,
            'pz': 0.0,
            't': 1.0,
            'is_anchor': False,
            'is_fixed': False,

            '_rx': 0.0,
            '_ry': 0.0,
            '_rz': 0.0,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            'lmin': 0.0,
            'lmax': 1e+7,
            'hmin': 0.0,
            'hmax': 1e+7,

            '_h': 0.0,
            '_f': 0.0,
            '_l': 0.0,
            '_a': 0.0,

            '_is_edge': True,
            '_is_tension': False
        })
        self.default_face_attributes.update({
            '_is_loaded': True
        })
        self.attributes.update({
            'name': 'FormDiagram',
        })

    def __str__(self):
        """Compile a mesh summary of the form diagram."""
        numv = self.number_of_vertices()
        nume = len(list(self.edges_where({'_is_edge': True})))
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
""".format(self.name, numv, nume, numf, vmin, vmax, fmin, fmax)

    @classmethod
    def from_lines(cls, lines, delete_boundary_face=True, precision=None, **kwargs):
        """Construct a FormDiagram from a list of lines described by start and end point coordinates.

        Parameters
        ----------
        lines : list
            A list of pairs of point coordinates.
        delete_boundary_face : bool, optional
            Set ``True`` to delete the face on the outside of the boundary, ``False`` to keep it.
            Default is ``True``.
        precision: str, optional
            The precision of the geometric map that is used to connect the lines.
            If not specified, the global precision stored in ``compas.PRECISION`` will be used.

        Returns
        -------
        FormDiagram
            A FormDiagram object.

        Examples
        --------
        >>> import compas
        >>> from compas.files import OBJ
        >>> from compas_tna.diagrams import FormDiagram
        >>> obj = OBJ(compas.get('lines.obj'))
        >>> vertices = obj.parser.vertices
        >>> edges = obj.parser.lines
        >>> lines = [(vertices[u], vertices[v]) for u, v in edges]
        >>> form = FormDiagram.from_lines(lines)
        """
        network = Network.from_lines(lines, precision=precision)
        points = network.to_points()
        cycles = network_find_cycles(network, breakpoints=network.leaves())
        form = cls.from_vertices_and_faces(points, cycles)
        if delete_boundary_face:
            form.delete_face(0)
        if 'name' in kwargs:
            form.name = kwargs['name']
        return form

    @classmethod
    def from_mesh(cls, mesh, **kwargs):
        """Construct a FormDiagram from a Mesh.

        Parameters
        ----------
        mesh : compas.datastructures.Mesh
            The mesh to be taken as reference.
            The keys of the faces and vertices of the base mesh will be kept.
            Only the XY coordinates per vertex are stored. Z = 0.0

        Returns
        -------
        FormDiagram
            A FormDiagram object.

        Examples
        --------
        >>> import compas
        >>> from compas.datastructures import Mesh
        >>> from compas_tna.diagrams import FormDiagram

        >>> mesh = Mesh.from_obj(compas.get('faces.obj'))
        >>> form = FormDiagram.from_mesh(mesh)
        >>> form.plot()
        """
        form = cls()
        for vkey, attr in mesh.vertices(True):
            form.add_vertex(key=vkey, x=attr['x'], y=attr['y'], z=0.0)
        for fkey in mesh.faces():
            form.add_face(vertices=mesh.face_vertices(fkey), fkey=fkey)
        if 'name' in kwargs:
            mesh.name = kwargs['name']
        return form

    @classmethod
    def from_rhinomesh(cls, guid, **kwargs):
        """Construct a FormDiagram from a Rhino mesh represented by a guid.

        Parameters
        ----------
        guid : str
            A globally unique identifier.

        Returns
        -------
        FormDiagram
            A FormDiagram object.

        Examples
        --------
        .. code-block:: python

            import compas_rhino
            from compas_tna.diagrams import FormDiagram

            guid = compas_rhino.select_mesh()
            form = FormDiagram.from_rhinomesh(guid)

        """
        from compas_rhino.geometry import RhinoMesh
        mesh = RhinoMesh.from_guid(guid).to_compas(cls)
        if 'name' in kwargs:
            mesh.name = kwargs['name']
        return mesh

    @classmethod
    def from_rhinosurface(cls, guid, **kwargs):
        """Construct a FormDiagram from a Rhino surface represented by its GUID.

        Parameters
        ----------
        guid : str
            A globally unique identifier.

        Returns
        -------
        FormDiagram
            A FormDiagram object.

        Examples
        --------
        .. code-block:: python

            import compas_rhino
            from compas_tna.diagrams import FormDiagram

            guid = compas_rhino.select_surface()
            form = FormDiagram.from_rhinosurface(guid)

        """
        from compas_rhino.geometry import RhinoSurface
        mesh = RhinoSurface.from_guid(guid).uv_to_compas(cls, **kwargs)
        if 'name' in kwargs:
            mesh.name = kwargs['name']
        return mesh

    @classmethod
    def from_rhinolines(cls, guids, delete_boundary_face=True, precision=None, **kwargs):
        """Construct a FormDiagram from a set of Rhino lines represented by their GUIDs.

        Parameters
        ----------
        guids : list
            A list of GUIDs.
        delete_boundary_face : bool, optional
            Set ``True`` to delete the face on the outside of the boundary, ``False`` to keep it.
            Default is ``True``.
        precision: str, optional
            The precision of the geometric map that is used to connect the lines.
            If not specified, the global precision stored in ``compas.PRECISION`` will be used.

        Returns
        -------
        FormDiagram
            A FormDiagram object.

        Examples
        --------
        .. code-block:: python

            import compas_rhino
            from compas_tna.diagrams import FormDiagram

            guids = compas_rhino.select_lines()
            form = FormDiagram.from_rhinolines(guids)

        """
        import compas_rhino
        lines = compas_rhino.get_line_coordinates(guids)
        mesh = FormDiagram.from_lines(lines, delete_boundary_face=delete_boundary_face, precision=precision, **kwargs)
        return mesh

    def uv_index(self):
        """Returns a dictionary that maps edge keys (i.e. pairs of vertex keys)
        to the corresponding edge index in a list or array of edges.

        Returns
        -------
        dict
            A dictionary of uv-index pairs.
        """
        return {(u, v): index for index, (u, v) in enumerate(self.edges_where({'_is_edge': True}))}

    def index_uv(self):
        """Returns a dictionary that maps edges in a list to the corresponding
        vertex key pairs.

        Returns
        -------
        dict
            A dictionary of index-uv pairs.
        """
        return dict(enumerate(self.edges_where({'_is_edge': True})))

    # --------------------------------------------------------------------------
    # dual and reciprocal
    # --------------------------------------------------------------------------

    def dual_diagram(self, cls):
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
        This means not only the vertices on the boundary are ignored, but also the vertices that are anchored.

        """
        dual = cls()
        fkey_centroid = {fkey: self.face_centroid(fkey) for fkey in self.faces()}
        inner = list(set(self.vertices()) - set(self.vertices_on_boundary()) - set(self.anchors()))
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

    def leaves(self):
        """Vertices with degree 1.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are leaves.
        """
        return self.vertices_where({'vertex_degree': 1})

    def corners(self):
        """Vertices with degree 2.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are corners.
        """
        return self.vertices_where({'vertex_degree': 2})

    def anchors(self):
        """Vertices with ``is_anchor`` set to ``True``.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are anchors.
        """
        return self.vertices_where({'is_anchor': True})

    def fixed(self):
        """Vertices with ``is_fixed`` set to ``True``.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are fixed.
        """
        return self.vertices_where({'is_fixed': True})

    # def residual(self):
    #     R = 0
    #     for vertex in self.vertices_where({'is_anchor': False, 'is_fixed': False}):
    #         rx, ry, rz = self.vertex_attributes(vertex, ['_rx', '_ry', '_rz'])
    #         R += rx ** 2 + ry ** 2 + rz ** 2
    #     return sqrt(R)

    # --------------------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # postprocess
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # boundary conditions
    # --------------------------------------------------------------------------

    def update_boundaries(self):
        """Update the boundaries to add outside faces."""
        # mark all "anchored edges" as '_is_edge=False'
        # they will be ignored in any futher steps
        # this is what indierectly creates isolated vertices
        # and vor example the corner cutoffs in orthogonal grids
        for edge in self.edges():
            if all(self.vertices_attribute('is_anchor', keys=edge)):
                if self.is_edge_on_boundary(*edge):
                    self.edge_attribute(edge, '_is_edge', False)
        # delete isolated (corner) vertices
        # technically this can happen for vertices with degree of any kind
        for vertex in list(self.vertices_where({'vertex_degree': 2})):
            nbrs = self.vertex_neighbors(vertex)
            if all(not self.edge_attribute((vertex, nbr), '_is_edge') for nbr in nbrs):
                for nbr in nbrs:
                    face = self.halfedge[vertex][nbr]
                    if face is not None:
                        break
                vertices = self.face_vertices(face)
                after = nbr
                before = vertices[vertices.index(after) - 2]
                self.split_face(face, before, after)
                self.edge_attribute((before, after), '_is_edge', False)
                self.delete_vertex(vertex)
        # boundaries
        for boundary in self.vertices_on_boundaries():
            anchors = [vertex for vertex in boundary if self.vertex_attribute(vertex, 'is_anchor')]
            if len(anchors) == 0:
                # if the boundary contains no anchors
                # only an additional face has to be added
                # this tends to only be the case with openings/holes
                vertices = boundary
                self.add_face(vertices, _is_loaded=False)
            elif len(anchors) == 1:
                # if the boundary has exactly 1 anchor
                # the boundary just has to be cut at the anchor and pasted back together
                # and then a face has to be added
                i = boundary.index(anchors[0])
                vertices = boundary[i:] + boundary[:i]
                self.add_face(vertices, _is_loaded=False)
            else:
                # if the boundary has more than 1 anchor
                # split the boundary into segments between the anchors
                # and add a boundary face for every segment
                segments = []
                for start, end in pairwise(anchors + anchors[:1]):
                    i = boundary.index(start)
                    j = boundary.index(end)
                    if i < j:
                        segment = boundary[i:j + 1]
                    elif i > j:
                        segment = boundary[i:] + boundary[:j + 1]
                    else:
                        continue
                    segments.append(segment)
                # add outer faces
                for vertices in segments:
                    if len(vertices) < 3:
                        continue
                    self.add_face(vertices, _is_loaded=False)
                    self.edge_attribute((vertices[0], vertices[-1]), '_is_edge', False)

    # --------------------------------------------------------------------------
    # visualisation
    # --------------------------------------------------------------------------

    def plot(self):
        """Plot a form diagram with a plotter with all the default settings."""
        from compas_plotters import MeshPlotter
        plotter = MeshPlotter(self, figsize=(12, 8), tight=True)
        vertexcolor = {}
        vertexcolor.update({key: '#00ff00' for key in self.vertices_where({'is_fixed': True})})
        vertexcolor.update({key: '#ff0000' for key in self.vertices_where({'is_anchor': True})})
        plotter.draw_vertices(facecolor=vertexcolor)
        plotter.draw_edges(keys=list(self.edges_where({'_is_edge': True})))
        plotter.draw_faces(keys=list(self.faces_where({'_is_loaded': True})))
        plotter.show()

    def draw(self, layer=None, clear_layer=True, settings=None):
        """Draw the form diagram in Rhino.

        Parameters
        ----------
        layer : str, optional
            The layer in which the drawing should be contained.
        clear_layer : bool, optional
            Clear the layer if ``True``.
            Default is ``True``.
        settings : dict, optional
            A dictionary of settings overwriting the default settings of the artist.
        """
        from compas_tna.rhino import FormArtist
        artist = FormArtist(self, layer=layer, settings=settings)
        if clear_layer:
            artist.clear_layer()
        artist.draw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
