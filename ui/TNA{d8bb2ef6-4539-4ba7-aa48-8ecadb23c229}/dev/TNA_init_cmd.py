from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_tna
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

            'boundaries.feet' : 2,

            'show.forces'    : True,
            'show.reactions' : True,

            'scale.forces'    : 0.1,
            'scale.reactions' : 0.1,

            'file.dir'  : compas_tna.DATA,
            'file.name' : 'tna.json'
        }
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
