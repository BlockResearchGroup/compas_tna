import math

from numpy import linspace

from compas.geometry import Point
from compas.tolerance import TOL
from compas.datastructures import Mesh


def create_arch_form_diagram(
    H: float = 1.0,
    L: float = 2.0,
    x0: float = 0.0,
    discretisation: int = 100,
) -> Mesh:
    """Construct a FormDiagram based on an arch linear discretisation.
    Note: The nodes of the form diagram are spaced following a projection in a semicircular arch.

    Parameters
    ----------
    H : float, optional
        Height of the arch, by default 1.00
    L : float, optional
        Span of the arch, by default 2.00
    x0 : float, optional
        Initial coordiante of the arch, by default 0.0
    discretisation : int, optional
        Numbers of nodes to be considered in the form diagram, by default 100

    Returns
    -------
    :class:`~compas_tno.diagrams.FormDiagram`
        The FormDiagram created.

    """
    # Add option for starting from Hi and Li for a given thk.
    radius = H / 2 + (L**2 / (8 * H))
    spr = math.atan2((L / 2), (radius - H))
    tot_angle = 2 * spr
    angle_init = (math.pi - tot_angle) / 2
    an = tot_angle / (discretisation - 1)

    lines = []

    for i in range(discretisation - 1):
        angle_i = angle_init + i * an
        angle_f = angle_init + (i + 1) * an
        xi = L / 2 - radius * math.cos(angle_i) + x0
        xf = L / 2 - radius * math.cos(angle_f) + x0

        lines.append([[xi, 0.0, 0.0], [xf, 0.0, 0.0]])
        
    form = Mesh.from_lines(lines)

    return form


def create_linear_form_diagram(
    L: float = 2.0,
    x0: float = 0.0,
    discretisation: int = 100,
) -> Mesh:
    """Helper to create a arch linear form-diagram with equaly spaced (in 2D) nodes.

    Parameters
    ----------
    L : float, optional
        Span of the arch, by default 2.00
    x0 : float, optional
        Initial coordiante of the arch, by default 0.0
    discretisation : int, optional
        Numbers of nodes to be considered in the form diagram, by default 100

    Returns
    -------
    :class:`~compas_tno.diagrams.FormDiagram`
        FormDiagram generated according to the parameters.

    """
    x = linspace(x0, x0 + L, discretisation)  # Continue this remove need of numpy in the future
    lines = []
    
    for i in range(discretisation - 1):
        xi = x[i]
        xf = x[i + 1]

        lines.append([[xi, 0.0, 0.0], [xf, 0.0, 0.0]])

    form = Mesh.from_lines(lines)

    return form

