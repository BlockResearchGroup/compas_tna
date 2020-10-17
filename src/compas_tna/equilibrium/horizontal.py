from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import angle_vectors_xy
from compas_tna.equilibrium.parallelisation import parallelise_edges


__all__ = [
    'horizontal_nodal',
]


def horizontal_nodal(form, force, alpha=100, kmax=100, callback=None):
    r"""Compute horizontal equilibrium using a node-per-node approach.

    Parameters
    ----------
    form : compas_tna.diagrams.FormDiagram
        The form diagram.
    force : compas_tna.diagrams.ForceDiagram
        The force diagram.
    alpha : float, optional
        Weighting factor for computation of the target vectors (the default is
        100.0, which implies that the target vectors are the edges of the form diagram).
        If 0.0, the target vectors are the edges of the force diagram.
    kmax : int, optional
       Maximum number of iterations.
       Default is ``100``.
    callback : callable, optional
        A callback function to be called at every iteration of the parallelisation algorithm.
        The callback should take the current iterand, the coordinates of the form diagram,
        and the coordinates of the force diagram as input parameters.
        Default is ``None``.

    Returns
    -------
    None

    Notes
    -----
    This function will update the form and force diagram instead of returning a result.
    The relationship between force densities (``q``), horizontal forces (``h``), and lengths (``l``)
    is the following:

    .. math::

        Q_{i} &= \frac{F_{i, thrust}}{L_{i, thrust}} \\
              &= \frac{H_{i, form}}{L_{i, form}} \\
              &= scale * \frac{L_{i, force}}{L_{i, form}}

    """
    alpha = float(alpha) / 100.0
    alpha = max(0, min(1, alpha))
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i = form.key_index()
    i_nbrs = {k_i[key]: [k_i[nbr] for nbr in form.vertex_neighbors(key)] for key in form.vertices()}
    fixed = set(list(form.anchors()) + list(form.fixed()))
    fixed = [k_i[key] for key in fixed]
    xy = form.vertices_attributes('xy')

    edges = list(form.edges_where({'_is_edge': True}))
    uv_i = form.uv_index()
    ij_e = {(k_i[u], k_i[v]): index for (u, v), index in iter(uv_i.items())}
    lmin = form.edges_attribute('lmin', edges=edges)
    lmax = form.edges_attribute('lmax', edges=edges)
    hmin = form.edges_attribute('hmin', edges=edges)
    hmax = form.edges_attribute('hmax', edges=edges)
    edges = [[k_i[u], k_i[v]] for u, v in edges]
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _k_i = force.key_index()
    _i_nbrs = {_k_i[key]: [_k_i[nbr] for nbr in force.vertex_neighbors(key)] for key in force.vertices()}
    _fixed = list(force.fixed())
    _fixed = [_k_i[key] for key in _fixed]
    _xy = force.vertices_attributes('xy')

    _edges = force.ordered_edges(form)
    _uv_i = {uv: index for index, uv in enumerate(_edges)}
    _ij_e = {(_k_i[u], _k_i[v]): index for (u, v), index in iter(_uv_i.items())}
    _lmin = force.edges_attribute('lmin', edges=_edges)
    _lmax = force.edges_attribute('lmax', edges=_edges)
    _edges = [[_k_i[u], _k_i[v]] for u, v in _edges]
    scale = force.attributes.get('scale', 1.0)
    # --------------------------------------------------------------------------
    # rotate force diagram to make it parallel to the form diagram
    # use CCW direction (opposite of cycle direction)
    # --------------------------------------------------------------------------
    _x, _y = zip(*_xy)
    _xy[:] = [list(item) for item in zip([-_ for _ in _y], _x)]
    # --------------------------------------------------------------------------
    # make the diagrams parallel to a target vector
    # that is the (alpha) weighted average of the directions of corresponding
    # edges of the two diagrams
    # --------------------------------------------------------------------------
    uv = [[xy[j][0] - xy[i][0], xy[j][1] - xy[i][1]] for i, j in edges]
    _uv = [[_xy[j][0] - _xy[i][0], _xy[j][1] - _xy[i][1]] for i, j in _edges]
    lengths = [(dx**2 + dy**2)**0.5 for dx, dy in uv]
    forces = [(dx**2 + dy**2)**0.5 for dx, dy in _uv]
    # --------------------------------------------------------------------------
    # the target vectors
    # --------------------------------------------------------------------------
    form_targets = [[alpha * v[0] / l, alpha * v[1] / l] if l else [0, 0] for v, l in zip(uv, lengths)]
    force_targets = [[(1 - alpha) * v[0] / l, (1 - alpha) * v[1] / l] if l else [0, 0] for v, l in zip(_uv, forces)]
    targets = [[a[0] + b[0], a[1] + b[1]] for a, b in zip(form_targets, force_targets)]
    # --------------------------------------------------------------------------
    # proper force bounds
    # --------------------------------------------------------------------------
    hmin[:] = [_ / scale for _ in hmin]
    hmax[:] = [_ / scale for _ in hmax]
    _lmin[:] = [max(a, b) for a, b in zip(hmin, _lmin)]
    _lmax[:] = [min(a, b) for a, b in zip(hmax, _lmax)]
    # --------------------------------------------------------------------------
    # parallelise
    # --------------------------------------------------------------------------
    if alpha < 1:
        parallelise_edges(xy, edges, targets, i_nbrs, ij_e, fixed=fixed, kmax=kmax, lmin=lmin, lmax=lmax)
    if alpha > 0:
        parallelise_edges(_xy, _edges, targets, _i_nbrs, _ij_e, fixed=_fixed, kmax=kmax, lmin=_lmin, lmax=_lmax, callback=callback)
    # --------------------------------------------------------------------------
    # update the coordinate difference vectors
    # --------------------------------------------------------------------------
    uv = [[xy[j][0] - xy[i][0], xy[j][1] - xy[i][1]] for i, j in edges]
    _uv = [[_xy[j][0] - _xy[i][0], _xy[j][1] - _xy[i][1]] for i, j in _edges]
    lengths = [(dx**2 + dy**2)**0.5 for dx, dy in uv]
    forces = [(dx**2 + dy**2)**0.5 for dx, dy in _uv]
    # --------------------------------------------------------------------------
    # compute the force densities
    # --------------------------------------------------------------------------
    q = [f / l for f, l in zip(forces, lengths)]
    # --------------------------------------------------------------------------
    # rotate the force diagram 90 degrees in CW direction
    # this way the relation between the two diagrams is easier to read
    # --------------------------------------------------------------------------
    _x, _y = zip(*_xy)
    _xy[:] = [list(item) for item in zip(_y, [-_ for _ in _x])]
    # --------------------------------------------------------------------------
    # angle deviations
    # note that this does not account for flipped edges!
    # --------------------------------------------------------------------------
    angles = [angle_vectors_xy(uv[i], _uv[i], deg=True) for i in range(len(edges))]
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    for key in form.vertices():
        i = k_i[key]
        form.vertex_attributes(key, 'xy', xy[i])
    for uv in form.edges_where({'_is_edge': True}):
        i = uv_i[uv]
        form.edge_attributes(uv, ['q', '_f', '_l', '_a'], [q[i], forces[i], lengths[i], angles[i]])
    # --------------------------------------------------------------------------
    # update force
    # --------------------------------------------------------------------------
    for key in force.vertices():
        i = _k_i[key]
        force.vertex_attributes(key, 'xy', _xy[i])
    for (u, v) in force.edges():
        if (u, v) in _uv_i:
            i = _uv_i[(u, v)]
        else:
            i = _uv_i[(v, u)]
        force.edge_attributes((u, v), ['_l', '_a'], [forces[i], angles[i]])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
