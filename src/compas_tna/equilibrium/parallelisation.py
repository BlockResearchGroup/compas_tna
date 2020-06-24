from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import midpoint_point_point_xy


__all__ = [
    'parallelise_edges',
]


def parallelise_edges(xy, edges, targets, i_nbrs, ij_e, fixed=None, kmax=100, lmin=None, lmax=None, callback=None):
    """Parallelise the edges of a mesh to given target vectors.

    Parameters
    ----------
    mesh : mesh
        The mesh object.
    targets : list
        A list of target vectors.
    fixed : list, optional
        The fixed nodes of the mesh.
        Default is ``None``.
    kmax : int, optional
        Maximum number of iterations.
        Default is ``1``.
    callback : callable, optional
        A user-defined callback function to be executed after every iteration.
        Default is ``None``.

    Returns
    -------
    None

    Examples
    --------
    >>>
    """
    if callback:
        if not callable(callback):
            raise Exception('The provided callback is not callable.')

    fixed = fixed or []
    fixed = set(fixed)

    n = len(xy)

    for k in range(kmax):
        xy0 = [[x, y] for x, y in xy]
        uv = [[xy[j][0] - xy[i][0], xy[j][1] - xy[i][1]] for i, j in edges]
        lengths = [(dx**2 + dy**2)**0.5 for dx, dy in uv]

        if lmin:
            lengths[:] = [max(a, b) for a, b in zip(lengths, lmin)]

        if lmax:
            lengths[:] = [min(a, b) for a, b in zip(lengths, lmax)]

        for j in range(n):
            if j in fixed:
                continue

            nbrs = i_nbrs[j]
            x, y = 0.0, 0.0

            for i in nbrs:
                ax, ay = xy0[i]

                if (i, j) in ij_e:
                    e = ij_e[(i, j)]
                    l = lengths[e]  # noqa: E741
                    tx, ty = targets[e]
                    x += ax + l * tx
                    y += ay + l * ty

                else:
                    e = ij_e[(j, i)]
                    l = lengths[e]  # noqa: E741
                    tx, ty = targets[e]
                    x += ax - l * tx
                    y += ay - l * ty

            xy[j][0] = x / len(nbrs)
            xy[j][1] = y / len(nbrs)

        for (i, j) in ij_e:
            e = ij_e[(i, j)]

            if lengths[e] == 0.0:
                c = midpoint_point_point_xy(xy[i], xy[j])
                xy[i][:] = c[:]
                xy[j][:] = c[:]

        if callback:
            callback(k, xy)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    import doctest
    doctest.testmod(globs=globals())
