from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_rhino.geometry import RhinoSurface

from compas_tna.equilibrium import horizontal_rhino as horizontal
from compas_tna.equilibrium import horizontal_nodal_rhino as horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical_from_zmax
from compas_tna.equilibrium import vertical_from_formforce_rhino as vertical_from_formforce
from compas_tna.equilibrium import vertical_from_target_rhino as vertical_from_target
from compas_tna.equilibrium import vertical_from_qind_rhino as vertical_from_qind


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class TNAActions(object):

    # set scale (absolute, zmax, proportional, target, ...)
    # update (horizontal) q from qind
    # update (horizontal) q from force
    # update force diagram from q
    # update vertical equilibrium from q

    def count_qind(self):
        pass

    def identify_qind(self):
        pass

    def update_q_from_qind(self):
        pass

    # ==========================================================================
    # scale of force diagram
    # ==========================================================================

    def compute_scale_from_zmax(self):
        pass

    def compute_scale_from_target(self):
        pass

    def compute_scale_from_bbox(self):
        pass

    # ==========================================================================
    # horizontal
    # ==========================================================================

    def parallelise_formforce(self):
        horizontal(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def parallelise_formforce_nodal(self):
        horizontal_nodal(self.form, self.force)
        self.form.draw()
        self.force.draw()

    # ==========================================================================
    # vertical
    # ==========================================================================

    def update_vertical(self):
        vertical_from_q(self.form, self.force)
        self.form.draw()
        self.force.draw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
