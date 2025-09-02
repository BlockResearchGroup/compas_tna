import numpy as np
import scipy.sparse as sps

from compas.matrices import connectivity_matrix
from compas_tna.diagrams import FormDiagram


class FormDiagramNumData:
    def __init__(self, formdiagram: FormDiagram):
        self.formdiagram = formdiagram
        self.vertex_index = self.formdiagram.vertex_index()
        self.edge_index = self.formdiagram.uv_index()
        # numerical cache
        self._xyz = None
        self._p = None
        self._t = None
        self._fixed = None
        self._free = None
        self._constrained = None
        self._thickness = None
        self._uv = None
        self._ij = None
        self._C = None
        self._q = None
        self._f = None
        self._r = None

    def update_formdiagram(self):
        for vertex in self.formdiagram.vertices():
            index = self.vertex_index[vertex]
            self.formdiagram.vertex_attribute(vertex, "z", self.xyz[index, 2])
            self.formdiagram.vertex_attributes(vertex, ["_rx", "_ry", "_rz"], self.r[index])

        for edge in self.formdiagram.edges_where({"_is_edge": True}):
            index = self.edge_index[edge]  # type: ignore
            self.formdiagram.edge_attributes(edge, ["q", "_f"], [self.q[index, 0], self.f[index, 0]])

    @property
    def xyz(self):
        if self._xyz is None:
            self._xyz = np.array(self.formdiagram.vertices_attributes("xyz"), dtype=np.float64)
        return self._xyz

    @property
    def p(self):
        if self._p is None:
            self._p = np.array(self.formdiagram.vertices_attributes(("px", "py", "pz")), dtype=np.float64)
        return self._p

    @property
    def t(self):
        if self._t is None:
            self._t = np.array(self.formdiagram.vertices_attribute("t"), dtype=np.float64)
        return self._t

    @property
    def fixed(self):
        if self._fixed is None:
            self._fixed = [self.vertex_index[vertex] for vertex in self.formdiagram.supports()]
        return self._fixed

    @property
    def free(self):
        if self._free is None:
            self._free = list(set(range(self.xyz.shape[0])) - set(self.fixed))
        return self._free

    @property
    def uv(self):
        if self._uv is None:
            self._uv = list(self.formdiagram.edges_where({"_is_edge": True}))
        return self._uv

    @property
    def ij(self):
        if self._ij is None:
            self._ij = [(self.vertex_index[u], self.vertex_index[v]) for u, v in self.uv]
        return self._ij

    @property
    def C(self):
        if self._C is None:
            self._C = connectivity_matrix(self.ij, "csr")
        return self._C

    @property
    def q(self):
        if self._q is None:
            self._q = np.array(self.formdiagram.edges_attribute("q", keys=self.uv), dtype=np.float64).reshape((-1, 1))
        return self._q

    @property
    def f(self):
        if self._f is None:
            self._f = np.zeros_like(self.q)
        return self._f

    @property
    def r(self):
        if self._r is None:
            self._r = np.zeros_like(self.xyz)
        return self._r

    # =============================================================================
    # Not cached
    # =============================================================================

    @property
    def Q(self):
        return sps.diags([self.q.ravel()], [0])  # type: ignore

    @property
    def CitQCi(self):
        pass

    @property
    def CitQCf(self):
        pass

    @property
    def CtQC(self):
        pass
