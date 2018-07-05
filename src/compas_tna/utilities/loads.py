from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import array
from numpy import zeros

from compas.geometry import centroid_points
from compas.geometry import length_vector
from compas.geometry import cross_vectors


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = ['LoadUpdater', ]


class LoadUpdater(object):
    """"""
    def __init__(self, network, p0, thickness=1.0, density=1.0, live=0.0):
        self.network = network
        self.p0 = p0
        self.thickness = thickness
        self.density = density
        self.live = live
        self.is_unloaded = {fkey: network.get_face_attribute(fkey, 'is_unloaded') for fkey in network.face}
        self.key_index = {key: index for index, key in enumerate(self.network.vertices())}

    def __call__(self, p, xyz):
        ta = self._tributary_areas(xyz)
        sw = ta * self.thickness * self.density + ta * self.live
        p[:, 2] = self.p0[:, 2] + sw[:, 0]
        return p

    # centroid can be calculated much faster
    # using a face-vertex incidence matrix
    def _tributary_areas(self, xyz):
        network = self.network
        is_unloaded = self.is_unloaded
        key_index = self.key_index
        fkey_centroid = {}
        for fkey in network.faces():
            vertices = network.face_vertices(fkey)
            if is_unloaded[fkey]:
                continue
            fkey_centroid[fkey] = array(centroid_points([xyz[key_index[key]] for key in set(vertices)]))
        areas = zeros((xyz.shape[0], 1))
        for u in network.vertices():
            p0 = xyz[key_index[u]]
            a = 0
            for v in network.halfedge[u]:
                p1  = xyz[key_index[v]]
                p01 = p1 - p0
                fkey = network.halfedge[u][v]
                if fkey in fkey_centroid:
                    p2 = fkey_centroid[fkey]
                    a += 0.25 * length_vector(cross_vectors(p01, p2 - p0))
                fkey = network.halfedge[v][u]
                if fkey in fkey_centroid:
                    p3 = fkey_centroid[fkey]
                    a += 0.25 * length_vector(cross_vectors(p01, p3 - p0))
            areas[key_index[u]] = a
        return areas


# def create_load_updater(network, p0, thickness=1.0, density=1.0, live=0.0, is_unloaded=None):
#     key_index = dict((key, index) for index, key in network.vertices_enum())
#     def tributary_areas(network, xyz):
#         fkey_centroid = {}
#         for fkey, vertices in network.face.iteritems():
#             if is_unloaded[fkey]:
#                 continue
#             fkey_centroid[fkey] = array(centroid([xyz[key_index[key]] for key in set(vertices)]))
#         areas = zeros((xyz.shape[0], 1))
#         for u in network.vertex.iterkeys():
#             p0 = xyz[key_index[u]]
#             a = 0
#             for v in network.halfedge[u]:
#                 p1  = xyz[key_index[v]]
#                 p01 = p1 - p0
#                 fkey = network.halfedge[u][v]
#                 if fkey in fkey_centroid:
#                     p2 = fkey_centroid[fkey]
#                     a += 0.25 * length(cross(p01, p2 - p0))
#                 fkey = network.halfedge[v][u]
#                 if fkey in fkey_centroid:
#                     p3 = fkey_centroid[fkey]
#                     a += 0.25 * length(cross(p01, p3 - p0))
#             areas[key_index[u]] = a
#         return areas
#     def updater(p, xyz):
#         ta = tributary_areas(network, xyz)
#         sw = ta * thickness * density + ta * live
#         p[:, 2] = p0[:, 2] + sw[:, 0]
#         return p
#     return updater


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
