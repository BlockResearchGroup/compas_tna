from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas.utilities import XFunc

from compas_rhino.geometry import RhinoSurface

from compas_tna.equilibrium import horizontal_rhino as horizontal
from compas_tna.equilibrium import horizontal_nodal_rhino as horizontal_nodal

from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical_from_zmax
from compas_tna.equilibrium import vertical_from_target_rhino as vertical_from_target
from compas_tna.equilibrium import vertical_from_bbox_rhino as vertical_from_bbox


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


count_dof_f = XFunc('compas_ags.ags.graphstatics.count_dof_xfunc')
identify_dof_f = XFunc('compas_ags.ags.graphstatics.identify_dof_xfunc')
update_forcedensity_f = XFunc('compas_ags.ags.graphstatics.update_forcedensity_xfunc')
update_forcediagram_f = XFunc('compas_ags.ags.graphstatics.update_forcediagram_xfunc')


def count_dof(form):
    return count_dof_f(form.to_data())


def identify_dof(form):
    return identify_dof_f(form.to_data())


def update_q_from_qind(form):
    form.data = update_forcedensity_f(form.to_data())


def update_forcediagram_from_q(force, form):
    force.data = update_forcediagram_f(force.to_data(), form.to_data())


class EquilibriumActions(object):

    # ==========================================================================
    # distribution: qind => 2D geometry of force diagram
    #
    # compute a force distribution from the independent edges
    # update the geometry of the foce diagram accordingly
    # ==========================================================================

    def count_qind(self):
        k, m = count_dof(self.form)
        print(k, m)

    def identify_qind(self):
        k, m, ind = identify_dof(self.form)
        print(k, m)
        self.form.set_edges_attribute('is_ind', False)
        self.form.set_edges_attribute('is_ind', True, keys=ind)
        self.form.draw()
        self.force.draw()

    def update_q_from_qind(self):
        update_q_from_qind(self.form)
        update_forcediagram_from_q(self.force, self.form)
        self.form.draw()
        self.force.draw()

    # ==========================================================================
    # distribution: horizontal => 2D geometry of form and force diagram
    #
    # compute horizontal equilibrium and update force densities accordingly
    # form and force are updated
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
    # scale => 3D geometry of form diagram
    #
    # determine the scale of the force diagram to optimise a specific goal
    # update the geometry of the form diagram accordingly
    # ==========================================================================

    def compute_scale_from_zmax(self):
        scale = vertical_from_zmax(self.form)
        self.force.attributes['scale'] = scale
        self.form.draw()

    def compute_scale_from_target(self):
        scale = vertical_from_target(self.form)
        self.force.attributes['scale'] = scale
        self.form.draw()

    def compute_scale_from_bbox(self):
        scale = vertical_from_bbox(self.form)
        self.force.attributes['scale'] = scale
        self.form.draw()

    # ==========================================================================
    # vertical => 3D geometry of form diagram
    #
    # update equilibrium for the given scale and force densities
    # ==========================================================================

    def update_vertical_from_q(self):
        vertical_from_q(self.form, self.force.attributes['scale'])
        self.form.draw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
