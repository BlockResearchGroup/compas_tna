from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import array
from scipy.interpolate import griddata


__all__ = ['distribute_thickness']


def distribute_thickness(formdiagram):
    """Distribute thickness by interpolating provided values over the vertex grid."""
    points = []
    values = []
    xi = []
    index_key = {}
    index = 0
    for key in formdiagram.vertices():
        t = formdiagram.vertex_attribute(key, 't')
        xy = formdiagram.vertex_attributes(key, 'xy')
        if t:
            points.append(xy)
            values.append(t)
        else:
            xi.append(xy)
            index_key[index] = key
            index += 1
    points = array(points)
    values = array(values)
    xi = array(xi)
    t = griddata(points, values, xi, method='linear')
    t = t.flatten().tolist()
    for index, value in enumerate(t):
        key = index_key[index]
        formdiagram.vertex_attribute(key, 't', value)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
