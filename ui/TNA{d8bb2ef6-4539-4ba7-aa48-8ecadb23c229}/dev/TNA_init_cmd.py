from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

from compas.rpc import Proxy

__commandname__ = "TNA_init"


def RunCommand(is_interactive):
    sc.sticky["TNA"] = {
        'proxy' : Proxy(),
        'form'  : None,
        'force' : None,
        'settings' : {
            'layer.form'  : 'TNA::FormDiagram',
            'layer.force' : 'TNA::ForceDiagram',
            'horizontal.kmax'  : 100,
            'horizontal.alpha' : 100,
        }
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
