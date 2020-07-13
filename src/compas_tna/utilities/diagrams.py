from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from numpy import empty_like
from numpy.linalg import cond

from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.linalg import lstsq
from scipy.linalg import solve
from scipy.linalg import norm

from scipy.sparse.linalg import factorized

from compas.numerical import connectivity_matrix
from compas.numerical import normrow
from compas.numerical import chofactor
from compas.numerical import lufactorized
from compas.numerical import dof
from compas.numerical import rref
from compas.numerical import nonpivots
from compas.numerical import equilibrium_matrix


__all__ = [
    'parallelise',
    'parallelise_sparse',
    'parallelise_nodal',
    'rot90',
    'apply_bounds',
    'update_z',
    'update_q_from_qind',
    'form_count_dof',
    'form_identify_dof',
]


EPS = 1 / sys.float_info.epsilon


def parallelise(A, B, X, known, k=1, key=None):
    unknown = list(set(range(X.shape[0])) - set(known))
    A11 = A[unknown, :][:, unknown]
    A12 = A[unknown, :][:, known]
    b = B[unknown] - A12.dot(X[known])
    if cond(A11) < EPS:
        if key:
            Y = cho_solve(chofactor(A11, key), b)
        else:
            Y = cho_solve(cho_factor(A11), b)
        X[unknown] = Y
        return X
    Y = lstsq(A11, b)
    Y = Y[0]
    X[unknown] = Y
    return X


def parallelise_sparse(A, B, X, known, k=1, key=None):
    unknown = list(set(range(X.shape[0])) - set(known))
    A11 = A[unknown, :][:, unknown]
    A12 = A[unknown, :][:, known]
    b = B[unknown] - A12.dot(X[known])
    if key:
        solve = lufactorized(A11, key)
        Y = solve(b)
    else:
        solve = factorized(A11)
        Y = solve(b)
    X[unknown] = Y
    return X


def parallelise_nodal(xy, C, targets, i_nbrs, ij_e, fixed=None, kmax=100, lmin=None, lmax=None):
    fixed = fixed or []
    fixed = set(fixed)

    n = xy.shape[0]

    for k in range(kmax):
        xy0 = xy.copy()
        uv = C.dot(xy)
        l = normrow(uv)

        if lmin is not None and lmax is not None:
            apply_bounds(l, lmin, lmax)

        for j in range(n):
            if j in fixed:
                continue

            nbrs = i_nbrs[j]
            xy[j, :] = 0.0

            for i in nbrs:
                if (i, j) in ij_e:
                    e = ij_e[(i, j)]
                    t = targets[e]
                elif (j, i) in ij_e:
                    e = ij_e[(j, i)]
                    t = -targets[e]
                else:
                    continue

                xy[j] += xy0[i] + l[e, 0] * t

            # add damping factor?
            xy[j] /= len(nbrs)

        for (i, j) in ij_e:
            e = ij_e[(i, j)]

            if l[e, 0] == 0.0:
                a = xy[i]
                b = xy[j]
                c = 0.5 * (a + b)
                xy[i] = c[:]
                xy[j] = c[:]


def rot90(xy, zdir=1.0):
    temp = empty_like(xy)
    temp[:, 0] = - zdir * xy[:, 1]
    temp[:, 1] = + zdir * xy[:, 0]
    return temp


def apply_bounds(x, xmin, xmax):
    xsmall = x < xmin
    xbig = x > xmax
    x[xsmall] = xmin[xsmall]
    x[xbig] = xmax[xbig]


def update_z(xyz, Q, C, p, free, fixed, updateloads, tol=1e-3, kmax=100, display=False):
    Ci = C[:, free]
    Cf = C[:, fixed]
    Ct = C.transpose()
    Cit = Ci.transpose()
    A = Cit.dot(Q).dot(Ci)
    A_solve = factorized(A)
    B = Cit.dot(Q).dot(Cf)
    CtQC = Ct.dot(Q).dot(C)

    updateloads(p, xyz)

    for k in range(kmax):
        if display:
            print(k)

        xyz[free, 2] = A_solve(p[free, 2] - B.dot(xyz[fixed, 2]))

        updateloads(p, xyz)

        r = CtQC.dot(xyz[:, 2]) - p[:, 2]
        residual = norm(r[free])

        if residual < tol:
            break

    return residual


def update_q_from_qind(E, q, dep, ind):
    """Update the full set of force densities using the values of the independent edges.

    Parameters
    ----------
    E : sparse csr matrix
        The equilibrium matrix.
    q : array
        The force densities of the edges.
    dep : list
        The indices of the dependent edges.
    ind : list
        The indices of the independent edges.

    Returns
    -------
    None
        The force densities are modified in-place.

    Examples
    --------
    >>>

    """
    m = E.shape[0] - len(dep)
    qi = q[ind]
    Ei = E[:, ind]
    Ed = E[:, dep]
    if m > 0:
        Edt = Ed.transpose()
        A = Edt.dot(Ed).toarray()
        b = Edt.dot(Ei).dot(qi)
    else:
        A = Ed.toarray()
        b = Ei.dot(qi)
    if cond(A) > EPS:
        res = lstsq(-A, b)
        qd = res[0]
    else:
        qd = solve(-A, b)
    q[dep] = qd


# ==============================================================================
# Form Diagram Functions
# ==============================================================================


def form_count_dof(form):
    k2i = form.key_index()
    xyz = form.vertices_attributes('xyz')
    fixed = [k2i[key] for key in form.anchors()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(k2i[u], k2i[v]) for u, v in form.edges_where({'_is_edge': True})]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xyz, free)
    return dof(E)


def form_identify_dof(form, **kwargs):
    algo = kwargs.get('algo') or 'sympy'
    k2i = form.key_index()
    xyz = form.vertices_attributes('xyz')
    fixed = [k2i[key] for key in form.anchors()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(k2i[u], k2i[v]) for u, v in form.edges_where({'_is_edge': True})]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xyz, free)
    return nonpivots(rref(E, algo=algo))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
