from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import array
from scipy.interpolate import griddata


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = ['distribute', ]


def distribute(formdiagram, config=None):
    points = []
    values = []
    xi     = []
    index_key = dict()
    index = 0
    for key, attr in formdiagram.vertices_iter(True):
        if attr['t']:
            points.append((attr['x'], attr['y']))
            values.append(attr['t'])
        else:
            xi.append((attr['x'], attr['y']))
            index_key[index] = key
            index += 1
    points = array(points)
    values = array(values)
    xi = array(xi)
    t = griddata(points, values, xi, method='linear')
    t = t.flatten().tolist()
    for index, value in enumerate(t):
        key = index_key[index]
        formdiagram.vertex[key]['t'] = value


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
