from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.colors import Color
from compas.scene import MeshObject


class ForceDiagramObject(MeshObject):
    """Base class for TNA force diagrams.

    Attributes
    ----------
    diagram : :class:`compas_tna.diagrams.Diagram`
        A TNA diagram.

    """

    def __init__(self, *args, **kwargs):
        super(ForceDiagramObject, self).__init__(*args, **kwargs)

        self.vertexcolor = Color.white()
        self.edgecolor = Color.black()
        self.facecolor = Color.from_rgb255(210, 210, 210)

        self.show_vertices = True
        self.show_edges = True
        self.show_faces = False

        self.vertexsize = 0.1

    @property
    def diagram(self):
        return self.mesh

    @diagram.setter
    def diagram(self, diagram):
        self.mesh = diagram
