from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import fabs

from compas.plotters.core import draw_xpoints_xy
from compas.plotters.core import draw_xlines_xy
from compas.plotters.core import draw_xarrows_xy
from compas.plotters.core import draw_xlabels_xy

from compas.utilities import color_to_colordict
from compas.utilities import is_color_light

from compas.plotters.core import size_to_sizedict

import matplotlib.pyplot as plt


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class Viewer2(object):
    
    def __init__(self, form, force):
        self.form = form
        self.force = force
        self.defaults = {}

    def show(self):
        plt.show()

    def setup(self):
        self.fig = plt.figure(figsize=(14.4, 9), tight_layout=True)
        self.fig.patch.set_facecolor('white')
        self.ax1 = self.fig.add_subplot('121')
        self.ax2 = self.fig.add_subplot('122')
        self.ax1.set_aspect('equal')
        self.ax2.set_aspect('equal')
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        self.ax1.set_xmargin(1.0)
        self.ax1.set_ymargin(1.0)
        self.ax1.set_xlim(-1.0, 11.0)
        self.ax1.set_ylim(-1.0, 11.0)
        self.ax2.set_xticks([])
        self.ax2.set_yticks([])
        self.ax2.set_xmargin(1.0)
        self.ax2.set_ymargin(1.0)
        self.ax2.set_xlim(-1.0, 11.0)
        self.ax2.set_ylim(-1.0, 11.0)
        self.ax1.axis('off')
        self.ax2.axis('off')

    def draw_form(self,
                  vertices_on=True,
                  edges_on=True,
                  faces_on=False,
                  forces_on=True,
                  arrows_on=True,
                  vertexcolor=None,
                  edgecolor=None,
                  facecolor=None,
                  edgelabel=None,
                  vertexlabel=None,
                  facelabel=None,
                  vertexsize=None,
                  forcescale=1.0,
                  lines=None,
                  points=None):

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        facelabel   = facelabel or {}
        vertexsize  = size_to_sizedict(vertexsize, self.form.vertices(), self.default_vertexsize)
        vertexcolor = color_to_colordict(vertexcolor, self.form.vertices(), self.default_vertexcolor)
        edgecolor   = color_to_colordict(edgecolor, self.form.edges_where(), self.default_edgecolor)
        facecolor   = color_to_colordict(facecolor, self.form.faces_where(), self.default_facecolor)

        x = self.form.get_vertices_attribute('x')
        y = self.form.get_vertices_attribute('y')

        if lines:
            x += [line['start'][0] for line in lines]
            x += [line['end'][0] for line in lines]
            y += [line['start'][1] for line in lines]
            y += [line['end'][1] for line in lines]

        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)
        dx, dy = -xmin, -ymin
        scale  = max(fabs(xmax - xmin) / 10.0, fabs(ymax - ymin) / 10.0)

        if vertices_on:
            _points = []
            for key, attr in self.form.vertices(True):
                bgcolor = vertexcolor[key]
                _points.append({
                    'pos'       : [(attr['x'] + dx) / scale, (attr['y'] + dy) / scale],
                    'radius'    : vertexsize[key],
                    'facecolor' : vertexcolor[key],
                    'edgecolor' : self.default_edgecolor,
                    'linewidth' : self.default_edgewidth * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default_fontsize,
                })
            draw_xpoints_xy(_points, self.ax1)


    def draw_force(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    viewer = Viewer2(None, None)
    viewer.setup()
    viewer.show()
