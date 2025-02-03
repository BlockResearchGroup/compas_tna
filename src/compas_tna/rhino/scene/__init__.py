"""
This package provides scene object plugins for visualising TNA diagrams in Rhino.
When working in Rhino, :class:`compas.scene.SceneObject`
will automatically use the corresponding Rhino scene object for each TNA diagram type.
"""

from compas.plugins import plugin
from compas.scene import register

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from .formobject import RhinoFormObject
from .forceobject import RhinoForceObject


@plugin(category="factories", requires=["Rhino"])
def register_scene_objects():
    register(FormDiagram, RhinoFormObject, context="Rhino")
    register(ForceDiagram, RhinoForceObject, context="Rhino")

    # print("TNA Rhino SceneObjects registered.")


__all__ = [
    "RhinoFormObject",
    "RhinoForceObject",
]
