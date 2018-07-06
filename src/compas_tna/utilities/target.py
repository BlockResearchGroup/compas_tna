from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

try:
    from numpy import hstack
    from numpy import take
    from numpy import einsum

    from scipy.interpolate import griddata
    from scipy.spatial.qhull import Delaunay

except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = ['update_target', ]


def update_target(heightfield, samples):
    hf_xy = heightfield[:, 0:2]
    hf_z  = heightfield[:, 2]
    s_xy  = samples[:, 0:2]
    t_z   = griddata(hf_xy, hf_z, s_xy, method='linear', fill_value=0.0).reshape((-1, 1))
    return t_z


# # not working yet
# # -> don't use this function
# def create_target_updater(xyz, uvw):
#     """Improvement over griddata implementation of scipy as described on SO.
#     see: http://stackoverflow.com/questions/20915502/
#     speedup-scipy-griddata-for-multiple-interpolations-between-two-irregular-grids
#     """
#     tri = Delaunay(xyz)
#     simplex = tri.find_simplex(uvw)
#     vertices = take(tri.simplices, simplex, axis=0)
#     temp = take(tri.transform, simplex, axis=0)
#     delta = uvw - temp[:, 3]
#     bary = einsum('njk, nk->nj', temp[:, :3, :], delta)
#     weights = hstack((bary, 1 - bary.sum(axis=1, keepdims=True)))

#     def updater(V):
#         return einsum('nj, nj->n', take(V, vertices), weights)
#     return updater


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
