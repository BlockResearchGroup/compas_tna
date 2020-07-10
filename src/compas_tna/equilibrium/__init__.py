"""
********************************************************************************
compas_tna.equilibrium
********************************************************************************

.. currentmodule:: compas_tna.equilibrium


Horizontal
==========

Algorithms related to horizontal equilibrium of the form diagram and thus of the
corresponding thrust network.

Horizontal equilibrium is established when the form and force diagram are reciprocal.
Two diagrams are said to be reciprocal if they are each other's dual and if all
corresponding edges are at any specific constant angle.

Note that for legibility, the form and force diagrams in ``compas_tna`` are drawn
such that corresponding edges of reciprocal diagrams are perpendicular.
However, the diagrams are made reciprocal by parallelising the corresponding edges.
The diagrams are thus rotated by 90 degrees and back at the beginning and end of
each of the horizontal equilibrium algorithms.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    horizontal_nodal


Proxies
-------

The ``_numpy`` variants of the above functions can be used directly in Rhino using an RPC server proxy.

Note that whenever the original algorithm expects a diagram instance as parameter,
the corresponding proxy function will expect the data representing that diagram
instead. The data representing the diagram is stored in the ``data`` attribute of the
diagram.

>>> tna = Proxy('compas_tna.equilibrium')
>>> formdata, forcedata = tna.horizontal_nodal_numpy_proxy(form.data, force.data)
>>> form.data = formdata
>>> force.data = forcedata

.. autosummary::
    :toctree: generated/
    :nosignatures:


Vertical
========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    vertical_from_zmax
    vertical_from_q

Proxies
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    vertical_from_zmax_proxy
    vertical_from_q_proxy


"""
from __future__ import absolute_import

import compas

from .horizontal import *  # noqa: F401 F403

if compas.IPY:
    pass
else:
    # from .horizontal_numpy import *  # noqa: F401 F403
    from .vertical_numpy import *  # noqa: F401 F403


__all__ = [name for name in dir() if not name.startswith('_')]
