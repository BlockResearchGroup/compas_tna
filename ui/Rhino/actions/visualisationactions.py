from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import compas
import compas_rhino
import compas_tna

from compas_tna.rhino import FormArtist
from compas_tna.rhino import ForceArtist
from compas_tna.rhino import DiagramHelper

HERE = os.path.abspath(os.path.dirname(__file__))

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__all__ = ['VisualisationActions']


class VisualisationActions(object):

    def show_forces(self):
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.clear_forces()
        artist.draw_forces()
        artist.redraw()

    def hide_forces(self):
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.clear_forces()
        artist.redraw()

    def show_reactions(self):
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.clear_reactions()
        artist.draw_reactions()
        artist.redraw()

    def hide_reactions(self):
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.clear_reactions()
        artist.redraw()

    def show_angles(self):
        angles = self.form.get_edges_attribute('a')
        amin = min(angles)
        amax = max(angles)
        adif = amax - amin
        text = {}
        color = {}
        for u, v, attr in self.form.edges_where({'is_edge': True}, True):
            a = attr['a']
            if a > 5:
                text[u, v] = "{:.1f}".format(a)
                color[u, v] = i_to_green((a - amin) / adif)
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.clear_edgelabels()
        artist.draw_edgelabels(text=text, color=color)
        artist.redraw()

    def hide_angles(self):
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.clear_edgelabels()
        artist.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
