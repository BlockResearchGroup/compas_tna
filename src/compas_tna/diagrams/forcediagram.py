from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh
from compas.topology import mesh_dual


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['ForceDiagram', ]


class ForceDiagram(Mesh):
    """"""

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.scale = 1.0
        self.default_vertex_attributes.update({
            'x' : 0.0,
            'y' : 0.0,
            'z' : 0.0,
            'is_fixed'   : False,
        })
        self.default_edge_attributes.update({
            'l'   : 0.0,
            'lmin': 1e-7,
            'lmax': 1e+7,
        })
        self.attributes.update({
            'name'                  : 'ForceDiagram',
            'color.vertex:is_fixed' : (0, 0, 0),
        })

    # --------------------------------------------------------------------------
    # Constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_formdiagram(cls, formdiagram):
        return mesh_dual(formdiagram, cls)

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving attributes of the force diagram.
    # --------------------------------------------------------------------------

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def uv_index(self, form=None):
        if not form:
            return dict(((u, v), index) for index, (u, v) in enumerate(self.edges()))
        uv_index = dict()
        for index, (u, v) in enumerate(form.edges_where({'is_edge': True})):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            uv_index[(f1, f2)] = index
        return uv_index

    def ordered_edges(self, form):
        key_index = self.key_index()
        uv_index  = self.uv_index(form=form)
        index_uv  = dict((index, uv) for uv, index in iter(uv_index.items()))
        edges     = [index_uv[index] for index in range(self.number_of_edges())]
        return [[key_index[u], key_index[v]] for u, v in edges]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    from compas.numerical import fd_numpy
    from compas.plotters import MeshPlotter
    from compas.utilities import pairwise

    from compas_tna.tna.diagrams.formdiagram import FormDiagram
    from compas_tna.tna.algorithms.horizontal import horizontal_nodal

    form = FormDiagram.from_obj(compas.get('faces.obj'))

    for key in form.vertices_where({'vertex_degree': 2}):
        form.vertex[key]['is_anchor'] = True

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

    for vertices in unsupported:
        fkey = form.add_face(vertices, is_unloaded=True)

    for vertices in unsupported:
        u = vertices[-1]
        v = vertices[0]
        form.set_edge_attribute((u, v), 'is_edge', False)

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

    force = ForceDiagram.from_formdiagram(form)

    plotter = MeshPlotter(force)
    plotter.draw_vertices(text='key')
    plotter.draw_faces()
    plotter.draw_edges()
    plotter.show()
