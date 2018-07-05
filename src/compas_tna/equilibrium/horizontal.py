from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from numpy import array
from numpy import float64

from compas.geometry import angle_vectors_xy

from compas.numerical import connectivity_matrix
from compas.numerical import normrow
from compas.numerical import normalizerow

from compas_tna.utilities import rot90
from compas_tna.utilities import apply_bounds
from compas_tna.utilities import parallelise_sparse
from compas_tna.utilities import parallelise_nodal


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = [
    'horizontal',
    'horizontal_nodal',
]


EPS = 1 / sys.float_info.epsilon


def horizontal(form, force, alpha=100.0, kmax=100, display=True):
    r"""Compute horizontal equilibrium.

    This implementation is based on the following formulation

    .. math::

        \mathbf{C}^{T} \mathbf{C} \mathbf{xy} = \mathbf{C}^{T} \mathbf{t}

    with :math:`\mathbf{C}` the connectivity matrix and :math:`\mathbf{t}` the
    target vectors.


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

    """
    # --------------------------------------------------------------------------
    # alpha == 1 : form diagram fixed
    # alpha == 0 : force diagram fixed
    # --------------------------------------------------------------------------
    alpha = max(0., min(1., float(alpha) / 100.0))
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i   = form.key_index()
    uv_i  = form.uv_index()
    fixed = set(form.anchors() + form.fixed())  # do something about this!
    fixed = [k_i[key] for key in fixed]
    edges = [[k_i[u], k_i[v]] for u, v in form.edges_where({'is_edge': True})]
    xy    = array(form.get_vertices_attributes('xy'), dtype=float64)
    lmin  = array(form.get_edges_attribute('lmin', 1e-7, where={'is_edge': True}), dtype=float64).reshape((-1, 1))
    lmax  = array(form.get_edges_attribute('lmax', 1e+7, where={'is_edge': True}), dtype=float64).reshape((-1, 1))
    C     = connectivity_matrix(edges, 'csr')
    Ct    = C.transpose()
    CtC   = Ct.dot(C)
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _k_i   = force.key_index()
    _fixed = force.fixed()
    _fixed = [_k_i[key] for key in _fixed]
    _fixed = _fixed or [0]
    _edges = force.ordered_edges(form)
    _xy    = array(force.get_vertices_attributes('xy'), dtype=float64)
    _lmin  = array(force.get_edges_attribute('lmin', 1e-7), dtype=float64).reshape((-1, 1))
    _lmax  = array(force.get_edges_attribute('lmax', 1e+7), dtype=float64).reshape((-1, 1))
    _C     = connectivity_matrix(_edges, 'csr')
    _Ct    = _C.transpose()
    _Ct_C  = _Ct.dot(_C)
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
    uv  = C.dot(xy)
    _uv = _C.dot(_xy)
    l   = normrow(uv)
    _l  = normrow(_uv)
    t   = alpha * normalizerow(uv) + (1 - alpha) * normalizerow(_uv)
    # parallelise
    for k in range(kmax):
        # apply length bounds
        apply_bounds(l, lmin, lmax)
        apply_bounds(_l, _lmin, _lmax)
        # print, if allowed
        if display:
            print(k)
        if alpha != 1.0:
            # if emphasis is not entirely on the form
            # update the form diagram
            xy = parallelise_sparse(CtC, Ct.dot(l * t), xy, fixed, 'CtC')
            uv = C.dot(xy)
            l  = normrow(uv)
        if alpha != 0.0:
            # if emphasis is not entirely on the force
            # update the force diagram
            _xy = parallelise_sparse(_Ct_C, _Ct.dot(_l * t), _xy, _fixed, '_Ct_C')
            _uv = _C.dot(_xy)
            _l  = normrow(_uv)
    # --------------------------------------------------------------------------
    # compute the force densities
    # --------------------------------------------------------------------------
    q = (_l / l).astype(float64)
    # --------------------------------------------------------------------------
    # rotate the force diagram 90 degrees in CW direction
    # this way the relation between the two diagrams is easier to read
    # --------------------------------------------------------------------------
    _xy[:] = rot90(_xy, -1.0)
    # --------------------------------------------------------------------------
    # angle deviations
    # note that this does not account for flipped edges!
    # --------------------------------------------------------------------------
    a = [angle_vectors_xy(uv[i], _uv[i]) for i in range(len(edges))]
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        i = k_i[key]
        attr['x'] = xy[i, 0]
        attr['y'] = xy[i, 1]
    for u, v, attr in form.edges_where({'is_edge': True}):
        i = uv_i[(u, v)]
        attr['q'] = q[i, 0]
        attr['a'] = a[i]
    # --------------------------------------------------------------------------
    # update force
    # --------------------------------------------------------------------------
    for key, attr in force.vertices(True):
        i = _k_i[key]
        attr['x'] = _xy[i, 0]
        attr['y'] = _xy[i, 1]


# this is experimental!
def horizontal_nodal(form, force, alpha=100, kmax=100, display=True):
    """Compute horizontal equilibrium using a node-per-node approach.

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

    """
    alpha = float(alpha) / 100.0
    alpha = max(0., min(1., alpha))
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i    = form.key_index()
    uv_i   = form.uv_index()
    i_nbrs = {k_i[key]: [k_i[nbr] for nbr in form.vertex_neighbours(key)] for key in form.vertices()}
    ij_e   = {(k_i[u], k_i[v]): index for (u, v), index in iter(uv_i.items())}
    fixed  = set(form.anchors() + form.fixed())  # do something about this!
    fixed  = [k_i[key] for key in fixed]
    edges  = [[k_i[u], k_i[v]] for u, v in form.edges_where({'is_edge': True})]
    xy     = array(form.get_vertices_attributes('xy'), dtype=float64)
    C      = connectivity_matrix(edges, 'csr')
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _k_i    = force.key_index()
    _uv_i   = force.uv_index(form=form)
    _i_nbrs = {_k_i[key]: [_k_i[nbr] for nbr in force.vertex_neighbours(key)] for key in force.vertices()}
    _ij_e   = {(_k_i[u], _k_i[v]): index for (u, v), index in iter(_uv_i.items())}
    _fixed  = force.fixed()
    _fixed  = [_k_i[key] for key in _fixed]
    _fixed  = _fixed or [0]
    _edges  = force.ordered_edges(form)
    _xy     = array(force.get_vertices_attributes('xy'), dtype=float64)
    _C      = connectivity_matrix(_edges, 'csr')
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
    uv  = C.dot(xy)
    _uv = _C.dot(_xy)
    l   = normrow(uv)
    _l  = normrow(_uv)
    # --------------------------------------------------------------------------
    # the target vectors
    # --------------------------------------------------------------------------
    targets = alpha * normalizerow(uv) + (1 - alpha) * normalizerow(_uv)
    # --------------------------------------------------------------------------
    # parallelise
    # --------------------------------------------------------------------------
    parallelise_nodal(xy, C, targets, i_nbrs, ij_e, fixed=fixed, kmax=kmax)
    parallelise_nodal(_xy, _C, targets, _i_nbrs, _ij_e, kmax=kmax)
    # --------------------------------------------------------------------------
    # update the coordinate difference vectors
    # --------------------------------------------------------------------------
    uv  = C.dot(xy)
    _uv = _C.dot(_xy)
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
    a = [angle_vectors_xy(uv[i], _uv[i]) for i in range(len(edges))]
    # --------------------------------------------------------------------------
    # update form
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        i = k_i[key]
        attr['x'] = xy[i, 0]
        attr['y'] = xy[i, 1]
    for u, v in form.edges_where({'is_edge': True}):
        attr = form.edgedata[u, v]
        i = uv_i[(u, v)]
        attr['q'] = q[i, 0]
        attr['a'] = a[i]
    # --------------------------------------------------------------------------
    # update force
    # --------------------------------------------------------------------------
    for key, attr in force.vertices(True):
        i = _k_i[key]
        attr['x'] = _xy[i, 0]
        attr['y'] = _xy[i, 1]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    from compas.numerical import fd_numpy
    from compas.plotters import MeshPlotter
    from compas.utilities import pairwise

    from compas_tna.diagrams import FormDiagram
    from compas_tna.diagrams import ForceDiagram
    from compas_tna.equilibrium import horizontal_nodal

    form = FormDiagram.from_obj(compas.get('faces.obj'))

    for key in form.vertices_where({'vertex_degree': 2}):
        form.vertex[key]['is_anchor'] = True

    boundary = form.vertices_on_boundary(ordered=True)

    unsupported = [[]]
    for key in boundary:
        unsupported[-1].append(key)
        if form.vertex[key]['is_anchor']:
            unsupported.append([key])

    unsupported[-1] += unsupported[0]
    del unsupported[0]

    for vertices in unsupported:
        for u, v in pairwise(vertices):
            form.set_edge_attribute((u, v), 'q', 10)

    for vertices in unsupported:
        fkey = form.add_face(vertices, is_unloaded=True)

    for vertices in unsupported:
        u = vertices[-1]
        v = vertices[0]
        form.set_edge_attribute((u, v), 'is_edge', False)

    vertices = form.get_vertices_attributes('xyz')
    edges = list(form.edges_where({'is_edge': True}))
    fixed = list(form.vertices_where({'is_anchor': True}))
    qs = [form.get_edge_attribute(uv, 'q') for uv in edges]
    loads = form.get_vertices_attributes(('px', 'py', 'pz'), (0, 0, 0))

    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, qs, loads)

    for key, attr in form.vertices(True):
        attr['x'] = xyz[key][0]
        attr['y'] = xyz[key][1]
        attr['z'] = xyz[key][2]

    force = ForceDiagram.from_formdiagram(form)

    horizontal_nodal(form, force)

    plotter = MeshPlotter(force)
    plotter.draw_vertices(text='key')
    plotter.draw_faces()
    plotter.draw_edges(text={(u, v): "{:.2f}".format(force.edge_length(u, v)) for u, v in force.edges()})
    plotter.show()
