from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import FaceNetwork
from compas.utilities import geometric_key


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class FormDiagram(FaceNetwork):
    """"""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.default_vertex_attributes.update({
            'x'            : 0.0,
            'y'            : 0.0,
            'z'            : 0.0,
            'px'           : 0.0,
            'py'           : 0.0,
            'pz'           : 0.0,
            'sw'           : 0.0,
            't'            : 1.0,
            'cx'           : 0.0,
            'cy'           : 0.0,
            'cz'           : 0.0,
            'zpre'         : 0.0,
            'z-'           : 0.0,
            'z+'           : 0.0,
            'weight'       : 1.0,
            'is_anchor'    : False,
            'is_fixed'     : False,
            'is_prescribed': False,
            'rx'           : 0.0,
            'ry'           : 0.0,
            'rz'           : 0.0,
        })
        self.default_edge_attributes.update({
            'q'     : 1.0,
            'l'     : 0.0,
            'f'     : 0.0,
            'qmin'  : 1e-7,
            'qmax'  : 1e+7,
            'lmin'  : 1e-7,
            'lmax'  : 1e+7,
            'fmin'  : 1e-7,
            'fmax'  : 1e+7,
            'a'     : 0.0,
            'is_ind': False,
        })
        self.default_face_attributes.update({
            'is_unloaded': False
        })
        self.attributes.update({
            'name'                       : 'FormDiagram',
            'anchor_degree'              : 1,
            'autofaces'                  : True,
            'color.vertex'               : (255, 255, 255),
            'color.edge'                 : (0, 0, 0),
            'color.face'                 : (0, 255, 255),
            'color.vertex:is_anchor'     : (255, 0, 0),
            'color.vertex:is_fixed'      : (0, 0, 0),
            'color.vertex:is_supported'  : (255, 0, 0),
            'color.vertex:is_prescribed' : (0, 255, 0),
            'color.face:is_unloaded'     : (0, 0, 255),
        })

    # --------------------------------------------------------------------------
    # faces
    # --------------------------------------------------------------------------

    def breakpoints(self):
        return list(set(self.leaves() + self.anchors()))

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving the attributes of the formdiagram.
    # --------------------------------------------------------------------------

    def anchors(self):
        return [key for key, attr in self.vertices(True) if attr['is_anchor']]

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_anchor']]
        # return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    def prescribed(self):
        return [key for key, attr in self.vertices(True) if attr['is_prescribed']]

    # this implies the vertices have an attribute 'is_constrained'
    def constrained(self):
        return [key for key, attr in self.vertices(True) if attr['cx'] or attr['cy'] or attr['cz']]

    def independent_edges(self):
        return [(u, v) for u, v, attr in self.edges(True) if attr['is_ind']]

    # --------------------------------------------------------------------------
    # Identify features of the formdiagram based on geometrical inputs.
    # --------------------------------------------------------------------------

    # rename these functions

    def identify_anchors(self, points=None, anchor_degree=None):
        if not anchor_degree:
            anchor_degree = self.attributes['anchor_degree']
        for key, attr in self.vertices(True):
            attr['is_anchor'] = self.vertex_degree(key) <= anchor_degree
        if points:
            xyz_key = {}
            for key in self.vertices():
                gkey = geometric_key(self.vertex_coordinates(key))
                xyz_key[gkey] = key
            for xyz in points:
                gkey = geometric_key(xyz)
                if gkey in xyz_key:
                    key = xyz_key[gkey]
                    self.vertex[key]['is_anchor'] = True

    def identify_prescribed(self, points=None):
        if points:
            xyz_key = {}
            for key in self.vertices():
                gkey = geometric_key(self.vertex_coordinates(key))
                xyz_key[gkey] = key
            for xyz in points:
                gkey = geometric_key(xyz)
                if gkey in xyz_key:
                    key = xyz_key[gkey]
                    self.vertex[key]['is_prescribed'] = True

    def identify_fixed(self, points=None):
        if points:
            xyz_key = {}
            for key in self.vertices():
                gkey = geometric_key(self.vertex_coordinates(key))
                xyz_key[gkey] = key
            for xyz in points:
                gkey = geometric_key(xyz)
                if gkey in xyz_key:
                    key = xyz_key[gkey]
                    self.vertex[key]['is_fixed'] = True

    def identify_constraints(self, points=None):
        if points:
            xyz_key = {}
            for key in self.vertices():
                gkey = geometric_key(self.vertex_coordinates(key))
                xyz_key[gkey] = key
            for xyz in points:
                gkey = geometric_key(xyz)
                if gkey in xyz_key:
                    key = xyz_key[gkey]
                    self.vertex[key]['cx'] = 1.0
                    self.vertex[key]['cy'] = 1.0

    def identify_loads(self):
        pass

    def identify_open_edges(self):
        pass

    def identify_holes(self):
        pass

    def identify_creases(self):
        pass


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import compas
    from compas.topology import network_find_faces

    form = FormDiagram.from_obj(compas.get('open_edges.obj'))

    network_find_faces(form, form.breakpoints())

    form.delete_face(0)

    print(form.faces_on_boundary())

