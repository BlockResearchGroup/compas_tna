from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from compas.geometry import scale_vector

from compas_rhino import MeshArtist


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['FormArtist', ]


class FormArtist(MeshArtist):

    @property
    def form(self):
        return self.datastructure

    def clear(self):
        super(FormArtist, self).clear()
        self.clear_loads()
        self.clear_selfweight()
        self.clear_reactions()
        self.clear_forces()

    def clear_loads(self):
        compas_rhino.delete_objects_by_name(name='{}.load.*'.format(self.form.name))

    def clear_selfweight(self):
        compas_rhino.delete_objects_by_name(name='{}.selfweight.*'.format(self.form.name))

    def clear_reactions(self):
        compas_rhino.delete_objects_by_name(name='{}.reaction.*'.format(self.form.name))

    def clear_forces(self):
        compas_rhino.delete_objects_by_name(name='{}.force.*'.format(self.form.name))

    def draw_loads(self, scale=None, color=None):
        self.clear_loads()

        lines = []
        color = color or self.form.attributes['color.load']
        scale = scale or self.form.attributes['scale.load']

        for key, attr in self.form.vertices_where({'is_anchor': False, 'is_external': False}, True):
            px = attr['px']
            py = attr['py']
            pz = attr['pz']
            sp = self.form.vertex_coordinates(key)
            ep = sp[0] + scale * px, sp[1] + scale * py, sp[2] + scale * pz

            lines.append({
                'start' : sp,
                'end'   : ep,
                'color' : color,
                'width' : width,
                'arrow' : 'end',
                'name'  : "{}.load.{}".format(self.form.name, key)
            })

        compas_rhino.xdraw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_selfweight(self, scale=None, color=None):
        self.clear_selfweight()

        lines = []
        color = color or self.form.attributes['color.selfweight']
        scale = scale or self.form.attributes['scale.selfweight']

        for key, attr in self.form.vertices_where({'is_anchor': False, 'is_external': False}, True):
            t = attr['t']
            a = self.form.vertex_area(key)
            sp = self.form.vertex_coordinates(key)
            ep = sp[0], sp[1], sp[2] + scale * t * a

            lines.append({
                'start' : sp,
                'end'   : ep,
                'color' : color,
                'width' : width,
                'arrow' : 'end',
                'name'  : "{}.selfweight.{}".format(self.form.name, key)
            })

        compas_rhino.xdraw_lines(lines, layer=self.layer, clear=False, redraw=False)        

    def draw_reactions(self, scale=None, color=None):
        self.clear_reactions()

        lines = []
        color = color or self.form.attributes['color.reaction']
        scale = scale or self.form.attributes['scale.reaction']

        for key, attr in self.form.vertices_where({'is_anchor': True}, True):
            rx = attr['rx']
            ry = attr['ry']
            rz = attr['rz']

            for nbr in self.form.vertex_neighbours(key):
                is_external = self.form.get_edge_attribute((key, nbr), 'is_external', False)

                if is_external:
                    f = self.form.get_edge_attribute((key, nbr), 'f', 0.0)
                    u = self.form.edge_direction(key, nbr)
                    u[2] = 0
                    v = scale_vector(u, f)

                    rx += v[0]
                    ry += v[1]

            sp = self.form.vertex_coordinates(key)
            e1 = sp[0] + scale * rx, sp[1] + scale * ry, sp[2]
            e2 = sp[0], sp[1], sp[2] + scale * rz

            lines.append({
                'start' : sp,
                'end'   : e1,
                'color' : color,
                'width' : width,
                'arrow' : 'start',
                'name'  : "{}.reaction.{}".format(self.form.name, key)
            })

            lines.append({
                'start' : sp,
                'end'   : e2,
                'color' : color,
                'width' : width,
                'arrow' : 'start',
                'name'  : "{}.reaction.{}".format(self.form.name, key)
            })

        compas_rhino.xdraw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_forces(self):
        self.clear_forces()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
