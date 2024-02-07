from __future__ import absolute_import

import compas

from .horizontal import horizontal_nodal

__all__ = [
    "horizontal_nodal",
]

if not compas.IPY:
    from .relaxation import relax_boundary_openings
    from .horizontal_numpy import horizontal_nodal_numpy
    from .horizontal_numpy import horizontal_numpy
    from .vertical_numpy import vertical_from_q
    from .vertical_numpy import vertical_from_zmax

    __all__ += [
        "horizontal_nodal_numpy",
        "horizontal_numpy",
        "relax_boundary_openings",
        "vertical_from_q",
        "vertical_from_zmax",
    ]
