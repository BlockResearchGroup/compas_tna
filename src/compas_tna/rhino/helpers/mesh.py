from __future__ import print_function

from ast import literal_eval

import compas
import compas_rhino

from compas.utilities import geometric_key

from compas_rhino.geometry import RhinoSurface

from compas_rhino.artists import MeshArtist

from compas_rhino.modifiers import Modifier
from compas_rhino.modifiers import VertexModifier
from compas_rhino.modifiers import EdgeModifier
from compas_rhino.modifiers import FaceModifier

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector

try:
    import Rhino
    import scriptcontext as sc
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


__author__    = ['Tom Van Mele']
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'mesh_select_edges',
    'mesh_unselect_edges'
]


def mesh_match_edges(mesh, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(mesh.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')[2].split('-')
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def mesh_select_edges(mesh, keys):
    guids = mesh_match_edges(mesh, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def mesh_unselect_edges(mesh, keys):
    guids = mesh_match_edges(mesh, keys)
    rs.EnableRedraw(False)
    rs.UnselectObjects(guids)
    rs.EnableRedraw(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    import compas
    from compas.datastructures import Mesh
    from compas_rhino import mesh_draw
    from compas_rhino import mesh_select_vertex
    from compas_rhino import mesh_move_vertex

    mesh = Mesh.from_obj(compas.get_data('quadmesh_planar.obj'))

    mesh_draw(mesh, layer='test', clear_layer=True)

#    key = mesh_select_vertex(mesh)
#
#    if mesh_move_vertex(mesh, key):
#        mesh_draw(mesh, layer='test', clear_layer=True)
