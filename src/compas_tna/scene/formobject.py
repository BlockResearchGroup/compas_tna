from compas.colors import Color
from compas.scene import MeshObject


class FormDiagramObject(MeshObject):
    """Base class for TNA form diagrams.

    Attributes
    ----------
    diagram : :class:`compas_tna.diagrams.Diagram`
        A TNA diagram.

    """

    def __init__(
        self,
        show_vertices=True,
        show_edges=True,
        show_faces=True,
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

        self.vertexcolor_fixed = Color.blue()
        self.vertexcolor_support = Color.red()

        self.color_reaction = Color.green()
        self.color_residual = Color.cyan()
        self.color_load = Color.green()
        self.color_selfweight = Color.blue()
        self.color_force = Color.blue()

        self.scale_reaction = 1.0
        self.scale_residual = 1.0
        self.scale_load = 1.0
        self.scale_force = 1.0
        self.scale_selfweight = 1.0

        self.tol_reaction = 1e-3
        self.tol_residual = 1e-3
        self.tol_load = 1e-3
        self.tol_force = 1e-3
        self.tol_selfweight = 1e-3

        self.show_selfweight = False
        self.show_loads = False
        self.show_reactions = False
        self.show_residuals = False
        self.show_forces = False
        self.show_angles = False

    @property
    def diagram(self):
        return self.mesh

    @diagram.setter
    def diagram(self, diagram):
        self.mesh = diagram

    def draw_loads(self):
        raise NotImplementedError

    def draw_selfweight(self):
        raise NotImplementedError

    def draw_reactions(self):
        raise NotImplementedError

    def draw_forces(self):
        raise NotImplementedError

    def draw_residuals(self):
        raise NotImplementedError

    def draw_angles(self):
        raise NotImplementedError
