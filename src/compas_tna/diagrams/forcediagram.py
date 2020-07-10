from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_tna.diagrams import Diagram


__all__ = ['ForceDiagram']


class ForceDiagram(Diagram):
    """The ``ForceDiagram`` defines a TNA force diagram.

    Attributes
    ----------
    primal : :class:`compas_tna.diagrams.FormDiagram`
        The TNA form diagram corresponding to the force diagram.
    scale : float
        The scale factor for calculating horizontal forces based on edge lengths.
        The horizontal force in an edge of the form diagram is equal
        to the length of the corresponding edge in the force diagram multiplied by the scale factor.
    default_vertex_attributes : dict
        The names and default values of the attributes of vertices.
    default_edge_attributes : dict
        The names and default values of the attributes of the edges.
    default_face_attributes : dict
        The names and default values of the attributes of the faces.

    Notes
    -----
    In TNA, a pair of form and force diagrams describe the horizontal equilibrium of a 3D network of forces
    with vertical loads applied to its nodes, if they are reciprocal.
    This means they are each others dual and that corresponding edge pairs are at a constant angle.
    Typically this angle is 0 or 90 degrees, but any other constant angle is sufficient.

    When the force diagram is created from the form diagram, both diagrams are dual.
    However, the reciprocal relationship has to be established separately,
    using one of the horizontal equilibrium solvers.

    """

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
            'lmin': 0.0,
            'lmax': 1e+7,

            '_a': 0.0,
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
        """Construct a force diagram from a given form diagram.

        Parameters
        ----------
        formdiagram : :class:`compas_tna.diagrams.FormDiagram`
            A form diagram instance.

        Returns
        -------
        :class:`compas_tna.diagrams.ForceDiagram`
            The dual force diagram.

        """
        dual = formdiagram.dual_diagram(cls)
        dual.vertices_attribute('z', 0.0)
        dual.primal = formdiagram
        formdiagram.dual = dual
        return dual

    # --------------------------------------------------------------------------
    # Vertices
    # --------------------------------------------------------------------------

    def fixed(self):
        """Vertices with ``is_fixed`` set to ``True``.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are fixed.
        """
        return self.vertices_where({'is_fixed': True})

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def uv_index(self, form=None):
        """Construct a map relating edge uv pairs to their index in an edge list.

        Parameters
        ----------
        form : :class:`compas_tna.diagrams.FormDiagram`, optional
            If provided, this maps edge uv's to the index in a list matching the ordering of corresponding edges in the form diagram.

        Returns
        -------
        dict
            A dict mapping edge uv tuples to indices in an (ordered) edge list.
        """
        if not form:
            return {uv: index for index, uv in enumerate(self.edges())}
        uv_index = dict()
        for index, (u, v) in enumerate(form.edges_where({'_is_edge': True})):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            uv_index[(f1, f2)] = index
        return uv_index

    def ordered_edges(self, form):
        """Construct an edge list in which the edges are ordered according to the ordering of edges in a corresponding list of form diagram edges.

        Parameters
        ----------
        form : :class:`compas_tna.diagrams.FormDiagram`, optional
            The form diagram according to which the edges should be ordered.

        Returns
        -------
        list
            A list of edge uv tuples.
        """
        uv_index = self.uv_index(form=form)
        index_uv = {index: uv for uv, index in iter(uv_index.items())}
        edges = [index_uv[index] for index in range(self.number_of_edges())]
        return edges

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
        """Plot a force diagram with a plotter with all the default settings."""
        from compas_plotters import MeshPlotter
        plotter = MeshPlotter(self, figsize=(12, 8), tight=True)
        plotter.draw_vertices(radius=0.05)
        plotter.draw_edges()
        plotter.show()

    def draw(self, layer=None, clear_layer=True, settings=None):
        """Draw the force diagram in Rhino.

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
