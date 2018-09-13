from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from compas.geometry import scale_vector_xy
from compas.geometry import subtract_vectors_xy
from compas.geometry import length_vector_xy

from compas.plotters import MeshPlotter
from compas.plotters import draw_xlines_xy


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['FormViewer', ]


class FormViewer(MeshPlotter):

    def __init__(self, form, *args, **kwargs):
        super(FormViewer, self).__init__(form, *args, **kwargs)

    @property
    def form(self):
        return self.mesh

    def draw_reactions(self, scale=1.0, color='#00ff00', width=1.0):
        lines = []

        for key, attr in self.form.vertices_where({'is_anchor': True}, True):
            nbrs = self.form.vertex_neighbors(key)

            rx = attr['rx']
            ry = attr['ry']
            rz = attr['rz']

            for nbr in nbrs:
                is_external = self.form.get_edge_attribute((key, nbr), 'is_external', False)

                if is_external:
                    f = self.form.get_edge_attribute((key, nbr), 'f', 0.0)
                    u = self.form.edge_direction(key, nbr)
                    v = scale_vector_xy(u, f)

                    rx += v[0]
                    ry += v[1]

            sp = self.form.vertex_coordinates(key, 'xy')
            ep = sp[0] + scale * rx, sp[1] + scale * ry

            lines.append({
                'start' : sp,
                'end'   : ep,
                'color' : color,
                'width' : width,
            })

        draw_xlines_xy(lines, self.axes)

    def draw_forces(self, scale=1.0, alpha=0.5):
        lines = []

        for u, v, attr in self.form.edges_where({'is_edge': True, 'is_external': False}, True):
            sp, ep = self.form.edge_coordinates(u, v)

            f = attr['f']
            width = scale * f

            lines.append({
                'start' : sp,
                'end'   : ep,
                'color' : '#0000ff',
                'width' : width,
            })

        draw_xlines_xy(lines, self.axes, alpha=alpha)

    def draw_horizontalforces(self, scale=1.0, alpha=0.5):
        lines = []

        for u, v, attr in self.form.edges_where({'is_edge': True, 'is_external': False}, True):
            sp, ep = self.form.edge_coordinates(u, v)

            q = attr['q']
            v = subtract_vectors_xy(ep, sp)
            l = length_vector_xy(v)
            f = q * l
            width = scale * f

            lines.append({
                'start' : sp,
                'end'   : ep,
                'color' : '#0000ff',
                'width' : width,
            })

        draw_xlines_xy(lines, self.axes, alpha=alpha)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
