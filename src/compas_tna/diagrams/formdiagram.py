from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh
from compas.utilities import geometric_key

from compas.datastructures.mesh.mesh import TPL


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
            'x'            : 0.0,
            'y'            : 0.0,
            'z'            : 0.0,
            'px'           : 0.0,
            'py'           : 0.0,
            'pz'           : 0.0,
            'sw'           : 0.0,
            't'            : 1.0,
            'cx'           : 0.0,
            'cy'           : 0.0,
            'cz'           : 0.0,
            'zpre'         : 0.0,
            'z-'           : 0.0,
            'z+'           : 0.0,
            'weight'       : 1.0,
            'is_anchor'    : False,
            'is_fixed'     : False,
            'is_prescribed': False,
            'rx'           : 0.0,
            'ry'           : 0.0,
            'rz'           : 0.0,
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

    # --------------------------------------------------------------------------
    # vertices
    # --------------------------------------------------------------------------

    def leaves(self):
        return self.vertices_where({'vertex_degree': 1})

    # --------------------------------------------------------------------------
    # edges
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # faces
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving the attributes of the formdiagram.
    # --------------------------------------------------------------------------

    def anchors(self):
        return [key for key, attr in self.vertices(True) if attr['is_anchor']]

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_anchor']]
        # return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    # --------------------------------------------------------------------------
    # Identify features of the formdiagram based on geometrical inputs.
    # --------------------------------------------------------------------------

    def identify_vertices(self, points):
        xyz_key = self.key_xyz()
        for xyz in points:
            gkey = geometric_key(xyz)
            if gkey in xyz_key:
                key = xyz_key[gkey]
                self.vertex[key]['is_anchor'] = True


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    from compas.numerical import fd_numpy
    from compas.utilities import pairwise

    from compas_tna.viewers import Viewer2


    form = FormDiagram.from_obj(compas.get('faces.obj'))

    # anchors can be identified by matching geometrical locations
    # or by vertex degree

    for key in form.vertices_where({'vertex_degree': 2}):
        form.vertex[key]['is_anchor'] = True

    # unsupported edges are on the boundary
    # between anchors

    boundary = form.vertices_on_boundary(ordered=True)

    unsupported = [[]]
    for key in boundary:
        unsupported[-1].append(key)
        if form.vertex[key]['is_anchor']:
            unsupported.append([key])

    unsupported[-1] += unsupported[0]
    del unsupported[0]

    for vertices in unsupported:
        for u, v in pairwise(vertices):
            form.set_edge_attribute((u, v), 'q', 10)

    # there should be a face on the outside of an unsupported boundary
    # the outside edge of the face is not a real edge
    # the face is also not really part of the structure and therefore not loaded

    for vertices in unsupported:
        fkey = form.add_face(vertices, is_loaded=False)

    for vertices in unsupported:
        u = vertices[-1]
        v = vertices[0]
        form.set_edge_attribute((u, v), 'is_edge', False)

    # compute horizontal equilibrium

    vertices = form.get_vertices_attributes('xyz')
    edges = list(form.edges_where({'is_edge': True}))
    fixed = list(form.vertices_where({'is_anchor': True}))
    qs = [form.get_edge_attribute(uv, 'q') for uv in edges]
    loads = form.get_vertices_attributes(('px', 'py', 'pz'), (0, 0, 0))

    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, qs, loads)

    for key, attr in form.vertices(True):
        attr['x'] = xyz[key][0]
        attr['y'] = xyz[key][1]
        attr['z'] = xyz[key][2]

    # visualise

    viewer = Viewer2(form, None)

    viewer.setup()
    viewer.draw_form()
    viewer.show()
