from typing import Any
from typing import Generator
from typing import Optional

from compas_tna.diagrams import Diagram
from compas_tna.diagrams import FormDiagram


class ForceDiagram(Diagram):
    """Class representing a TNA force diagram.

    Attributes
    ----------
    primal : :class:`compas_tna.diagrams.FormDiagram`
        The TNA form diagram corresponding to the force diagram.

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

    def __init__(self, *args, name="ForceDiagram", **kwargs):
        super().__init__(*args, name=name, **kwargs)

        self.primal = None
        self.attributes["scale"] = 1.0

        self.default_vertex_attributes.update(
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "is_fixed": False,
            }
        )
        self.default_edge_attributes.update(
            {
                "lmin": 0.0,
                "lmax": 1e7,
                "_a": 0.0,
            }
        )

    # --------------------------------------------------------------------------
    # Constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_formdiagram(cls, formdiagram: FormDiagram) -> "ForceDiagram":
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
        dual.vertices_attribute("z", 0.0)
        dual.primal = formdiagram
        formdiagram.dual = dual
        return dual

    # --------------------------------------------------------------------------
    # Vertices
    # --------------------------------------------------------------------------

    def fixed(self) -> Generator[int, None, None]:
        """Vertices with ``is_fixed`` set to ``True``.

        Returns
        -------
        generator
            A generator object for iteration over vertex keys that are fixed.

        """
        return self.vertices_where(is_fixed=True)

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def uv_index(self, form: Optional[FormDiagram] = None) -> dict[tuple[int, int], int]:
        """Construct a map relating edge uv pairs to their index in an edge list.

        Parameters
        ----------
        form : :class:`compas_tna.diagrams.FormDiagram`, optional
            If provided, this maps edge uv's to the index in a list
            matching the ordering of corresponding edges in the form diagram.

        Returns
        -------
        dict
            A dict mapping edge uv tuples to indices in an (ordered) edge list.

        """
        if not form:
            return {uv: index for index, uv in enumerate(self.edges())}
        uv_index = dict()
        for index, (u, v) in enumerate(form.edges_where(_is_edge=True)):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            uv_index[(f1, f2)] = index
        return uv_index

    def ordered_edges(self, form: FormDiagram) -> list[tuple[int, int]]:
        """Construct an edge list in which the edges are ordered
        according to the ordering of edges in a corresponding list of form diagram edges.

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

    def form_edge_attribute(self, form: FormDiagram, edge: tuple[int, int], name: str, value: Any = None) -> Any:
        """Get or set the attribute value of the corresponding edge in the form diagam.

        Parameters
        ----------
        form : :class:`FormDiagram`
            The form diagram.
        edge : tuple[int, int]
            The identifier of the edge.
        name : str
            The name of the attribute.
        value : Any, optional
            A new value.

        Returns
        -------
        Any

        """
        f1, f2 = edge
        for u, v in form.face_halfedges(f1):
            if form.halfedge[v][u] == f2:
                break
        return form.edge_attribute((u, v), name, value=value)
