from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from thrustactions import ThrustActions
from forwardactions import ForwardActions
from forceactions import ForceActions
from formactions import FormActions


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


class TNAFrontController(ThrustActions, ForwardActions, ForceActions, FormActions):

    instancename = 'tna'

    def __init__(self):
        self.settings = {
            'forward.vertical.zmax' : None,

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
