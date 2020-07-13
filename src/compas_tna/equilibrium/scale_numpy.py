from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from numpy import array
from numpy import float64

from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_tna.utilities import LoadUpdater
from compas_tna.utilities import update_z


__all__ = [
    'scale_from_target',
]


EPS = 1 / sys.float_info.epsilon


def scale_from_target(form, zmax, kmax=100, xtol=1e-2, rtol=1e-3, density=1.0, display=False):
    """For the given form and force diagram, compute the scale of the force
    diagram for which the highest point of the thrust network is equal to a
    specified value.

    Parameters
    ----------
    form : compas_tna.diagrams.formdiagram.FormDiagram
        The form diagram
    force : compas_tna.diagrams.forcediagram.ForceDiagram
        The corresponding force diagram.
    zmax : float
        The maximum height of the thrust network (the default is None, which
        implies that the maximum height will be equal to a quarter of the diagonal
        of the bounding box of the form diagram).
    kmax : int
        The maximum number of iterations for computing vertical equilibrium
        (the default is 100).
    tol : float
        The stopping criterion.
    density : float
        The density for computation of the self-weight of the thrust network
        (the default is 1.0). Set this to 0.0 to ignore self-weight and only
        consider specified point loads.
    display : bool
        If True, information about the current iteration will be displayed.

    Returns
    -------
    float
        The scale of the forcedensities.

    """
    xtol2 = xtol ** 2
    # --------------------------------------------------------------------------
    # FormDiagram
    # --------------------------------------------------------------------------
    k_i = form.key_index()
    uv_i = form.uv_index()
    vcount = len(form.vertex)
    anchors = list(form.anchors())
    fixed = list(form.fixed())
    fixed = set(anchors + fixed)
    fixed = [k_i[key] for key in fixed]
    free = list(set(range(vcount)) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    xyz = array(form.vertices_attributes('xyz'), dtype=float64)
    thick = array(form.vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p = array(form.vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    q = [attr.get('q', 1.0) for key, attr in form.edges_where({'is_edge': True}, True)]
    q = array(q, dtype=float64).reshape((-1, 1))
    C = connectivity_matrix(edges, 'csr')
    Ci = C[:, free]
    Cf = C[:, fixed]
    Cit = Ci.transpose()
    Ct = C.transpose()
    # --------------------------------------------------------------------------
    # original data
    # --------------------------------------------------------------------------
    p0 = array(p, copy=True)
    q0 = array(q, copy=True)
    # --------------------------------------------------------------------------
    # load updater
    # --------------------------------------------------------------------------
    update_loads = LoadUpdater(form, p0, thickness=thick, density=density)
    # --------------------------------------------------------------------------
    # scale to zmax
    # note that zmax should not exceed scale * diagonal
    # --------------------------------------------------------------------------
    scale = 1.0

    for k in range(kmax):
        if display:
            print(k)

        update_loads(p, xyz)

        q = scale * q0
        Q = diags([q.ravel()], [0])
        A = Cit.dot(Q).dot(Ci)
        b = p[free, 2] - Cit.dot(Q).dot(Cf).dot(xyz[fixed, 2])
        xyz[free, 2] = spsolve(A, b)
        z = max(xyz[free, 2])
        res2 = (z - zmax) ** 2

        if res2 < xtol2:
            break

        scale = scale * (z / zmax)
    # --------------------------------------------------------------------------
    # vertical
    # --------------------------------------------------------------------------
    q = scale * q0
    Q = diags([q.ravel()], [0])

    res = update_z(xyz, Q, C, p, free, fixed, update_loads, tol=rtol, kmax=kmax, display=display)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    l = normrow(C.dot(xyz))
    f = q * l
    r = Ct.dot(Q).dot(C).dot(xyz) - p
    # --------------------------------------------------------------------------
    # form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z'] = xyz[index, 2]
        attr['_rx'] = r[index, 0]
        attr['_ry'] = r[index, 1]
        attr['_rz'] = r[index, 2]
    for key, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[key]
        attr['_f'] = f[index, 0]

    return scale


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
