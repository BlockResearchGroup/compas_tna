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

    horizontal
    horizontal_nodal


Proxies
-------

Use these functions in combination with a ``Proxy`` server to use the above horizontal
equilibrium algorithms directly from Rhino.

Note that whenever the original algorithm expects a diagram instance as parameter,
the corresponding proxy function will expect the data representing that diagram
instead. The data representing the diagram is stored in the ``data`` attribute of the
diagram.

.. code-block:: python

    proxy = Proxy('compas_tna.equilibrium')
    result = proxy.horizontal_nodal_proxy(form.data, force.data)
    if result:
        form.data = result[0]
        force.data = result[1]


.. autosummary::
    :toctree: generated/
    :nosignatures:

    horizontal_proxy
    horizontal_nodal_proxy


Vertical
========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    vertical_from_zmax
    vertical_from_bbox
    vertical_from_q

Proxies
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    vertical_from_zmax_proxy
    vertical_from_bbox_proxy
    vertical_from_q_proxy


"""
from __future__ import absolute_import

import compas

if compas.IPY:
    # from .horizontal import *
    from .vertical_alglib import *
else:
    from .horizontal_numpy import *
    from .vertical_numpy import *
    # from .scale_numpy import *


__all__ = [name for name in dir() if not name.startswith('_')]
