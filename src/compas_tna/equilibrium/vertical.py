from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

try:
    from numpy import array
    from numpy import float64
    from numpy import zeros
    from numpy import diagflat
    from numpy import absolute
    from numpy import reciprocal
    from numpy import vstack
    from numpy import hstack

    from scipy.linalg import norm
    from scipy.linalg import solve
    from scipy.sparse import diags
    from scipy.sparse.linalg import spsolve

except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise

import compas
import compas_tna

from compas.utilities import XFunc

from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import normrow

from compas_tna.utilities import LoadUpdater
from compas_tna.utilities import update_z
from compas_tna.utilities import update_q_from_qind


__author__  = 'Tom Van Mele'
__email__   = 'vanmelet@ethz.ch'


__all__ = [
    'vertical_from_zmax',
    'vertical_from_target',
    'vertical_from_bbox',
    'vertical_from_q',
    'vertical_from_qind',

    'vertical_from_zmax_xfunc',
    'vertical_from_target_xfunc',
    'vertical_from_bbox_xfunc',
    'vertical_from_q_xfunc',

    'vertical_from_zmax_rhino',
    'vertical_from_target_rhino',
    'vertical_from_bbox_rhino',
    'vertical_from_q_rhino',
]


EPS = 1 / sys.float_info.epsilon


def vertical_from_zmax_rhino(form, *args, **kwargs):
    import compas_rhino

    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.vertical_from_zmax_xfunc')
    f.tmpdir = compas_tna.TEMP
    f.callback = callback
    formdata, scale = f(form.to_data(), *args, **kwargs)
    form.data = formdata

    return scale


def vertical_from_target_rhino(form, *args, **kwargs):
    import compas_rhino

    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.vertical_from_target_xfunc')
    f.tmpdir = compas_tna.TEMP
    f.callback = callback
    formdata, scale = f(form.to_data(), *args, **kwargs)
    form.data = formdata

    return scale


def vertical_from_bbox_rhino(form, *args, **kwargs):
    import compas_rhino

    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.vertical_from_bbox_xfunc')
    f.tmpdir = compas_tna.TEMP
    f.callback = callback
    formdata, scale = f(form.to_data(), *args, **kwargs)
    form.data = formdata

    return scale


def vertical_from_q_rhino(form, *args, **kwargs):
    import compas_rhino

    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.vertical_from_q_xfunc')
    f.tmpdir = compas_tna.TEMP
    f.callback = callback
    formdata = f(form.to_data(), *args, **kwargs)
    form.data = formdata


def vertical_from_zmax_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    scale = vertical_from_zmax(form, *args, **kwargs)
    return form.to_data(), scale


def vertical_from_target_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    scale = vertical_from_target(form, *args, **kwargs)
    return form.to_data(), scale


def vertical_from_bbox_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    scale = vertical_from_bbox(form, *args, **kwargs)
    return form.to_data(), scale


def vertical_from_q_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    vertical_from_q(form, *args, **kwargs)
    return form.to_data()


def vertical_from_zmax(form, zmax, kmax=100, xtol=1e-2, rtol=1e-3, density=1.0, display=True):
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

    """
    xtol2 = xtol ** 2
    # --------------------------------------------------------------------------
    # FormDiagram
    # --------------------------------------------------------------------------
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = len(form.vertex)
    anchors = list(form.anchors())
    fixed   = list(form.fixed())
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    free    = list(set(range(vcount)) - set(fixed))
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    q       = [attr.get('q', 1.0) for u, v, attr in form.edges_where({'is_edge': True}, True)]
    q       = array(q, dtype=float64).reshape((-1, 1))
    C       = connectivity_matrix(edges, 'csr')
    Ci      = C[:, free]
    Cf      = C[:, fixed]
    Cit     = Ci.transpose()
    Ct      = C.transpose()
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

        q            = scale * q0
        Q            = diags([q.ravel()], [0])
        A            = Cit.dot(Q).dot(Ci)
        b            = p[free, 2] - Cit.dot(Q).dot(Cf).dot(xyz[fixed, 2])
        xyz[free, 2] = spsolve(A, b)
        z            = max(xyz[free, 2])
        res2         = (z - zmax) ** 2

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
    l  = normrow(C.dot(xyz))
    f  = q * l
    r  = Ct.dot(Q).dot(C).dot(xyz) - p
    sw = p - p0
    # --------------------------------------------------------------------------
    # form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]

    return scale


def vertical_from_target(form, density=1.0):
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = len(form.vertex)
    anchors = list(form.anchors())
    fixed   = list(form.fixed())
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    free    = list(set(range(vcount)) - set(fixed))
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    q       = [attr.get('q', 1.0) for u, v, attr in form.edges_where({'is_edge': True}, True)]
    q       = array(q, dtype=float64).reshape((-1, 1))
    C       = connectivity_matrix(edges, 'csr')
    Ci      = C[:, free]
    Cf      = C[:, fixed]
    Cit     = Ci.transpose()
    Ct      = C.transpose()
    # --------------------------------------------------------------------------
    # original data
    # --------------------------------------------------------------------------
    p0 = array(p, copy=True)
    q0 = array(q, copy=True)
    # --------------------------------------------------------------------------
    # target
    # --------------------------------------------------------------------------
    zT = array(form.get_vertices_attribute('zT'), dtype=float64).reshape((-1, 1))
    xyz[:, 2] = zT[:, 0]
    # --------------------------------------------------------------------------
    # load updater
    # --------------------------------------------------------------------------
    update_loads = LoadUpdater(form, p0, thickness=thick, density=1.0)
    update_loads(p, xyz)
    # --------------------------------------------------------------------------
    # scale
    # to bestfit of target geometry
    # --------------------------------------------------------------------------
    n      = vcount
    ni     = len(free)
    eye_n0 = diagflat([1] * n + [0])
    nul_ni = zeros((ni, ni))
    Q      = diags([q.flatten()], [0])
    A      = Cit.dot(Q).dot(C)
    pzi    = p[free, 2].reshape((-1, 1))
    Aeq    = hstack((A.toarray(), pzi))
    beq    = zeros((ni, 1))
    Ceq    = vstack((hstack((eye_n0, Aeq.T)),
                     hstack((Aeq, nul_ni))))
    deq    = vstack((zT,
                     zeros((1, 1)),
                     beq))
    res    = solve(Ceq.T.dot(Ceq), Ceq.T.dot(deq))
    scale  = absolute(reciprocal(res[n][0]))
    # --------------------------------------------------------------------------
    # vertical
    # --------------------------------------------------------------------------
    q  = scale * q0
    Q  = diags([q.flatten()], [0])

    A            = Cit.dot(Q).dot(Ci)
    b            = p[free, 2] - Cit.dot(Q).dot(Cf).dot(xyz[fixed, 2])
    xyz[free, 2] = spsolve(A, b)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    l  = normrow(C.dot(xyz))
    f  = q * l
    r  = Ct.dot(Q).dot(C).dot(xyz) - p
    sw = p - p0
    # --------------------------------------------------------------------------
    # form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]

    return scale


def vertical_from_bbox(form, factor, kmax=100, tol=1e-3, density=1.0, display=True):
    # --------------------------------------------------------------------------
    # FormDiagram
    # --------------------------------------------------------------------------
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = len(form.vertex)
    anchors = list(form.anchors())
    fixed   = list(form.fixed())
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    free    = list(set(range(vcount)) - set(fixed))
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    q       = [attr.get('q', 1.0) for u, v, attr in form.edges_where({'is_edge': True}, True)]
    q       = array(q, dtype=float64).reshape((-1, 1))
    C       = connectivity_matrix(edges, 'csr')
    Ci      = C[:, free]
    Cf      = C[:, fixed]
    Cit     = Ci.transpose()
    Ct      = C.transpose()
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
    # scale
    # --------------------------------------------------------------------------
    (xmin, ymin, zmin), (xmax, ymax, zmax) = form.bbox()
    d = ((xmax - xmin) ** 2 + (ymax - ymin) ** 2) ** 0.5
    scale = d * factor
    # --------------------------------------------------------------------------
    # vertical
    # --------------------------------------------------------------------------
    q = scale * q0
    Q = diags([q.ravel()], [0])
    update_z(xyz, Q, C, p, free, fixed, update_loads, tol=tol, kmax=kmax, display=display)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    l  = normrow(C.dot(xyz))
    f  = q * l
    r  = Ct.dot(Q).dot(C).dot(xyz) - p
    sw = p - p0
    # --------------------------------------------------------------------------
    # form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]

    return scale


def vertical_from_qind(form, scale=1.0, density=1.0, kmax=100, tol=1e-3, display=True):
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = form.number_of_vertices()
    anchors = list(form.anchors())
    fixed   = list(form.fixed())
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    ecount  = len(edges)
    ind     = [index for index, (u, v, attr) in enumerate(form.edges_where({'is_edge': True}, True)) if attr['is_ind']]
    dep     = list(set(range(ecount)) - set(ind))
    free    = list(set(range(vcount)) - set(fixed))
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    q       = [attr.get('q', 1.0) for u, v, attr in form.edges_where({'is_edge': True}, True)]
    q       = array(q, dtype=float64).reshape((-1, 1))
    C       = connectivity_matrix(edges, 'csr')
    E       = equilibrium_matrix(C, xyz[:, 0:2], free, 'csr')
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
    # update forcedensity based on given q[ind]
    # --------------------------------------------------------------------------
    update_q_from_qind(E, q0, dep, ind)
    q = scale * q0
    Q = diags([q.ravel()], [0])
    # --------------------------------------------------------------------------
    # compute vertical
    # --------------------------------------------------------------------------
    update_z(xyz, Q, C, p, free, fixed, update_loads, tol=tol, kmax=kmax, display=display)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    l  = normrow(C.dot(xyz))
    f  = q * l
    r  = C.transpose().dot(Q).dot(C).dot(xyz) - p
    sw = p - p0
    # --------------------------------------------------------------------------
    # form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['q'] = q0[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


def vertical_from_q(form, scale=1.0, density=1.0, kmax=100, tol=1e-3, display=True):
    """Compute vertical equilibrium from the force densities of the independent edges.

    Parameters
    ----------
    form (compas_tna.diagrams.formdiagram.FormDiagram):
        The form diagram
    scale : float
        The scale of the horizontal forces.
        Default is ``1.0``.
    density : float, optional
        The density for computation of the self-weight of the thrust network.
        Set this to 0.0 to ignore self-weight and only consider specified point loads.
        Default is ``1.0``.
    kmax : int, optional
        The maximum number of iterations for computing vertical equilibrium.
        Default is ``100``.
    tol : float
        The stopping criterion.
        Default is ``0.001``.
    display : bool
        Display information about the current iteration.
        Default is ``True``.

    """
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = form.number_of_vertices()
    anchors = list(form.anchors())
    fixed   = list(form.fixed())
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    free    = list(set(range(vcount)) - set(fixed))
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    q       = [attr.get('q', 1.0) for u, v, attr in form.edges_where({'is_edge': True}, True)]
    q       = array(q, dtype=float64).reshape((-1, 1))
    C       = connectivity_matrix(edges, 'csr')
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
    # update forcedensity based on given q[ind]
    # --------------------------------------------------------------------------
    q = scale * q0
    Q = diags([q.ravel()], [0])
    # --------------------------------------------------------------------------
    # compute vertical
    # --------------------------------------------------------------------------
    update_z(xyz, Q, C, p, free, fixed, update_loads, tol=tol, kmax=kmax, display=display)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    l  = normrow(C.dot(xyz))
    f  = q * l
    r  = C.transpose().dot(Q).dot(C).dot(xyz) - p
    sw = p - p0
    # --------------------------------------------------------------------------
    # form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
