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


__all__ = ['FormForcePlotter']


# the viewer should hold two instances of the plotter
# with coordinated setup of axes
# => everything you can do with a plotter, you can do for both form and force


class FormForcePlotter(object):
    
    def __init__(self, form, force):
        self.default = {
            'facecolor'          : '#ffffff',
            'edgecolor'          : '#000000',
            'vertexcolor'        : '#ffffff',
            'vertexsize'         : 0.1,
            'edgewidth'          : 1.0,
            'compressioncolor'   : '#0000ff',
            'tensioncolor'       : '#ff0000',
            'externalforcecolor' : '#00ff00',
            'externalforcewidth' : 2.0,
            'textcolor'          : '#000000',
            'fontsize'           : 8,
            'pointsize'          : 0.1,
            'linewidth'          : 1.0,
            'pointcolor'         : '#ffffff',
            'linecolor'          : '#000000',
            'linestyle'          : '-',
        }
        self.form = form
        self.force = force
        self.setup()

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
                  forces_on=False,
                  arrows_on=False,
                  vertexcolor=None,
                  edgecolor=None,
                  facecolor=None,
                  edgelabel=None,
                  vertexlabel=None,
                  facelabel=None,
                  vertexsize=None,
                  forcescale=1.0):

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        facelabel   = facelabel or {}

        vertexsize  = size_to_sizedict(vertexsize, self.form.vertices(), self.default['vertexsize'])
        vertexcolor = color_to_colordict(vertexcolor, self.form.vertices(), self.default['vertexcolor'])
        edgecolor   = color_to_colordict(edgecolor, self.form.edges_where({'is_edge': True}), self.default['edgecolor'])
        facecolor   = color_to_colordict(facecolor, self.form.faces_where({'is_loaded': True}), self.default['facecolor'])

        x = self.form.get_vertices_attribute('x')
        y = self.form.get_vertices_attribute('y')

        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y), max(y)

        dx, dy = -xmin, -ymin

        scale = min(10.0 / fabs(xmax - xmin), 10.0 / fabs(ymax - ymin))

        key_xy = {k: [scale * (a['x'] + dx), scale * (a['y'] + dy)] for k, a in self.form.vertices(True)}

        # vertices

        if vertices_on:
            points = []
            for key, attr in self.form.vertices(True):
                bgcolor = vertexcolor[key]
                points.append({
                    'pos'       : key_xy[key],
                    'radius'    : vertexsize[key],
                    'facecolor' : vertexcolor[key],
                    'edgecolor' : self.default['edgecolor'],
                    'linewidth' : self.default['edgewidth'] * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default['fontsize'],
                })
            draw_xpoints_xy(points, self.ax1)

        # edges

        if edges_on:
            leaves = set(self.form.leaves())
            lines  = []
            arrows = []

            for u, v in self.form.edges_where({'is_edge': True}):

                sp = key_xy[u]
                ep = key_xy[v]

                if forces_on:
                    force = self.form.get_edge_attribute((u, v), 'f')
                    width = forcescale * fabs(force)
                    color = self.default['tensioncolor'] if force > 0 else self.default['compressioncolor']
                    text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])

                    lines.append({
                        'start'    : sp,
                        'end'      : ep,
                        'width'    : width,
                        'color'    : color,
                        'text'     : text,
                        'fontsize' : self.default['fontsize']
                    })

                arrows.append({
                    'start' : sp,
                    'end'   : ep,
                    'width' : self.default['edgewidth']
                })

            if arrows:
                if arrows_on:
                    draw_xarrows_xy(arrows, self.ax1)
                else:
                    draw_xlines_xy(arrows, self.ax1)
            if lines:
                draw_xlines_xy(lines, self.ax1, alpha=0.5)

    def draw_force(self,
                   vertices_on=True,
                   edges_on=True,
                   faces_on=False,
                   forces_on=False,
                   arrows_on=False,
                   vertexcolor=None,
                   edgecolor=None,
                   facecolor=None,
                   edgelabel=None,
                   vertexlabel=None,
                   facelabel=None,
                   vertexsize=None):

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        facelabel   = facelabel or {}

        vertexsize  = size_to_sizedict(vertexsize, self.force.vertices(), self.default['vertexsize'])
        vertexcolor = color_to_colordict(vertexcolor, self.force.vertices(), self.default['vertexcolor'])
        edgecolor   = color_to_colordict(edgecolor, self.force.edges(), self.default['edgecolor'])
        facecolor   = color_to_colordict(facecolor, self.force.faces(), self.default['facecolor'])

        x = self.force.get_vertices_attribute('x')
        y = self.force.get_vertices_attribute('y')

        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)

        dx, dy = -xmin, -ymin
        scale  = min(10.0 / fabs(xmax - xmin), 10.0 / fabs(ymax - ymin))
        key_xy = {k: [scale * (a['x'] + dx), scale * (a['y'] + dy)] for k, a in self.force.vertices(True)}

        # vertices

        if vertices_on:
            points = []
            for key, attr in self.force.vertices(True):
                bgcolor = vertexcolor[key]
                points.append({
                    'pos'       : key_xy[key],
                    'radius'    : vertexsize[key],
                    'facecolor' : vertexcolor[key],
                    'edgecolor' : self.default['edgecolor'],
                    'linewidth' : self.default['edgewidth'] * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default['fontsize'],
                })
            draw_xpoints_xy(points, self.ax2)

        # edges

        if edges_on:
            leaves = set(self.form.leaves())
            arrows = []
            for u, v, attr in self.force.edges(True):
                sp = key_xy[u]
                ep = key_xy[v]

                arrows.append({
                    'start' : sp,
                    'end'   : ep,
                    'color' : self.default['edgecolor'],
                    'width' : self.default['edgewidth'],
                })

            if arrows_on:
                draw_xarrows_xy(arrows, self.ax2)
            else:
                draw_xlines_xy(arrows, self.ax2)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    plotter = FormForcePlotter(None, None)
    plotter.show()
