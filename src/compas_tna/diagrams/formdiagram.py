from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sin
from math import cos
from math import sqrt

import compas

from compas.geometry import subtract_vectors_xy
from compas.geometry import add_vectors_xy
from compas.geometry import normalize_vector_xy
from compas.geometry import cross_vectors

from compas.datastructures import network_find_cycles
from compas.datastructures import Network

from compas_tna.diagrams import Diagram


__all__ = ['FormDiagram']


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

    A ``FormDiagram`` has the following default attributes

    *   ``default_vertex_attributes``

        *   ``x``  : The X coordinate of the vertex.
        *   ``y``  : The Y coordinate of the vertex.
        *   ``z``  : The Z coordinate of the vertex.
        *   ``px`` : The X component of the applied load on the vertex.
        *   ``py`` : The Y component of the applied load on the vertex.
        *   ``pz`` : The Z component of the applied load on the vertex.
        *   ``rx`` : The X component of the residual force at the vertex.
        *   ``ry`` : The Y component of the residual force at the vertex.
        *   ``rz`` : The Z component of the residual force at the vertex.
        *   ``sw`` : The selfweight of the structure at the vertex.
        *   ``t``  : The thickness of the structure at the vertex.
        *   ``is_anchor``   : Flag to indicate that the vertex is an anchor, i.e. a support
        *   ``is_fixed``    : Flag to indicate that the position of a vertex is fixed.
        *   ``is_external`` : Flag to indicate that a vertex is external to the structure.

    *   ``default_edge_attributes``

        *   ``q``    : The force density in the edge.
        *   ``f``    : The (horizontal) force in the edge.
        *   ``l``    : The length of the edge.
        *   ``a``    : The angle between this edge and the corresponding edge in the force diagram.
        *   ``qmin`` : The minimum force density allowed in the edge.
        *   ``qmax`` : The maximum force density allowed in the edge.
        *   ``fmin`` : The minimum (horizontal) force allowed in the edge.
        *   ``fmax`` : The maximum (horizontal) force allowed in the edge.
        *   ``lmin`` : The minimum length of the edge.
        *   ``lmax`` : The maximum length of the edge.
        *   ``is_edge``     : Flag to indicate that the edge represents an actual edge of the diagram.
        *   ``is_external`` : Flag to indicate that the edge represents an external force.

    *   ``default_face_attributes``

        *   ``is_loaded`` : Flag to indicate that a face of the form diagram is part of the surface of the structure.

    """

    __module__ = 'compas_tna.diagrams'

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'px': 0.0,
            'py': 0.0,
            'pz': 0.0,
            'sw': 0.0,
            't': 1.0,
            'is_anchor': False,
            'is_fixed': False,
            'is_external': False,
            'rx': 0.0,
            'ry': 0.0,
            'rz': 0.0,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            'f': 0.0,
            'l': 0.0,
            'a': 0.0,
            'qmin': 0.0,
            'qmax': 1e+7,
            'lmin': 0.0,
            'lmax': 1e+7,
            'fmin': 0.0,
            'fmax': 1e+7,
            'is_edge': True,
            'is_external': False,
            'is_tension': False
        })
        self.default_face_attributes.update({
            'is_loaded': True
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
        .. code-block:: python

            import compas
            from compas.datastructures import Mesh
            from compas_tna.diagrams import FormDiagram

            mesh = Mesh.from_obj(compas.get('faces.obj'))
            form = FormDiagram.from_mesh(mesh)
            form.plot()
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
        nume = len(list(self.edges_where({'is_edge': True})))
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
        return {(u, v): index for index, (u, v) in enumerate(self.edges_where({'is_edge': True}))}

    def index_uv(self):
        """Returns a dictionary that maps edges in a list to the corresponding
        vertex key pairs.

        Returns
        -------
        dict
            A dictionary of index-uv pairs.

        """
        return dict(enumerate(self.edges_where({'is_edge': True})))

    # --------------------------------------------------------------------------
    # dual and reciprocal
    # --------------------------------------------------------------------------

    def dual(self, cls):
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
        # there is a discrepancy between the norm of residuals calculated by the equilibrium functions`
        # and the result found here
        R = 0
        for key, attr in self.vertices_where({'is_anchor': False, 'is_fixed': False}, True):
            rx, ry, rz = attr['rx'], attr['ry'], attr['rz']
            R += sqrt(rx ** 2 + ry ** 2 + rz ** 2)
        return R

    # --------------------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------------------

    # def bbox(self):
    #     x, y, z = zip(* self.vertices_attributes('xyz'))
    #     return (min(x), min(y), min(z)), (max(x), max(y), max(z))

    # --------------------------------------------------------------------------
    # postprocess
    # --------------------------------------------------------------------------

    # def collapse_small_edges(self, tol=1e-2):
    #     boundaries = self.vertices_on_boundaries()
    #     for boundary in boundaries:
    #         for u, v in pairwise(boundary):
    #             l = self.edge_length(u, v)
    #             if l < tol:
    #                 mesh_collapse_edge(self, v, u, t=0.5, allow_boundary=True)

    # def smooth(self, fixed, kmax=10):
    #     mesh_smooth_area(self, fixed=fixed, kmax=kmax)

    # --------------------------------------------------------------------------
    # boundary conditions
    # --------------------------------------------------------------------------

    # update boundaries should loop over all boundaries
    # containing anchors

    def update_boundaries(self, feet=2):
        boundaries = self.vertices_on_boundaries()
        exterior = boundaries[0]
        interior = boundaries[1:]
        self.update_exterior(exterior, feet=feet)
        self.update_interior(interior)

    def update_exterior(self, boundary, feet=2):
        """"""
        segments = self.split_boundary(boundary)
        if not feet:
            for vertices in segments:
                if len(vertices) > 2:
                    self.add_face(vertices, is_loaded=False)
                    u = vertices[-1]
                    v = vertices[0]
                    self.edge_attribute((u, v), 'is_edge', False)
                else:
                    u, v = vertices
                    self.edge_attribute((u, v), 'is_edge', False)
        else:
            self.add_feet(segments, feet=feet)

    def update_interior(self, boundaries):
        """"""
        for vertices in boundaries:
            self.add_face(vertices, is_loaded=False)

    def split_boundary(self, boundary):
        """"""
        segment = []
        segments = [segment]
        for key in boundary:
            segment.append(key)
            if self.vertex_attribute(key, 'is_anchor'):
                segment = [key]
                segments.append(segment)
        segments[-1] += segments[0]
        del segments[0]
        return segments

    def add_feet(self, segments, feet=2):
        """"""
        def rotate(point, angle):
            x = cos(angle) * point[0] - sin(angle) * point[1]
            y = sin(angle) * point[0] + cos(angle) * point[1]
            return x, y, 0

        def cross_z(ab, ac):
            return ab[0] * ac[1] - ab[1] * ac[0]

        scale = self.attributes['feet.scale']
        alpha = self.attributes['feet.alpha'] * pi / 180
        tol = self.attributes['feet.tol']

        key_foot = {}
        key_xyz = {key: self.vertex_coordinates(key, 'xyz') for key in self.vertices()}

        for i, vertices in enumerate(segments):
            key = vertices[0]
            after = vertices[1]
            before = segments[i - 1][-2]

            b = key_xyz[before]
            o = key_xyz[key]
            a = key_xyz[after]

            ob = normalize_vector_xy(subtract_vectors_xy(b, o))
            oa = normalize_vector_xy(subtract_vectors_xy(a, o))

            z = cross_z(ob, oa)

            if z > +tol:
                r = normalize_vector_xy(add_vectors_xy(oa, ob))
                r = [-scale * axis for axis in r]

            elif z < -tol:
                r = normalize_vector_xy(add_vectors_xy(oa, ob))
                r = [+scale * axis for axis in r]

            else:
                ba = normalize_vector_xy(subtract_vectors_xy(a, b))
                r = cross_vectors([0, 0, 1], ba)
                r = [+scale * axis for axis in r]

            if feet == 1:
                x, y, z = add_vectors_xy(o, r)
                m = self.add_vertex(x=x, y=y, z=o[2], is_fixed=True, is_external=True)
                key_foot[key] = m

            elif feet == 2:
                lx, ly, lz = add_vectors_xy(o, rotate(r, +alpha))
                rx, ry, rz = add_vectors_xy(o, rotate(r, -alpha))
                l = self.add_vertex(x=lx, y=ly, z=o[2], is_fixed=True, is_external=True)
                r = self.add_vertex(x=rx, y=ry, z=o[2], is_fixed=True, is_external=True)
                key_foot[key] = l, r

            else:
                pass

        for vertices in segments:
            l = vertices[0]
            r = vertices[-1]

            if feet == 1:
                lm = key_foot[l]
                rm = key_foot[r]
                self.add_face([lm] + vertices + [rm], is_loaded=False)
                self.edge_attribute((l, lm), 'is_external', True)
                self.edge_attribute((rm, lm), 'is_edge', False)

            elif feet == 2:
                lb = key_foot[l][0]
                la = key_foot[l][1]
                rb = key_foot[r][0]
                self.add_face([lb, l, la], is_loaded=False)
                self.add_face([la] + vertices + [rb], is_loaded=False)
                self.edge_attribute((l, lb), 'is_external', True)
                self.edge_attribute((l, la), 'is_external', True)
                self.edge_attribute((lb, la), 'is_edge', False)
                self.edge_attribute((la, rb), 'is_edge', False)

            else:
                pass

    # --------------------------------------------------------------------------
    # visualisation
    # --------------------------------------------------------------------------

    def plot(self):
        from compas_plotters import MeshPlotter
        plotter = MeshPlotter(self, figsize=(12, 8), tight=True)
        vertexcolor = {}
        vertexcolor.update({key: '#00ff00' for key in self.vertices_where({'is_fixed': True})})
        vertexcolor.update({key: '#0000ff' for key in self.vertices_where({'is_external': True})})
        vertexcolor.update({key: '#ff0000' for key in self.vertices_where({'is_anchor': True})})
        plotter.draw_vertices(facecolor=vertexcolor)
        plotter.draw_edges(keys=list(self.edges_where({'is_edge': True})))
        plotter.draw_faces(keys=list(self.faces_where({'is_loaded': True})))
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
            vertexcolor.update({key: '#0000ff' for key in self.vertices_where({'is_external': True})})
            vertexcolor.update({key: '#ff0000' for key in self.vertices_where({'is_anchor': True})})
            artist.draw_vertices(color=vertexcolor)
        if settings.get('show.edges', True):
            artist.draw_edges(keys=list(self.edges_where({'is_edge': True})))
        if settings.get('show.faces', True):
            artist.draw_faces(keys=list(self.faces_where({'is_loaded': True})))
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

    import compas
    from compas.datastructures import Mesh
    from compas.files import OBJ

    filepath = compas.get('lines.obj')

    obj = OBJ(filepath)
    vertices = obj.parser.vertices
    edges = obj.parser.lines
    lines = [(vertices[u], vertices[v], 0) for u, v in edges]

    form = FormDiagram.from_lines(lines, delete_boundary_face=False)

    mesh = Mesh.from_obj(compas.get('faces.obj'))
    height = 5.0
    mesh.set_vertices_attribute('z', height)
    form = FormDiagram.from_mesh(mesh)

    assert form.number_of_faces() == mesh.number_of_faces()
    assert form.number_of_vertices() == mesh.number_of_vertices()
    assert max(mesh.get_vertices_attribute('z')) - height == max(form.get_vertices_attribute('z'))

    form.plot()
