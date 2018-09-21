from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import compas
import compas_rhino

from compas.utilities import flatten
from compas.utilities import geometric_key

from compas_rhino.geometry import RhinoPoint
from compas_rhino.geometry import RhinoCurve

from compas_rhino.modifiers import VertexModifier
from compas_rhino.modifiers import EdgeModifier
from compas_rhino.modifiers import FaceModifier

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector


__author__  = 'Tom Van Mele'
__email__   = 'vanmelet@ethz.ch'


__all__ = ['FormHelper']


def match_edges(mesh, keys):
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


def select_edges(mesh, keys):
    guids = match_edges(mesh, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def unselect_edges(mesh, keys):
    guids = match_edges(mesh, keys)
    rs.EnableRedraw(False)
    rs.UnselectObjects(guids)
    rs.EnableRedraw(True)


class FormHelper(VertexSelector,
                 EdgeSelector,
                 FaceSelector,
                 VertexModifier,
                 EdgeModifier,
                 FaceModifier):

    @staticmethod
    def select_continuous_edges(form):
        keys = FormHelper.select_edges(form)
        if not keys:
            return
        keys = [form.get_continuous_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        select_edges(form, keys)

    @staticmethod
    def identify_vertices_on_points(form, guids):
        gkey_key = form.gkey_key()
        keys = []
        for guid in guids:
            point = RhinoPoint(guid)
            gkey = geometric_key(point.xyz)
            if gkey in gkey_key:
                key = gkey_key[gkey]
                keys.append(key)
        return keys

    @staticmethod
    def identify_vertices_on_curves(form, guids):
        gkey_key = form.gkey_key()
        keys = []
        for guid in guids:
            curve = RhinoCurve(guid)
            for key in form.vertices():
                xyz = form.vertex_coordinates(key)
                closest = curve.closest_point(xyz)
                gkey = geometric_key(closest)
                if gkey in gkey_key:
                    if key == gkey_key[gkey]:
                        keys.append(key)
        return keys
