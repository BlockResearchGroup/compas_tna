from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.scene import MeshObject


class DiagramObject(MeshObject):
    """Base class for TNA diagrams.

    Parameters
    ----------
    diagram : :class:`compas_tna.diagrams.Diagram`
        A TNA diagram.

    Attributes
    ----------
    diagram : :class:`compas_tna.diagrams.Diagram`
        A TNA diagram.

    """

    def __init__(self, diagram, **kwargs):
        super(DiagramObject, self).__init__(mesh=diagram, **kwargs)
        self._diagram = None
        self.diagram = diagram

    @property
    def diagram(self):
        return self._diagram

    @diagram.setter
    def diagram(self, diagram):
        self._diagram = diagram
        self._transformation = None
        self._vertex_xyz = None
