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


# not sure if these functions can be used directly
# there is still an implementation difference between AGS and TNA
# use only the low-level functions that deal with mathematical abstractions
# or the wrappers for diagrams available in TNA

form_count_dof_ = XFunc('compas_ags.ags.form_count_dof_xfunc')
form_identify_dof_ = XFunc('compas_ags.ags.form_identify_dof_xfunc')
form_update_q_from_qind_ = XFunc('compas_ags.ags.form_update_q_from_qind_xfunc')
force_update_from_form_ = XFunc('compas_ags.ags.force_update_from_form_xfunc')


def form_count_dof(form):
    return form_count_dof_(form.to_data())


def form_identify_dof(form):
    return form_identify_dof_(form.to_data())


def form_update_q_from_qind(form):
    form.data = form_update_q_from_qind_(form.to_data())


def force_update_from_form(force, form):
    force.data = force_update_from_form_(force.to_data(), form.to_data())


class EquilibriumActions(object):

    def count_qind(self):
        k, m = form_count_dof(self.form)
        print(k, m)

    def identify_qind(self):
        k, m, ind = form_identify_dof(self.form)
        print(k, m, len(ind))
        self.form.set_edges_attribute('is_ind', False)
        self.form.set_edges_attribute('is_ind', True, keys=map(tuple, ind))
        self.form.draw()
        self.force.draw()

    # ==========================================================================
    # distribution: qind => 2D geometry of force diagram
    #
    # compute a force distribution from the independent edges
    # update the geometry of the foce diagram accordingly
    # ==========================================================================

    def update_q_from_qind(self):
        form_update_q_from_qind(self.form)
        force_update_from_form(self.force, self.form)
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
        scale = self.force.attributes['scale']
        vertical_from_q(self.form, scale)
        self.form.draw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
