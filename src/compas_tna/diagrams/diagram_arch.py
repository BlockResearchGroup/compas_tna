import math

from compas.datastructures import Mesh


def create_arch_linear_mesh(H: float = 1.0, L: float = 2.0, x0: float = 0.0, n: int = 100) -> Mesh:
    """Construct a Mesh based on an arch linear discretisation.
    Note: The nodes of the mesh are spaced following a projection in a semicircular arch.

    Parameters
    ----------
    H : float, optional
        Height of the arch, by default 1.0
    L : float, optional
        Span of the arch, by default 2.0
    x0 : float, optional
        Initial coordinate of the arch, by default 0.0
    n : int, optional
        Numbers of nodes to be considered in the mesh, by default 100

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    """
    if n < 2:
        raise ValueError("n must be at least 2 to create a valid mesh")
    if H <= 0 or L <= 0:
        raise ValueError("Height (H) and length (L) must be positive values")
    if L < 2 * H:
        raise ValueError("Length (L) must be greater than 2 * Height (H)")

    # Add option for starting from Hi and Li for a given thk.
    radius = H / 2 + (L**2 / (8 * H))
    spr = math.atan2((L / 2), (radius - H))
    tot_angle = 2 * spr
    angle_init = (math.pi - tot_angle) / 2
    an = tot_angle / (n - 1)

    lines = []

    for i in range(n - 1):
        angle_i = angle_init + i * an
        angle_f = angle_init + (i + 1) * an
        xi = L / 2 - radius * math.cos(angle_i) + x0
        xf = L / 2 - radius * math.cos(angle_f) + x0

        lines.append([[xi, 0.0, 0.0], [xf, 0.0, 0.0]])

    mesh = Mesh.from_lines(lines)

    return mesh


def create_arch_linear_equally_spaced_mesh(L: float = 2.0, x0: float = 0.0, n: int = 100) -> Mesh:
    """Construct a Mesh based on an arch linear discretisation with equally spaced nodes.

    Parameters
    ----------
    L : float, optional
        Span of the arch, by default 2.0
    x0 : float, optional
        Initial coordinate of the arch, by default 0.0
    n : int, optional
        Numbers of nodes to be considered in the mesh, by default 100

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    """
    if n < 2:
        raise ValueError("n must be at least 2 to create a valid mesh")
    if L <= 0:
        raise ValueError("Length (L) must be a positive value")

    # Equally spaced coordinates
    x = [x0 + i * L / (n - 1) for i in range(n)]
    lines = []

    for i in range(n - 1):
        xi = x[i]
        xf = x[i + 1]

        lines.append([[xi, 0.0, 0.0], [xf, 0.0, 0.0]])

    mesh = Mesh.from_lines(lines)

    return mesh
