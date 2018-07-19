from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from patternactions import PatternActions
from formactions import FormActions
from forceactions import ForceActions
from equilibriumactions import EquilibriumActions
from vizactions import VizActions


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class TNAFrontController(VizActions, EquilibriumActions, ForceActions, FormActions, PatternActions):

    instancename = 'tna'

    def __init__(self):
        self.settings = {
            'TNA.zmax'  : None,
            'TNA.dr'    : 1e-3,
            'TNA.dx'    : 1e-6,
            'TNA.kmax'  : 100,
            'TNA.alpha' : 100,
        }
        self.form = None
        self.force = None

    def init(self):
        pass

    def update_settings(self):
        compas_rhino.update_settings(self.settings)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
