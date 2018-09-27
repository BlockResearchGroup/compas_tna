from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import compas
import compas_rhino
import compas_tna

from compas_tna.equilibrium import horizontal_nodal_rhino as horizontal
from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical


HERE = os.path.abspath(os.path.dirname(__file__))

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__all__ = ['EquilibriumActions']


class EquilibriumActions(object):

    def update_horizontal(self):
        horizontal(self.form, self.force, alpha=self.settings['horizontal.alpha'], kmax=self.settings['horizontal.kmax'])
        self.form.draw(layer=self.settings['form.layer'])
        self.force.draw(layer=self.settings['force.layer'])

    def update_vertical(self):
        vertical(self.form, self.settings['vertical.zmax'])
        self.form.draw(layer=self.settings['form.layer'])
        self.force.draw(layer=self.settings['force.layer'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
