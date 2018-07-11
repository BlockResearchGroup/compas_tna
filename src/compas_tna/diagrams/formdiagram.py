from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sin
from math import cos
from math import sqrt

from compas.datastructures import Mesh
from compas.utilities import geometric_key
from compas.utilities import pairwise

from compas.datastructures.mesh.mesh import TPL

from compas.geometry import subtract_vectors_xy
from compas.geometry import add_vectors_xy
from compas.geometry import normalize_vector_xy
from compas.geometry import cross_vectors


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['FormDiagram', ]


class FormDiagram(Mesh):
    """"""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.default_vertex_attributes.update({
            'x'         : 0.0,
            'y'         : 0.0,
            'z'         : 0.0,
            'px'        : 0.0,
            'py'        : 0.0,
            'pz'        : 0.0,
            'sw'        : 0.0,
            't'         : 1.0,
            'is_anchor' : False,
            'is_fixed'  : False,
            'rx'        : 0.0,
            'ry'        : 0.0,
            'rz'        : 0.0,
        })
        self.default_edge_attributes.update({
            'q'      : 1.0,
            'l'      : 0.0,
            'f'      : 0.0,
            'qmin'   : 1e-7,
            'qmax'   : 1e+7,
            'lmin'   : 1e-7,
            'lmax'   : 1e+7,
            'fmin'   : 1e-7,
            'fmax'   : 1e+7,
            'a'      : 0.0,
            'is_ind' : False,
            'is_edge': True,
        })
        self.default_face_attributes.update({
            'is_loaded': True
        })
        self.attributes.update({
            'name'                       : 'FormDiagram',
            'color.vertex'               : (255, 255, 255),
            'color.edge'                 : (0, 0, 0),
            'color.face'                 : (210, 210, 210),
            'color.vertex:is_anchor'     : (255, 0, 0),
            'color.vertex:is_fixed'      : (0, 0, 0),
            'color.vertex:is_supported'  : (255, 0, 0),
            'color.vertex:is_prescribed' : (0, 255, 0),
            'color.reaction'             : (0, 255, 0),
            'color.residual'             : (0, 255, 255),
            'color.load'                 : (0, 0, 255),
            'color.selfweight'           : (0, 0, 255),
            'scale.reaction'             : 1.0,
            'scale.residual'             : 1.0,
            'scale.load'                 : 1.0,
            'scale.selfweight'           : 1.0,
            'foot.scale'                 : 0.1,
            'foot.alpha'                 : 45,
            'foot.tol'                   : 0.1,
        })

    def __str__(self):
        """Compile a summary of the mesh."""
        numv = self.number_of_vertices()
        nume = len(list(self.edges_where({'is_edge': True})))
        numf = self.number_of_faces()

        vmin = self.vertex_min_degree()
        vmax = self.vertex_max_degree()
        fmin = self.face_min_degree()
        fmax = self.face_max_degree()

        return TPL.format(self.name, numv, nume, numf, vmin, vmax, fmin, fmax)

    def uv_index(self):
        """Returns a dictionary that maps edge keys (i.e. pairs of vertex keys)
        to the corresponding edge index in a list or array of edges.

        Returns
        -------
        dict
            A dictionary of uv-index pairs.

        See Also
        --------
        * :meth:`index_uv`

        """
        return {(u, v): index for index, (u, v) in enumerate(self.edges_where({'is_edge': True}))}

    def index_uv(self):
        """Returns a dictionary that maps edges in a list to the corresponding
        vertex key pairs.

        Returns
        -------
        dict
            A dictionary of index-uv pairs.

        See Also
        --------
        * :meth:`uv_index`

        """
        return dict(enumerate(self.edges_where({'is_edge': True})))

    def dual(self, cls):
        dual = cls()

        fkey_centroid = {fkey: self.face_centroid(fkey) for fkey in self.faces()}
        outer = self.vertices_on_boundary()[0]
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
        return self.vertices_where({'vertex_degree': 1})

    def corners(self):
        return self.vertices_where({'vertex_degree': 2})

    # --------------------------------------------------------------------------
    # edges
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # faces
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------------------

    def anchors(self):
        return [key for key, attr in self.vertices(True) if attr['is_anchor']]

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    # --------------------------------------------------------------------------
    # boundary
    # --------------------------------------------------------------------------

    def vertices_on_boundary(self):
        """Find the vertices on the boundary.

        Parameters
        ----------
        ordered : bool, optional
            If ``True``, Return the vertices in the same order as they are found on the boundary.
            Default is ``False``.

        Returns
        -------
        list
            The vertices of the boundary.

        Warning
        -------
        If the vertices are requested in order, and the mesh has multiple borders,
        currently only the vertices of one of the borders will be returned.

        Examples
        --------
        >>>

        """
        vertices_set = set()
        for key, nbrs in iter(self.halfedge.items()):
            for nbr, face in iter(nbrs.items()):
                if face is None:
                    vertices_set.add(key)
                    vertices_set.add(nbr)
        vertices_all = list(vertices_set)

        boundaries = []
        key = sorted([(key, self.vertex_coordinates(key)) for key in vertices_all], key=lambda x: (x[1][1], x[1][0]))[0][0]

        while vertices_all:
            vertices = []
            start = key

            while 1:
                for nbr, fkey in iter(self.halfedge[key].items()):
                    if fkey is None:
                        vertices.append(nbr)
                        key = nbr
                        break

                if key == start:
                    boundaries.append(vertices)
                    vertices_all = [x for x in vertices_all if x not in vertices]
                    break

            if vertices_all:
                key = vertices_all[0]            

        return boundaries

    def is_boundary_convex(self, boundary):
        # return dict with key => True/False
        # return dict with key => cross_z
        pass

    # --------------------------------------------------------------------------
    # postprocess
    # --------------------------------------------------------------------------

    def collapse_small_edges(self, tol=1e-2):
        boundaries = self.vertices_on_boundary()
        for boundary in boundaries:
            for u, v in pairwise(boundary):
                l = self.edge_length(u, v)
                if l < tol:
                    self.collapse_edge(v, u, t=0.5, allow_boundary=True)

    def set_anchors(self, points=None, degree=0):
        if points:
            xyz_key = self.key_xyz()
            for xyz in points:
                gkey = geometric_key(xyz)
                if gkey in xyz_key:
                    key = xyz_key[gkey]
                    self.set_vertex_attribute(key, 'is_anchor', True)
        if degree:
            for key in self.vertices():
                if self.vertex_degree(key) <= degree:
                    self.set_vertex_attribute(key, 'is_anchor', True)

    def relax(self, fixed):
        from compas.numerical import fd_numpy
        key_index = self.key_index()
        vertices = self.get_vertices_attributes('xyz')
        edges = list(self.edges_where({'is_edge': True}))
        edges = [(key_index[u], key_index[v]) for u, v in edges]
        fixed = list(fixed)
        fixed = [key_index[key] for key in fixed]
        qs = [self.get_edge_attribute(uv, 'q') for uv in edges]
        loads = self.get_vertices_attributes(('px', 'py', 'pz'), (0, 0, 0))
        xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, qs, loads)
        for key, attr in self.vertices(True):
            index = key_index[key]
            attr['x'] = xyz[index][0]
            attr['y'] = xyz[index][1]
            attr['z'] = xyz[index][2]

    def smooth_interior(self):
        pass

    def update_exterior(self, boundary, feet=2):
        """"""
        segments = self.split_boundary(boundary)
        if not feet:
            for vertices in segments:
                if len(vertices) > 2:
                    self.add_face(vertices, is_loaded=False)
                    u = vertices[-1]
                    v = vertices[0]
                    self.set_edge_attribute((u, v), 'is_edge', False)
                else:
                    u, v = vertices
                    self.set_edge_attribute((u, v), 'is_edge', False)
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
            if self.vertex[key]['is_anchor']:
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

        scale = self.attributes['foot.scale']
        alpha = self.attributes['foot.alpha'] * pi / 180
        tol   = self.attributes['foot.tol']

        key_foot = {}
        key_xy = {key: self.vertex_coordinates(key, 'xy') for key in self.vertices()}

        for i, vertices in enumerate(segments):
            key = vertices[0]
            after = vertices[1]
            before = segments[i - 1][-2]

            b = key_xy[before]
            o = key_xy[key]
            a = key_xy[after]

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
                m = self.add_vertex(x=x, y=y, z=0, is_fixed=True)
                key_foot[key] = m

            elif feet == 2:
                lx, ly, lz = add_vectors_xy(o, rotate(r, +alpha))
                rx, ry, rz = add_vectors_xy(o, rotate(r, -alpha))
                l = self.add_vertex(x=lx, y=ly, z=0, is_fixed=True)
                r = self.add_vertex(x=rx, y=ry, z=0, is_fixed=True)
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
                self.set_edge_attribute((rm, lm), 'is_edge', False)

            elif feet == 2:
                lb = key_foot[l][0]
                la = key_foot[l][1]
                rb = key_foot[r][0]
                self.add_face([lb, l, la], is_loaded=False)
                self.add_face([la] + vertices + [rb], is_loaded=False)
                self.set_edge_attribute((lb, la), 'is_edge', False)
                self.set_edge_attribute((la, rb), 'is_edge', False)
            
            else:
                pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
