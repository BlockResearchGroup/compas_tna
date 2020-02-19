from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import angle_vectors_xy

from numpy import array
from numpy import float64

from compas.numerical import connectivity_matrix
from compas.numerical import normrow
from compas.numerical import normalizerow

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.utilities import rot90
from compas_tna.utilities import apply_bounds
from compas_tna.utilities import parallelise_sparse
from compas_tna.utilities import parallelise_nodal


__all__ = [
    'horizontal',
    'horizontal_nodal',
    'horizontal_proxy',
    'horizontal_nodal_proxy'
]


def horizontal_proxy(formdata, forcedata, *args, **kwargs):
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    horizontal(form, force, *args, **kwargs)
    return form.to_data(), force.to_data()


def horizontal_nodal_proxy(formdata, forcedata, *args, **kwargs):
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    horizontal_nodal(form, force, *args, **kwargs)
    return form.to_data(), force.to_data()


def horizontal(form, force, alpha=100.0, kmax=100, display=True):
    r"""Compute horizontal equilibrium.

    Parameters
    ----------
    form : compas_tna.diagrams.formdiagram.FormDiagram
    force : compas_tna.diagrams.forcediagram.ForceDiagram
    alpha : float
        Weighting factor for computation of the target vectors (the default is
        100.0, which implies that the target vectors are the edges of the form diagram).
        If 0.0, the target vectors are the edges of the force diagram.
    kmax : int
       Maximum number of iterations (the default is 100).
    display : bool
        Display information about the current iteration (the default is True).

    Notes
    -----
    This implementation is based on the following formulation

    .. math::

        \mathbf{C}^{T} \mathbf{C} \mathbf{xy} = \mathbf{C}^{T} \mathbf{t}

    with :math:`\mathbf{C}` the connectivity matrix and :math:`\mathbf{t}` the
    target vectors.

    """
    # --------------------------------------------------------------------------
    # alpha == 1 : form diagram fixed
    # alpha == 0 : force diagram fixed
    # --------------------------------------------------------------------------
    alpha = max(0., min(1., float(alpha) / 100.0))
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i = form.key_index()
    uv_i = form.uv_index()
    fixed = set(list(form.anchors()) + list(form.fixed()))
    fixed = [k_i[key] for key in fixed]
    edges = [[k_i[u], k_i[v]] for u, v in form.edges_where({'is_edge': True})]
    xy = array(form.vertices_attributes('xy'), dtype=float64)
    lmin = array([attr.get('lmin', 1e-7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    lmax = array([attr.get('lmax', 1e+7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    fmin = array([attr.get('fmin', 1e-7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    fmax = array([attr.get('fmax', 1e+7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    C = connectivity_matrix(edges, 'csr')
    Ct = C.transpose()
    CtC = Ct.dot(C)

    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _k_i = force.key_index()
    _uv_i = force.uv_index(form=form)
    _fixed = list(force.fixed())
    _fixed = [_k_i[key] for key in _fixed]
    _fixed = _fixed or [0]
    _edges = force.ordered_edges(form)
    _xy = array(force.vertices_attributes('xy'), dtype=float64)
    _C = connectivity_matrix(_edges, 'csr')
    _Ct = _C.transpose()
    _Ct_C = _Ct.dot(_C)

    # --------------------------------------------------------------------------
    # rotate force diagram to make it parallel to the form diagram
    # use CCW direction (opposite of cycle direction)
    # --------------------------------------------------------------------------
    _xy[:] = rot90(_xy, +1.0)
    # --------------------------------------------------------------------------
    # make the diagrams parallel to a target vector
    # that is the (alpha) weighted average of the directions of corresponding
    # edges of the two diagrams
    # --------------------------------------------------------------------------
    uv = C.dot(xy)
    _uv = _C.dot(_xy)
    l = normrow(uv)
    _l = normrow(_uv)
    t = alpha * normalizerow(uv) + (1 - alpha) * normalizerow(_uv)
    # parallelise
    # add the outer loop to the parallelise function
    for k in range(kmax):
        # apply length bounds
        apply_bounds(l, lmin, lmax)
        apply_bounds(_l, fmin, fmax)
        # print, if allowed
        if display:
            print(k)
        if alpha != 1.0:
            # if emphasis is not entirely on the form
            # update the form diagram
            xy = parallelise_sparse(CtC, Ct.dot(l * t), xy, fixed, 'CtC')
            uv = C.dot(xy)
            l = normrow(uv)
        if alpha != 0.0:
            # if emphasis is not entirely on the force
            # update the force diagram
            _xy = parallelise_sparse(_Ct_C, _Ct.dot(_l * t), _xy, _fixed, '_Ct_C')
            _uv = _C.dot(_xy)
            _l = normrow(_uv)
    # --------------------------------------------------------------------------
    # compute the force densities
    # --------------------------------------------------------------------------
    f = _l
    q = (f / l).astype(float64)
    # --------------------------------------------------------------------------
    # rotate the force diagram 90 degrees in CW direction
    # this way the relation between the two diagrams is easier to read
    # --------------------------------------------------------------------------
    _xy[:] = rot90(_xy, -1.0)
    # --------------------------------------------------------------------------
    # angle deviations
    # note that this does not account for flipped edges!
    # --------------------------------------------------------------------------
    a = [angle_vectors_xy(uv[i], _uv[i], deg=True) for i in range(len(edges))]
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        i = k_i[key]
        attr['x'] = xy[i, 0]
        attr['y'] = xy[i, 1]
    for (u, v), attr in form.edges_where({'is_edge': True}, True):
        i = uv_i[(u, v)]
        attr['q'] = q[i, 0]
        attr['f'] = f[i, 0]
        attr['l'] = l[i, 0]
        attr['a'] = a[i]
    # --------------------------------------------------------------------------
    # update force
    # --------------------------------------------------------------------------
    for key, attr in force.vertices(True):
        i = _k_i[key]
        attr['x'] = _xy[i, 0]
        attr['y'] = _xy[i, 1]
    for (u, v), attr in force.edges_where({'is_edge': True}, True):
        i = _uv_i[(u, v)]
        attr['l'] = _l[i, 0]


def horizontal_nodal(form, force, alpha=100, kmax=100, display=True):
    """Compute horizontal equilibrium using a node-per-node approach.

    Parameters
    ----------
    form : compas_tna.diagrams.FormDiagram
    force : compas_tna.diagrams.ForceDiagram
    alpha : float
        Weighting factor for computation of the target vectors (the default is
        100.0, which implies that the target vectors are the edges of the form diagram).
        If 0.0, the target vectors are the edges of the force diagram.
    kmax : int
       Maximum number of iterations (the default is 100).
    display : bool
        Display information about the current iteration (the default is True).

    """
    alpha = float(alpha) / 100.0
    alpha = max(0., min(1., alpha))
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i = form.key_index()
    uv_i = form.uv_index()
    i_nbrs = {k_i[key]: [k_i[nbr] for nbr in form.vertex_neighbors(key)] for key in form.vertices()}
    ij_e = {(k_i[u], k_i[v]): index for (u, v), index in iter(uv_i.items())}
    fixed = set(list(form.anchors()) + list(form.fixed()))
    fixed = [k_i[key] for key in fixed]
    edges = [[k_i[u], k_i[v]] for u, v in form.edges_where({'is_edge': True})]
    lmin = array([attr.get('lmin', 1e-7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    lmax = array([attr.get('lmax', 1e+7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    fmin = array([attr.get('fmin', 1e-7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    fmax = array([attr.get('fmax', 1e+7) for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    flipmask = array([1.0 if not attr['is_tension'] else -1.0 for key, attr in form.edges_where({'is_edge': True}, True)], dtype=float).reshape((-1, 1))
    xy = array(form.vertices_attributes('xy'), dtype=float64)
    C = connectivity_matrix(edges, 'csr')
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _k_i = force.key_index()
    _uv_i = force.uv_index(form=form)
    _i_nbrs = {_k_i[key]: [_k_i[nbr] for nbr in force.vertex_neighbors(key)] for key in force.vertices()}
    _ij_e = {(_k_i[u], _k_i[v]): index for (u, v), index in iter(_uv_i.items())}
    _fixed = list(force.fixed())
    _fixed = [_k_i[key] for key in _fixed]
    _fixed = _fixed or [0]
    _edges = force.ordered_edges(form)
    _xy = array(force.vertices_attributes('xy'), dtype=float64)
    _C = connectivity_matrix(_edges, 'csr')
    # --------------------------------------------------------------------------
    # rotate force diagram to make it parallel to the form diagram
    # use CCW direction (opposite of cycle direction)
    # --------------------------------------------------------------------------
    _xy[:] = rot90(_xy, +1.0)
    # --------------------------------------------------------------------------
    # make the diagrams parallel to a target vector
    # that is the (alpha) weighted average of the directions of corresponding
    # edges of the two diagrams
    # --------------------------------------------------------------------------
    uv = flipmask * C.dot(xy)
    _uv = _C.dot(_xy)
    l = normrow(uv)
    _l = normrow(_uv)
    # --------------------------------------------------------------------------
    # the target vectors
    # --------------------------------------------------------------------------
    targets = alpha * normalizerow(uv) + (1 - alpha) * normalizerow(_uv)
    # --------------------------------------------------------------------------
    # parallelise
    # --------------------------------------------------------------------------
    if alpha < 1:
        parallelise_nodal(xy, C, targets, i_nbrs, ij_e, fixed=fixed, kmax=kmax, lmin=lmin, lmax=lmax)
    if alpha > 0:
        parallelise_nodal(_xy, _C, targets, _i_nbrs, _ij_e, kmax=kmax, lmin=fmin, lmax=fmax)
    # --------------------------------------------------------------------------
    # update the coordinate difference vectors
    # --------------------------------------------------------------------------
    uv = C.dot(xy)
    _uv = _C.dot(_xy)
    l = normrow(uv)
    _l = normrow(_uv)
    # --------------------------------------------------------------------------
    # compute the force densities
    # --------------------------------------------------------------------------
    f = flipmask * _l
    q = (f / l).astype(float64)
    # --------------------------------------------------------------------------
    # rotate the force diagram 90 degrees in CW direction
    # this way the relation between the two diagrams is easier to read
    # --------------------------------------------------------------------------
    _xy[:] = rot90(_xy, -1.0)
    # --------------------------------------------------------------------------
    # angle deviations
    # note that this does not account for flipped edges!
    # --------------------------------------------------------------------------
    a = [angle_vectors_xy(uv[i], _uv[i], deg=True) for i in range(len(edges))]
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        i = k_i[key]
        attr['x'] = xy[i, 0]
        attr['y'] = xy[i, 1]
    for (u, v), attr in form.edges_where({'is_edge': True}, True):
        i = uv_i[(u, v)]
        attr['q'] = q[i, 0]
        attr['f'] = f[i, 0]
        attr['l'] = l[i, 0]
        attr['a'] = a[i]
    # --------------------------------------------------------------------------
    # update force
    # --------------------------------------------------------------------------
    for key, attr in force.vertices(True):
        i = _k_i[key]
        attr['x'] = _xy[i, 0]
        attr['y'] = _xy[i, 1]
    for (u, v), attr in force.edges(True):
        if (u, v) in _uv_i:
            i = _uv_i[(u, v)]
            attr['l'] = _l[i, 0]
        elif (v, u) in _uv_i:
            i = _uv_i[(v, u)]
            attr['l'] = _l[i, 0]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
