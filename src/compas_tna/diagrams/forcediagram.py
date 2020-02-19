from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_tna.diagrams import Diagram


__all__ = ['ForceDiagram']


class ForceDiagram(Diagram):
    """"""

    __module__ = 'compas_tna.diagrams'

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.primal = None
        self.scale = 1.0
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'is_fixed': False,
        })
        self.default_edge_attributes.update({
        })
        self.attributes.update({
            'name': 'ForceDiagram',
            'scale': 1.0,

            'color.vertex': (255, 255, 255),
            'color.edge': (0, 0, 0),
            'color.face': (210, 210, 210),
        })

    # --------------------------------------------------------------------------
    # Constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_formdiagram(cls, formdiagram):
        dual = formdiagram.dual(cls)
        dual.vertices_attribute('z', 0.0)
        dual.primal = formdiagram
        return dual

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
        uv_index = self.uv_index(form=form)
        index_uv = {index: uv for uv, index in iter(uv_index.items())}
        edges = [index_uv[index] for index in range(self.number_of_edges())]
        return [[key_index[u], key_index[v]] for u, v in edges]

    def get_form_edge_attribute(self, form, key, name, value=None):
        f1, f2 = key
        for u, v in form.face_halfedges(f1):
            if form.halfedge[v][u] == f2:
                break
        return form.edge_attribute((u, v), name, value=value)

    # --------------------------------------------------------------------------
    # visualisation
    # --------------------------------------------------------------------------

    def plot(self):
        from compas_plotters import MeshPlotter
        plotter = MeshPlotter(self, figsize=(12, 8), tight=True)
        plotter.draw_vertices(radius=0.05)
        plotter.draw_edges()
        plotter.show()

    def draw(self, layer=None, clear_layer=True, settings=None):
        from compas_tna.rhino import ForceArtist
        artist = ForceArtist(self, layer=layer)
        if clear_layer:
            artist.clear_layer()
        if not settings:
            settings = {}
        vertexcolor = {}
        vertexcolor.update({key: '#00ff00' for key in self.vertices_where({'is_fixed': True})})
        artist.draw_vertices(color=vertexcolor)
        artist.draw_edges()
        artist.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
