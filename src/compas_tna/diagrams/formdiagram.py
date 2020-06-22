from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sin
from math import cos
from math import sqrt

import compas

from compas.geometry import add_vectors_xy
from compas.geometry import subtract_vectors_xy
from compas.geometry import normalize_vector_xy
from compas.geometry import angle_vectors_xy
from compas.geometry import cross_vectors
from compas.geometry import scale_vector

from compas.datastructures import network_find_cycles
from compas.datastructures import Network

from compas_tna.diagrams import Diagram


__all__ = ['FormDiagram']


def rotate(point, angle):
    x = cos(angle) * point[0] - sin(angle) * point[1]
    y = sin(angle) * point[0] + cos(angle) * point[1]
    return x, y, 0


def cross_z(ab, ac):
    return ab[0] * ac[1] - ab[1] * ac[0]


class FormDiagram(Diagram):
    """The ``FormDiagram`` extends the base ``Diagram`` with attributes and methods relevant for a form diagram in TNA.

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

    """

    __module__ = 'compas_tna.diagrams'

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

            '_sw': 0.0,
            '_rx': 0.0,
            '_ry': 0.0,
            '_rz': 0.0,
            '_is_external': False,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            'qmin': 0.0,
            'qmax': 1e+7,
            'lmin': 0.0,
            'lmax': 1e+7,
            'fmin': 0.0,
            'fmax': 1e+7,

            '_f': 0.0,
            '_l': 0.0,
            '_a': 0.0,
            '_is_edge': True,
            '_is_external': False,
            '_is_tension': False
        })
        self.default_face_attributes.update({
            '_is_loaded': True
        })
        self.attributes.update({
            'name': 'FormDiagram',
            'feet.scale': 1.0,
            'feet.alpha': 45,
            'feet.tol': 0.1,
        })

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

        """
        dual = cls()
        fkey_centroid = {fkey: self.face_centroid(fkey) for fkey in self.faces()}
        outer = self.vertices_on_boundary()
        inner = list(set(self.vertices()) - set(outer))
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
        iterator
            An iterator of vertex keys.
        """
        return self.vertices_where({'vertex_degree': 1})

    def corners(self):
        """Vertices with degree 2.

        Returns
        -------
        iterator
            An iterator of vertex keys.
        """
        return self.vertices_where({'vertex_degree': 2})

    def anchors(self):
        """Vertices with ``is_anchor`` set to ``True``.

        Returns
        -------
        iterator
            An iterator of vertex keys.
        """
        return self.vertices_where({'is_anchor': True})

    def fixed(self):
        """Vertices with ``is_fixed`` set to ``True``.

        Returns
        -------
        iterator
            An iterator of vertex keys.
        """
        return self.vertices_where({'is_fixed': True})

    def residual(self):
        R = 0
        for key, attr in self.vertices_where({'is_anchor': False, 'is_fixed': False}, True):
            rx, ry, rz = attr['_rx'], attr['_ry'], attr['_rz']
            R += rx ** 2 + ry ** 2 + rz ** 2
        return sqrt(R)

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
        """"""
        scale = self.attributes['feet.scale']
        alpha = pi * 45 / 180
        tol = self.attributes['feet.tol']
        # mark all "anchored edges" as '_is_edge=False'
        for edge in self.edges():
            self.edge_attribute(edge, '_is_edge', not all(self.vertices_attribute('is_anchor', keys=edge)))
        # outer boundary
        # note: how to make sure this is the "outer" boundary
        boundaries = self.vertices_on_boundaries()
        exterior = boundaries[0]
        # split outer boundary
        # where `is_anchor=True`
        # into (ordered) series of boundary edges
        segment = []
        segments = [segment]
        for vertex in exterior:
            segment.append(vertex)
            if self.vertex_attribute(vertex, 'is_anchor'):
                segment = [vertex]
                segments.append(segment)
        segments[-1] += segments[0]
        del segments[0]
        # add new vertices
        # where number of `_is_edge=True` connected edges at begin/end vertices of a segment is greater than 1
        key_foot = {}
        key_xyz = {key: self.vertex_coordinates(key, 'xyz') for key in self.vertices()}
        for i, vertices in enumerate(segments):
            key = vertices[0]
            nbrs = self.vertex_neighbors(key)
            # check necessary condition for feet
            count = 0
            for nbr in nbrs:
                edge = key, nbr
                if self.edge_attribute(edge, '_is_edge'):
                    count += 1
            # only add feet if necessary
            if count > 1:
                after = vertices[1]
                before = segments[i - 1][-2]
                # base point
                o = key_xyz[key]
                # +normal
                b = key_xyz[before]
                a = key_xyz[after]
                ob = normalize_vector_xy(subtract_vectors_xy(b, o))
                oa = normalize_vector_xy(subtract_vectors_xy(a, o))
                z = cross_z(ob, oa)
                if z > +tol:
                    n = normalize_vector_xy(add_vectors_xy(oa, ob))
                    n = scale_vector(n, -scale)
                elif z < -tol:
                    n = normalize_vector_xy(add_vectors_xy(oa, ob))
                    n = scale_vector(n, +scale)
                else:
                    ba = normalize_vector_xy(subtract_vectors_xy(a, b))
                    n = cross_vectors([0, 0, 1], ba)
                    n = scale_vector(n, +scale)
                # left and right
                lx, ly, lz = add_vectors_xy(o, rotate(n, +alpha))
                rx, ry, rz = add_vectors_xy(o, rotate(n, -alpha))
                l = self.add_vertex(x=lx, y=ly, z=o[2], is_fixed=True, _is_external=True)
                r = self.add_vertex(x=rx, y=ry, z=o[2], is_fixed=True, _is_external=True)
                key_foot[key] = l, r
                # foot face
                self.add_face([l, key, r], _is_loaded=False)
                # foot face attributes
                self.edge_attribute((l, key), '_is_external', True)
                self.edge_attribute((key, r), '_is_external', True)
                self.edge_attribute((r, l), '_is_edge', False)
        # add (opening?) faces
        for vertices in segments:
            if len(vertices) < 3:
                continue
            left = vertices[0]
            right = vertices[-1]
            start = None
            end = None
            if left in key_foot:
                start = key_foot[left][1]
            if right in key_foot:
                end = key_foot[right][0]
            if start is not None:
                vertices.insert(0, start)
            if end is not None:
                vertices.append(end)
            self.add_face(vertices, _is_loaded=False)
            self.edge_attribute((vertices[0], vertices[-1]), '_is_edge', False)

    # --------------------------------------------------------------------------
    # visualisation
    # --------------------------------------------------------------------------

    def plot(self):
        from compas_plotters import MeshPlotter
        plotter = MeshPlotter(self, figsize=(12, 8), tight=True)
        vertexcolor = {}
        vertexcolor.update({key: '#00ff00' for key in self.vertices_where({'is_fixed': True})})
        vertexcolor.update({key: '#0000ff' for key in self.vertices_where({'_is_external': True})})
        vertexcolor.update({key: '#ff0000' for key in self.vertices_where({'is_anchor': True})})
        plotter.draw_vertices(facecolor=vertexcolor)
        plotter.draw_edges(keys=list(self.edges_where({'_is_edge': True})))
        plotter.draw_faces(keys=list(self.faces_where({'_is_loaded': True})))
        plotter.show()

    def draw(self, layer=None, clear_layer=True, settings=None):
        from compas_tna.rhino import FormArtist
        artist = FormArtist(self, layer=layer)
        if clear_layer:
            artist.clear_layer()
        if not settings:
            settings = {}
        if settings.get('show.vertices', True):
            vertexcolor = {}
            vertexcolor.update({key: '#00ff00' for key in self.vertices_where({'is_fixed': True})})
            vertexcolor.update({key: '#0000ff' for key in self.vertices_where({'_is_external': True})})
            vertexcolor.update({key: '#ff0000' for key in self.vertices_where({'is_anchor': True})})
            artist.draw_vertices(color=vertexcolor)
        if settings.get('show.edges', True):
            artist.draw_edges(keys=list(self.edges_where({'_is_edge': True})))
        if settings.get('show.faces', True):
            artist.draw_faces(keys=list(self.faces_where({'_is_loaded': True})))
        if settings.get('show.forces', False):
            artist.draw_forces(scale=settings.get('scale.forces', 0.1))
        if settings.get('show.reactions', False):
            artist.draw_reactions(scale=settings.get('scale.reactions', 0.01))
        if settings.get('show.angles', False):
            artist.draw_angles(tol=settings.get('tol.angle', 5.0))
        artist.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
