import sys

import numpy.typing as npt
from numpy.linalg import cond
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.linalg import lstsq
from scipy.sparse.linalg import factorized

from compas.linalg import lufactorized
from compas.linalg import normrow

EPS = 1 / sys.float_info.epsilon


def parallelise(A: npt.NDArray, x: npt.NDArray, b: npt.NDArray, known: list[int]) -> npt.NDArray:
    r"""Solve a system of linear equations with part of solution known.

    Parameters
    ----------
    A : array
        Coefficient matrix represented as an (m x n) array.
    b : array
        Right-hand-side represented as an (m x 1) array.
    x : array
        Unknowns/knowns represented as an (n x 1) array.
    known : list
        The indices of the known elements of ``x``.

    Returns
    -------
    array: (n x 1) vector solution.

    Notes
    -----
    Computes the solution of the system of linear equations.

    .. math::

        \mathbf{A} \mathbf{x} = \mathbf{b}

    Examples
    --------
    >>> C = connectivity_matrix(form)
    >>> Q = diags([form.q()], [0])
    >>> xy = form.xy()
    >>> uv = C.dot(xy)
    >>> C_dual = connectivity_matrix(force)
    >>> xy_dual = force.xy()
    >>> known_dual = [index for index, vertex in enumerate(force.vertices()) if force.vertex_attribute(vertex, "is_fixed")]
    >>> parallelise(C_dual.T.dot(C_dual), C_dual.T.dot(Q).dot(uv), xy_dual, known_dual)

    """
    unknown = list(set(range(x.shape[0])) - set(known))
    A11 = A[unknown, :][:, unknown]
    A12 = A[unknown, :][:, known]
    b = b[unknown] - A12.dot(x[known])
    if cond(A11) < EPS:
        x[unknown] = cho_solve(cho_factor(A11), b)
        return x
    x[unknown] = lstsq(A11, b)[0]  # type: ignore
    return x


def parallelise_sparse(A, B, X, known, k=1, key=None):
    unknown = list(set(range(X.shape[0])) - set(known))
    A11 = A[unknown, :][:, unknown]
    A12 = A[unknown, :][:, known]
    b = B[unknown] - A12.dot(X[known])
    if key:
        Y = lufactorized(A11, key)(b)
    else:
        Y = factorized(A11)(b)
    X[unknown] = Y
    return X


def parallelise_nodal(xy, C, targets, i_nbrs, ij_e, fixed=None, kmax=100, lmin=None, lmax=None):
    fixed = fixed or []
    fixed = set(fixed)

    n = xy.shape[0]

    for k in range(kmax):
        xy0 = xy.copy()
        uv = C.dot(xy)
        l = normrow(uv)  # noqa: E741

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

        for i, j in ij_e:
            e = ij_e[(i, j)]

            if l[e, 0] == 0.0:
                a = xy[i]
                b = xy[j]
                c = 0.5 * (a + b)
                xy[i] = c[:]
                xy[j] = c[:]


def apply_bounds(x, xmin, xmax):
    xsmall = x < xmin
    xbig = x > xmax
    x[xsmall] = xmin[xsmall]
    x[xbig] = xmax[xbig]
