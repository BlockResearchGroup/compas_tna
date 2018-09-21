from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh


__author__  = 'Tom Van Mele'
__email__   = 'vanmelet@ethz.ch'


__all__ = ['ForceDiagram']


class ForceDiagram(Mesh):
    """"""

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.scale = 1.0
        self.default_vertex_attributes.update({
            'x'        : 0.0,
            'y'        : 0.0,
            'z'        : 0.0,
            'is_fixed' : False,
        })
        self.default_edge_attributes.update({
            'l' : 0.0,
        })
        self.attributes.update({
            'name'         : 'ForceDiagram',
            'scale'        : 1.0,

            'color.vertex' : (255, 255, 255),
            'color.edge'   : (0, 0, 0),
            'color.face'   : (210, 210, 210),
        })

    # --------------------------------------------------------------------------
    # Constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_formdiagram(cls, formdiagram):
        return formdiagram.dual(cls)

    # --------------------------------------------------------------------------
    # Vertices
    # --------------------------------------------------------------------------

    def fixed(self):
        return self.vertices_where({'is_fixed': True})

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
        index_uv  = {index: uv for uv, index in iter(uv_index.items())}
        edges     = [index_uv[index] for index in range(self.number_of_edges())]
        return [[key_index[u], key_index[v]] for u, v in edges]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
