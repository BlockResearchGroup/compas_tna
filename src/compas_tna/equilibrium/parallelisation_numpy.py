import sys

from numpy.linalg import cond
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.linalg import lstsq
from scipy.sparse.linalg import factorized

from compas.linalg import chofactor
from compas.linalg import lufactorized
from compas.linalg import normrow

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
