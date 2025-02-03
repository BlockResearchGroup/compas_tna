"""
This package provides scene object plugins for visualising TNA diagrams in Jupyter Notebooks.
When working in a notebook, :class:`compas.scene.SceneObject`
will automatically use the corresponding scene object for each TNA diagram type.
"""

from compas.plugins import plugin
from compas.scene import register

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram
from .formobject import ThreeFormObject
from .forceobject import ThreeForceObject


@plugin(category="factories", requires=["pythreejs"])
def register_scene_objects():
    register(FormDiagram, ThreeFormObject, context="Notebook")
    register(ForceDiagram, ThreeForceObject, context="Notebook")

    # print("TNA Notebook SceneObjects registered.")


__all__ = [
    "ThreeFormObject",
    "ThreeForceObject",
]
