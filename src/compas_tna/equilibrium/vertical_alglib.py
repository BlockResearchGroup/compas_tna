from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from copy import deepcopy

from compas.geometry import cross_vectors
from compas.geometry import length_vector
from compas.geometry import centroid_points
from compas.geometry import norm_vector

from compas_tna.equilibrium._alglib._core import xalglib


__all__ = ['vertical_from_q_alglib']


def vertical_from_q_alglib(form, scale=1.0, density=1.0, kmax=100, tol=1e-3):
    """"""
    key_index = form.key_index()
    xyz = form.vertices_attributes('xyz')
    loads = form.vertices_attributes(('px', 'py', 'pz'))
    n = form.number_of_vertices()
    fixed = list(set(list(form.anchors()) + list(form.fixed())))
    free = list(set(range(n)) - set(fixed))
    ni = len(free)
    nf = len(fixed)
    xyzf = [xyz[i] for i in fixed]
    selfweight = selfweight_calculator(form, density=density)
    adjacency = {}
    for key in form.vertices():
        nbrs = form.vertex_neighbors(key)
        adj = [key_index[nbr] for nbr in nbrs if form.edge_attribute((key, nbr), '_is_edge')]
        adjacency[key_index[key]] = adj
    ij_q = {uv: scale * form.edge_attribute(uv, 'q', 1.0) for uv in form.edges_where({'_is_edge': True})}
    ij_q.update({(v, u): q for (u, v), q in ij_q.items()})
    ij_q = {(key_index[u], key_index[v]): ij_q[u, v] for u, v in ij_q}
    nonzero_fixed, nonzero_free = nonzero(adjacency, fixed, free)
    CtQC = xalglib.sparsecreate(n, n)
    CitQCi = xalglib.sparsecreate(ni, ni)
    CitQCf = xalglib.sparsecreate(ni, nf)
    solver = xalglib.linlsqrcreate(ni, ni)
    update_matrices(adjacency, free, nonzero_fixed, nonzero_free, CtQC, CitQCf, CitQCi, ij_q)
    update_z(solver, xyz, xyzf, free, CtQC, CitQCf, CitQCi, selfweight=selfweight, kmax=kmax, tol=tol)
    p = deepcopy(loads)
    sw = selfweight(xyz)
    for i in range(len(p)):
        p[i][2] -= sw[i]
    rx, ry, rz = compute_residuals(xyz, p, n, CtQC)
    for key in form.vertices():
        index = key_index[key]
        form.vertex_attributes(key, 'xyz', xyz[index])
        form.vertex_attributes(key, 'rx', rx[index])
        form.vertex_attributes(key, 'ry', ry[index])
        form.vertex_attributes(key, 'rz', rz[index])
    for u, v in form.edges():
        l = form.edge_length(u, v)
        f = q * l
        form.edge_attributes((u, v), ('f', 'l'), (f, l))


# ==============================================================================
# helpers
# ==============================================================================


def selfweight_calculator(form, density=1.0):
    key_index = form.key_index()
    sw = [0] * form.number_of_vertices()
    rho = [attr['t'] * density for key, attr in form.vertices(True)]
    def calculate_selfweight(xyz):
        fkey_centroid = {fkey: form.face_centroid(fkey) for fkey in form.faces() if form.face_attribute(fkey, '_is_loaded')}
        for u in form.vertices():
            i = key_index[u]
            p0 = xyz[i]
            area = 0
            for v in form.halfedge[u]:
                j = key_index[v]
                p01 = subtract_vectors(xyz[j], p0)
                fkey = form.halfedge[u][v]
                if fkey in fkey_centroid:
                    p02 = subtract_vectors(fkey_centroid[fkey], p0)
                    area += length_vector(cross_vectors(p01, p02))
                fkey = form.halfedge[v][u]
                if fkey in fkey_centroid:
                    p03 = subtract_vectors(fkey_centroid[fkey], p0)
                    area += length_vector(cross_vectors(p01, p03))
            sw[i] = 0.25 * area * rho[i]
        return sw
    return calculate_selfweight


def nonzero(adjacency, fixed, free):
    n = len(adjacency)
    j_col_free = {value: index for index, value in enumerate(free)}
    j_col_fixed = {value: index for index, value in enumerate(fixed)}
    i_nonzero_free = {i: [] for i in range(n)}
    i_nonzero_fixed = {i: [] for i in range(n)}
    fixed = set(fixed)
    for i in range(n):
        if i in fixed:
            i_nonzero_fixed[i].append((i, j_col_fixed[i]))
        else:
            i_nonzero_free[i].append((i, j_col_free[i]))
        for j in adjacency[i]:
            if j in fixed:
                i_nonzero_fixed[i].append((j, j_col_fixed[j]))
            else:
                i_nonzero_free[i].append((j, j_col_free[j]))
    return i_nonzero_fixed, i_nonzero_free


def update_matrices(adjacency, free, nonzero_fixed, nonzero_free, CtQC, CitQCf, CitQCi, ij_q):
    xalglib.sparseconverttohash(CtQC)
    xalglib.sparseconverttohash(CitQCi)
    xalglib.sparseconverttohash(CitQCf)
    n = len(adjacency)
    ni = len(free)
    for i in range(n):
        Q = 0
        for j in adjacency[i]:
            q = ij_q[(i, j)]
            Q += q
            xalglib.sparseset(CtQC, i, j, -q)
        xalglib.sparseset(CtQC, i, i, Q)
    for row in range(ni):
        i = free[row]
        for j, col in nonzero_fixed[i]:
            xalglib.sparseset(CitQCf, row, col, xalglib.sparseget(CtQC, i, j))
        for j, col in nonzero_free[i]:
            xalglib.sparseset(CitQCi, row, col, xalglib.sparseget(CtQC, i, j))


def update_z(solver, xyz, xyzf, free, CtQC, CitQCf, CitQCi, selfweight, tol=1e-3, kmax=100):
    # solve A.x = b
    # with A = CitQCi
    #      b = pzi - CitQCf.zf
    #      x = zi
    xalglib.sparseconverttocrs(CitQCi)
    xalglib.sparseconverttocrs(CitQCf)
    xalglib.sparseconverttocrs(CtQC)
    n = len(xyz)
    ni = len(free)
    z = [z for _, _, z in xyz]
    zf = [z for _, _, z in xyzf]
    A = CitQCi
    b_ = xalglib.sparsemv(CitQCf, zf, [0] * ni)
    out = [0] * n
    for k in range(kmax):
        sw = selfweight(xyz)
        b = [- sw[i][2] - b_[i] for i in range(ni)]
        xalglib.linlsqrsolvesparse(solver, A, b)
        zi, _ = xalglib.linlsqrresults(solver)
        for i in range(ni):
            z[free[i]] = zi[i]
        rz = xalglib.sparsemv(CtQC, z, out)
        rz = [- sw[i][2] - rz[i] for i in range(n)]
        residual = norm([rz[free[i]] for i in range(ni)])
        if residual < tol:
            break
    for i in range(ni):
        xyz[free[i]][2] = zi[i]
    return residual


def compute_residuals(xyz, p, n, CtQC):
    # residual = CtQC.xyz - p
    xalglib.sparseconverttocrs(CtQC)
    x, y, z = zip(*xyz)
    x = list(x)
    y = list(y)
    z = list(z)
    out = [0] * n
    rx = xalglib.sparsemv(CtQC, x, out)
    rx = [p[i][0] - rx[i] for i in range(n)]
    ry = xalglib.sparsemv(CtQC, y, out)
    ry = [p[i][1] - ry[i] for i in range(n)]
    rz = xalglib.sparsemv(CtQC, z, out)
    rz = [p[i][2] - rz[i] for i in range(n)]
    return rx, ry, rz


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
