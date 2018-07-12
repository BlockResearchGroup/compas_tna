from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

try:
    from numpy import array
    from numpy import float64
    from scipy.sparse.linalg import spsolve
    from scipy.sparse import diags

except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise

from compas.utilities import XFunc

from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import normrow

from compas_tna.utilities import LoadUpdater

from compas_tna.utilities import update_z
from compas_tna.utilities import update_q_from_qind


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = [
    'vertical_from_zmax',
    'vertical_from_formforce',
    'vertical_from_qind',
    'vertical_from_zmax_xfunc',
    'vertical_from_formforce_xfunc',
    'vertical_from_qind_xfunc',
    'vertical_from_zmax_rhino'
]


EPS = 1 / sys.float_info.epsilon


def vertical_from_zmax_xfunc(formdata, forcedata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    from compas_tna.diagrams import ForceDiagram
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    vertical_from_zmax(form, force, *args, **kwargs)
    return form.to_data(), force.to_data()


def vertical_from_formforce_xfunc(formdata, forcedata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    from compas_tna.diagrams import ForceDiagram
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    vertical_from_formforce(form, force, *args, **kwargs)
    return form.to_data(), force.to_data()


def vertical_from_qind_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    vertical_from_qind(form, *args, **kwargs)
    return form.to_data()


def vertical_from_zmax_rhino(form, force, *args, **kwargs):
    import compas_rhino

    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.vertical_from_zmax_xfunc', callback=callback)
    formdata, forcedata = f(form.to_data(), force.to_data(), *args, **kwargs)
    form.data = formdata
    force.data = forcedata


def vertical_from_zmax(form, force, zmax=None, kmax=100, tol=1e-6, density=1.0, display=True):
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
    tol2 = tol ** 2
    if not zmax:
        # use the bounding box for this
        # aligned?
        x = form.get_vertices_attribute('x')
        y = form.get_vertices_attribute('y')
        xmin = min(x)
        ymin = min(y)
        xmax = max(x)
        ymax = max(y)
        d = ((xmax - xmin) ** 2 + (ymax - ymin) ** 2) ** 0.5
        zmax = 0.25 * d
    # --------------------------------------------------------------------------
    # FormDiagram
    # --------------------------------------------------------------------------
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = len(form.vertex)
    anchors = form.anchors()
    fixed   = form.fixed()
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    free    = list(set(range(vcount)) - set(fixed))
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    p0      = p.copy()
    C       = connectivity_matrix(edges, 'csr')
    Ci      = C[:, free]
    Cf      = C[:, fixed]
    Cit     = Ci.transpose()
    Ct      = C.transpose()
    # --------------------------------------------------------------------------
    # ForceDiagram
    # --------------------------------------------------------------------------
    _xyz   = array(force.get_vertices_attributes('xyz'), dtype=float64)
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')
    # --------------------------------------------------------------------------
    # load updater
    # --------------------------------------------------------------------------
    update_loads = LoadUpdater(form, p0, thickness=thick, density=density)
    # --------------------------------------------------------------------------
    # lengths
    # --------------------------------------------------------------------------
    uv  = C.dot(xyz[:, 0:2])
    _uv = _C.dot(_xyz[:, 0:2])
    l    = normrow(uv)
    _l   = normrow(_uv)
    # --------------------------------------------------------------------------
    # scale to zmax
    # note that zmax should not exceed scale * diagonal
    # --------------------------------------------------------------------------
    scale = 1.0
    for k in range(kmax):
        if display:
            print(k)
        if k < kmax - 1:
            update_loads(p, xyz)
        h            = scale * _l
        q            = h / l
        Q            = diags([q.ravel()], [0])
        A            = Cit.dot(Q).dot(Ci)
        b            = p[free, 2] - Cit.dot(Q).dot(Cf).dot(xyz[fixed, 2])
        xyz[free, 2] = spsolve(A, b)
        z     = max(xyz[free, 2])
        scale = scale * (z / zmax)
        # res2  = (z - zmax) ** 2
        # if res2 < tol2:
        #     break
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    uvw = C.dot(xyz)
    l   = normrow(uvw)
    f   = q * l
    r   = Ct.dot(Q).dot(C).dot(xyz) - p
    sw  = p - p0

    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]
    # --------------------------------------------------------------------------
    # update force
    # --------------------------------------------------------------------------
    force.attributes['scale'] = scale


def vertical_from_formforce(form, force, kmax=100, tol=1e-6, density=1.0, display=True):
    """For the given form and force diagram, compute the thrust network.

    Parameters
    ----------
    form : compas_tna.diagrams.formdiagram.FormDiagram
        The form diagram
    force : compas_tna.diagrams.forcediagram.ForceDiagram
        The corresponding force diagram.
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
    # --------------------------------------------------------------------------
    # FormDiagram
    # --------------------------------------------------------------------------
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = form.number_of_vertices()
    anchors = form.anchors()
    fixed   = form.fixed()
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    free    = list(set(range(vcount)) - set(fixed))
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    p0      = p.copy()
    C       = connectivity_matrix(edges, 'csr')
    # --------------------------------------------------------------------------
    # ForceDiagram
    # --------------------------------------------------------------------------
    scale = force.attributes['scale']
    _xyz   = array(force.get_vertices_attributes('xyz'), dtype=float64)
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')
    # --------------------------------------------------------------------------
    # load updater
    # --------------------------------------------------------------------------
    update_loads = LoadUpdater(form, p0, thickness=thick, density=density)
    # --------------------------------------------------------------------------
    # compute forcedensity
    # --------------------------------------------------------------------------
    uv  = C.dot(xyz[:, 0:2])
    _uv = _C.dot(_xyz[:, 0:2])
    l    = normrow(uv)
    _l   = normrow(_uv)
    h    = scale * _l
    q    = h / l
    Q    = diags([q.ravel()], [0])
    # --------------------------------------------------------------------------
    # compute vertical
    # --------------------------------------------------------------------------
    update_z(xyz, Q, C, p, free, fixed, update_loads, tol=tol, kmax=kmax, display=display)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    uvw = C.dot(xyz)
    l   = normrow(uvw)
    f   = q * l
    r   = C.transpose().dot(Q).dot(C).dot(xyz) - p
    sw  = p - p0
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


def vertical_from_qind(form, ind, m, density=1.0, kmax=100, tol=1e-6, display=True):
    """Compute vertical equilibrium from the force densities of the independent edges.

    Parameters:
        form (compas_tna.diagrams.formdiagram.FormDiagram):
            The form diagram
        ind (int):
            The indices of the independent form edges. Should be identified
            using ForceDiagram.dof
        m (int):
            Should be identified using ForceDiagram.dof
        density (float):
            The density for computation of the self-weight of the thrust network
            (the default is 1.0). Set this to 0.0 to ignore self-weight and only
            consider specified point loads.
        kmax (int):
            The maximum number of iterations for computing vertical equilibrium
            (the default is 100).
        tol (float):
            The stopping criterion.
        display (bool):
            If True, information about the current iteration will be displayed.

    References:
        Pellegrino and Calladine, Matrix Analysis of statically and kinematically
        indeterminate frameworks. International Journal of Solids Structures 1986:22(4):409-28.

    """
    k_i     = form.key_index()
    uv_i    = form.uv_index()
    vcount  = form.number_of_vertices()
    anchors = form.anchors()
    fixed   = form.fixed()
    fixed   = set(anchors + fixed)
    fixed   = [k_i[key] for key in fixed]
    free    = list(set(range(vcount)) - set(fixed))
    dep     = list(set(range(ecount)) - set(ind))
    edges   = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    ecount  = len(edges)
    xyz     = array(form.get_vertices_attributes('xyz'), dtype=float64)
    thick   = array(form.get_vertices_attribute('t'), dtype=float64).reshape((-1, 1))
    p       = array(form.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    p0      = p.copy()
    q       = array(form.get_edges_attribute('q', where={'is_edge': True}), dtype=float64).reshape((-1, 1))
    C       = connectivity_matrix(edges, 'csr')
    E       = equilibrium_matrix(C, xyz[:, 0:2], free, 'csr')
    # --------------------------------------------------------------------------
    # load updater
    # --------------------------------------------------------------------------
    update_loads = LoadUpdater(form, p0, thickness=thick, density=density)
    # --------------------------------------------------------------------------
    # update forcedensity based on given q[ind]
    # --------------------------------------------------------------------------
    update_q_from_qind(q, E, ind, dep, m)
    Q = diags([q.ravel()], [0])
    # --------------------------------------------------------------------------
    # compute vertical
    # --------------------------------------------------------------------------
    update_z(xyz, Q, C, p, free, fixed, update_loads, tol=tol, kmax=kmax, display=display)
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    uvw = C.dot(xyz)
    l   = normrow(uvw)
    f   = q * l
    r   = C.transpose().dot(Q).dot(C).dot(xyz) - p
    sw  = p - p0
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = sw[index, 2]
    for u, v, attr in form.edges_where({'is_edge': True}, True):
        index = uv_i[(u, v)]
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
