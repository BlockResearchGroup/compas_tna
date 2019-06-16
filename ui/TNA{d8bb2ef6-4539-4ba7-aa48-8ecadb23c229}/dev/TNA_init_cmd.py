from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import scriptcontext as sc
import rhinoscriptsyntax as rs

import compas_tna
from compas.rpc import Proxy


__commandname__ = "TNA_init"


def get_document_basename():
    return rs.DocumentName()


def get_document_filename():
    basename = get_document_basename()
    if not basename:
        return None
    return os.path.splitext(basename)[0]


def get_document_extension():
    basename = get_document_basename()
    if not basename:
        return None
    return os.path.splitext(basename)[1]


def get_document_filepath():
    return rs.DocumentPath()


def get_document_dirname():
    filepath = get_document_filepath()
    if not filepath:
        return None
    return os.path.dirname(filepath)


# ==============================================================================
# Command
# ==============================================================================


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

            'file.dir'  : get_document_dirname(),
            'file.name' : None
        }
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
