from compas.colors import Color
from compas.scene import MeshObject


class ForceDiagramObject(MeshObject):
    """Base class for TNA force diagrams.

    Attributes
    ----------
    diagram : :class:`compas_tna.diagrams.Diagram`
        A TNA diagram.

    """

    def __init__(
        self,
        show_vertices=True,
        show_edges=True,
        show_faces=False,
        vertexcolor=Color.white(),
        edgecolor=Color.black(),
        facecolor=Color.from_rgb255(210, 210, 210),
        **kwargs,
    ):
        super().__init__(
            show_vertices=show_vertices,
            show_edges=show_edges,
            show_faces=show_faces,
            vertexcolor=vertexcolor,
            edgecolor=edgecolor,
            facecolor=facecolor,
            **kwargs,
        )

    @property
    def diagram(self):
        return self.mesh

    @diagram.setter
    def diagram(self, diagram):
        self.mesh = diagram
