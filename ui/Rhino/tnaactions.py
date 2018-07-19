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

    def horizontal(self):
        horizontal(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def horizontal_nodal(self):
        horizontal_nodal(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def vertical_zmax(self):
        vertical_from_zmax(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def vertical_formforce(self):
        vertical_from_formforce(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def vertical_target(self):
        guid = compas_rhino.select_surface()
        surface = RhinoSurface(guid)
        points = self.form.get_vertices_attributes('xyz')
        projections = surface.project_points(points)
        key_index = self.form.key_index()
        for key, attr in self.form.vertices(True):
            if attr['is_anchor']:
                continue
            if attr['is_external']:
                continue
            index = key_index[key]
            attr['zT'] = projections[index][2]
        vertical_from_target(self.form, self.force)
        self.form.draw()
        self.force.draw()

    def vertical_qind(self):
        vertical_from_qind(self.form, self.force)
        self.form.draw()
        self.force.draw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
