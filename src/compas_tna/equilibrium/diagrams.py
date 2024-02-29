import sys

from numpy import empty_like
from numpy.linalg import cond
from scipy.linalg import lstsq
from scipy.linalg import norm
from scipy.linalg import solve
from scipy.sparse.linalg import factorized

from compas.linalg import dof
from compas.linalg import nonpivots
from compas.linalg import rref
from compas.matrices import connectivity_matrix
from compas.matrices import equilibrium_matrix

EPS = 1 / sys.float_info.epsilon


def rot90(xy, zdir=1.0):
    temp = empty_like(xy)
    temp[:, 0] = -zdir * xy[:, 1]
    temp[:, 1] = +zdir * xy[:, 0]
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


def form_count_dof(form):
    """Count the DOF of the FormDiagram.

    Parameters
    ----------
    form : :class:`compas_tna.diagrams.FormDiagram`

    Returns
    -------
    int

    """
    k2i = form.vertex_index()
    xyz = form.vertices_attributes("xyz")
    fixed = [k2i[key] for key in form.supports()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(k2i[u], k2i[v]) for u, v in form.edges_where({"_is_edge": True})]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xyz, free)
    return dof(E)


def form_identify_dof(form, **kwargs):
    algo = kwargs.get("algo") or "sympy"
    k2i = form.vertex_index()
    xyz = form.vertices_attributes("xyz")
    fixed = [k2i[key] for key in form.supports()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(k2i[u], k2i[v]) for u, v in form.edges_where({"_is_edge": True})]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xyz, free)
    return nonpivots(rref(E, algo=algo))
