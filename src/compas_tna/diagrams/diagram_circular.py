import math

from compas.datastructures import Mesh
from compas.geometry import intersection_line_line_xy


def create_circular_radial_mesh(center=(5.0, 5.0), radius=5.0, n_hoops=8, n_parallels=20, r_oculus=0.0, diagonal=False, diagonal_type='split') -> Mesh:
    """Construct a circular radial FormDiagram with hoops equally spaced in plan.

    Parameters
    ----------
    center : tuple, optional
        Planar coordinates of the form-diagram (xc, yc), by default (5.0, 5.0)
    radius : float, optional
        Radius of the form diagram, by default 5.0
    n_hoops : int, optional
        Number of hoops of the dome form diagram, by default 8
    n_parallels : int, optional
        Number of parallels of the dome form diagram, by default 20
    r_oculus : float, optional
        Value of the radius of the oculus, if no oculus is present should be set to zero, by default 0.0
    diagonal : bool, optional
        Activate diagonal in the quads, by default False
    diagonal_type : str, optional
        Control how diagonals are placed in the quads Options are ["split", "straight", "right", "left"] 
        Default is "split", when the X diagonals will be split at their intersection. 
        If "straight" the both quad diagonals are added as straight lines.
        If "right" the diagonals will point to the right (x positive) of the diagram.
        If "left" the diagonals will point to the left (x negative) of the diagram.

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    """

    xc = center[0]
    yc = center[1]
    theta = 2 * math.pi / n_parallels
    r_div = (radius - r_oculus) / n_hoops
    lines = []

    # indset = []  # TODO: Automate indset selection...

    for nr in range(n_hoops + 1):
        for nc in range(n_parallels):
            if (r_oculus + nr * r_div) > 0.0:
                # Meridian Elements
                xa = xc + (r_oculus + nr * r_div) * math.cos(theta * nc)
                xb = xc + (r_oculus + nr * r_div) * math.cos(theta * (nc + 1))
                ya = yc + (r_oculus + nr * r_div) * math.sin(theta * nc)
                yb = yc + (r_oculus + nr * r_div) * math.sin(theta * (nc + 1))
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])

            if nr <= n_hoops - 1:
                # Radial Elements
                xa = xc + (r_oculus + nr * r_div) * math.cos(theta * nc)
                xb = xc + (r_oculus + (nr + 1) * r_div) * math.cos(theta * nc)
                ya = yc + (r_oculus + nr * r_div) * math.sin(theta * nc)
                yb = yc + (r_oculus + (nr + 1) * r_div) * math.sin(theta * nc)
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])

    if diagonal:
        for nr in range(n_hoops):
            for nc in range(n_parallels):
                if (r_oculus + nr * r_div) > 0.0:
                    # Meridian Element i
                    xa = xc + (r_oculus + nr * r_div) * math.cos(theta * nc)
                    xb = xc + (r_oculus + nr * r_div) * math.cos(theta * (nc + 1))
                    ya = yc + (r_oculus + nr * r_div) * math.sin(theta * nc)
                    yb = yc + (r_oculus + nr * r_div) * math.sin(theta * (nc + 1))

                    # Meridian Element i + 1
                    xa_ = xc + (r_oculus + (nr + 1) * r_div) * math.cos(theta * nc)
                    xb_ = xc + (r_oculus + (nr + 1) * r_div) * math.cos(theta * (nc + 1))
                    ya_ = yc + (r_oculus + (nr + 1) * r_div) * math.sin(theta * nc)
                    yb_ = yc + (r_oculus + (nr + 1) * r_div) * math.sin(theta * (nc + 1))

                    if diagonal_type == "right":
                        if nc + 1 > n_parallels / 2:
                            lines.append([[xa, ya, 0.0], [xb_, yb_, 0.0]])
                        else:
                            lines.append([[xa_, ya_, 0.0], [xb, yb, 0.0]])
                    elif diagonal_type == "left":
                        if nc + 1 > n_parallels / 2:
                            lines.append([[xa_, ya_, 0.0], [xb, yb, 0.0]])
                        else:
                            lines.append([[xa, ya, 0.0], [xb_, yb_, 0.0]])
                    elif diagonal_type == "straight":
                        midx, midy, _ = intersection_line_line_xy([[xa, ya], [xb_, yb_]], [[xa_, ya_], [xb, yb]])  # type: ignore
                        lines.append([[xa, ya, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb_, yb_, 0.0]])
                        lines.append([[xa_, ya_, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb, yb, 0.0]])
                    elif diagonal_type == "split":
                        midx = (xa + xa_ + xb + xb_) / 4
                        midy = (ya + ya_ + yb + yb_) / 4
                        lines.append([[xa, ya, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb_, yb_, 0.0]])
                        lines.append([[xa_, ya_, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb, yb, 0.0]])
                    else:
                        raise ValueError(f"Invalid diagonal type: {diagonal_type}. Choose from ['split', 'straight', 'right', 'left']")

    mesh = Mesh.from_lines(lines, delete_boundary_face=True)
    if r_oculus > 0.0:
        mesh.delete_face(1)

    return mesh


def create_circular_radial_spaced_mesh(center=(5.0, 5.0), radius=5.0, n_hoops=8, n_parallels=20, r_oculus=0.0, diagonal=False, diagonal_type='split') -> Mesh:
    """Construct a circular radial FormDiagram with hoops not equally spaced in plan, but equally spaced with regards to the projection on a hemisphere.

    Parameters
    ----------
    center : tuple, optional
        Planar coordinates of the form-diagram (xc, yc), by default (5.0, 5.0)
    radius : float, optional
        Radius of the form diagram, by default 5.0
    n_hoops : int, optional
        Number of hoops of the dome form diagram, by default 8
    n_parallels : int, optional
        Number of parallels of the dome form diagram, by default 20
    r_oculus : float, optional
        Value of the radius of the oculus, if no oculus is present should be set to zero, by default 0.0
    diagonal : bool, optional
        Activate diagonal X diagonals in the quads. See diagonal_type for more details.
    diagonal_type : str, optional
        Control how diagonals are placed in the quads Options are ["split", "straight", "right", "left"] 
        Default is "split", when the X diagonals will be split at their intersection. 
        If "straight" the both quad diagonals are added as straight lines.
        If "right" the diagonals will point to the right (x positive) of the diagram.
        If "left" the diagonals will point to the left (x negative) of the diagram.

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    """
    xc = center[0]
    yc = center[1]
    theta = 2 * math.pi / n_parallels
    r_div = (radius - r_oculus) / n_hoops
    radius = radius - r_oculus
    lines = []

    for nr in range(n_hoops + 1):
        for nc in range(n_parallels):
            if (r_oculus + nr) > 0:
                # Meridian Elements
                xa = xc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.cos(theta * nc)
                xb = xc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.cos(theta * (nc + 1))
                ya = yc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.sin(theta * nc)
                yb = yc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.sin(theta * (nc + 1))
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])

            if nr <= n_hoops - 1:
                # Radial Elements
                xa = xc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.cos(theta * nc)
                xb = xc + (r_oculus + radius * math.cos((n_hoops - (nr + 1)) / n_hoops * math.pi / 2)) * math.cos(theta * nc)
                ya = yc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.sin(theta * nc)
                yb = yc + (r_oculus + radius * math.cos((n_hoops - (nr + 1)) / n_hoops * math.pi / 2)) * math.sin(theta * nc)
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])

    if diagonal:
        for nr in range(n_hoops):
            for nc in range(n_parallels):
                if (r_oculus + nr * r_div) > 0.0:
                    # Meridian Element i
                    xa = xc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.cos(theta * nc)
                    xb = xc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.cos(theta * (nc + 1))
                    ya = yc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.sin(theta * nc)
                    yb = yc + (r_oculus + radius * math.cos((n_hoops - nr) / n_hoops * math.pi / 2)) * math.sin(theta * (nc + 1))

                    # Meridian Element i + 1
                    xa_ = xc + (r_oculus + radius * math.cos((n_hoops - (nr + 1)) / n_hoops * math.pi / 2)) * math.cos(theta * nc)
                    xb_ = xc + (r_oculus + radius * math.cos((n_hoops - (nr + 1)) / n_hoops * math.pi / 2)) * math.cos(theta * (nc + 1))
                    ya_ = yc + (r_oculus + radius * math.cos((n_hoops - (nr + 1)) / n_hoops * math.pi / 2)) * math.sin(theta * nc)
                    yb_ = yc + (r_oculus + radius * math.cos((n_hoops - (nr + 1)) / n_hoops * math.pi / 2)) * math.sin(theta * (nc + 1))
                    if diagonal_type == "right":
                        if nc + 1 > n_parallels / 2:
                            lines.append([[xa, ya, 0.0], [xb_, yb_, 0.0]])
                        else:
                            lines.append([[xa_, ya_, 0.0], [xb, yb, 0.0]])
                    elif diagonal_type == "left":
                        if nc + 1 > n_parallels / 2:
                            lines.append([[xa_, ya_, 0.0], [xb, yb, 0.0]])
                        else:
                            lines.append([[xa, ya, 0.0], [xb_, yb_, 0.0]])
                    elif diagonal_type == "straight":
                        midx, midy, _ = intersection_line_line_xy([[xa, ya], [xb_, yb_]], [[xa_, ya_], [xb, yb]])  # type: ignore
                        lines.append([[xa, ya, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb_, yb_, 0.0]])
                        lines.append([[xa_, ya_, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb, yb, 0.0]])
                    elif diagonal_type == "split":
                        midx = (xa + xa_ + xb + xb_) / 4
                        midy = (ya + ya_ + yb + yb_) / 4
                        lines.append([[xa, ya, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb_, yb_, 0.0]])
                        lines.append([[xa_, ya_, 0.0], [midx, midy, 0.0]])
                        lines.append([[midx, midy, 0.0], [xb, yb, 0.0]])
                    else:
                        raise ValueError(f"Invalid diagonal type: {diagonal_type}. Choose from ['split', 'straight', 'right', 'left']")

    mesh = Mesh.from_lines(lines, delete_boundary_face=True)
    if r_oculus > 0.0:
        mesh.delete_face(1)

    return mesh


def create_circular_spiral_mesh(center=(5.0, 5.0), radius=5.0, n_hoops=8, n_parallels=20, r_oculus=0.0) -> Mesh:
    """Construct a circular radial FormDiagram with hoops not equally spaced in plan, but equally spaced with regards to the projection on a hemisphere.

    Parameters
    ----------
    center : tuple, optional
        Planar coordinates of the form-diagram (xc, yc), by default (5.0, 5.0)
    radius : float, optional
        Radius of the form diagram, by default 5.0
    n_hoops : int, optional
        Number of hoops of the dome form diagram, by default 8
        The number of spiral intersections in the diagram equals the number of hoops.
    n_parallels : int, optional
        Number of parallels of the dome form diagram, by default 20
        The number of spirals in the diagram equals the number of parallels.
    r_oculus : float, optional
        Value of the radius of the oculus, if no oculus is present should be set to zero, by default 0.0

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    """
    xc = center[0]
    yc = center[1]
    theta = 2 * math.pi / n_parallels
    r_div = (radius - r_oculus) / n_hoops
    lines = []

    for nr in range(n_hoops + 1):
        for nc in range(n_parallels):
            if nr > 0.0:  # This avoid the center...
                if nr % 2 == 0:
                    # Diagonal to Up
                    xa = xc + (r_oculus + nr * r_div) * math.cos(theta * nc)
                    xb = xc + (r_oculus + (nr - 1) * r_div) * math.cos(theta * (nc + 1 / 2))
                    ya = yc + (r_oculus + nr * r_div) * math.sin(theta * nc)
                    yb = yc + (r_oculus + (nr - 1) * r_div) * math.sin(theta * (nc + 1 / 2))

                    # Diagonal to Down
                    xa_ = xc + (r_oculus + nr * r_div) * math.cos(theta * nc)
                    xb_ = xc + (r_oculus + (nr - 1) * r_div) * math.cos(theta * (nc - 1 / 2))
                    ya_ = yc + (r_oculus + nr * r_div) * math.sin(theta * nc)
                    yb_ = yc + (r_oculus + (nr - 1) * r_div) * math.sin(theta * (nc - 1 / 2))

                    lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
                    lines.append([[xa_, ya_, 0.0], [xb_, yb_, 0.0]])
                else:
                    # Diagonal to Up
                    xa = xc + (r_oculus + nr * r_div) * math.cos(theta * (nc + 1 / 2))
                    xb = xc + (r_oculus + (nr - 1) * r_div) * math.cos(theta * (nc + 1))
                    ya = yc + (r_oculus + nr * r_div) * math.sin(theta * (nc + 1 / 2))
                    yb = yc + (r_oculus + (nr - 1) * r_div) * math.sin(theta * (nc + 1))

                    # Diagonal to Down
                    xa_ = xc + (r_oculus + nr * r_div) * math.cos(theta * (nc + 1 / 2))
                    xb_ = xc + (r_oculus + (nr - 1) * r_div) * math.cos(theta * (nc))
                    ya_ = yc + (r_oculus + nr * r_div) * math.sin(theta * (nc + 1 / 2))
                    yb_ = yc + (r_oculus + (nr - 1) * r_div) * math.sin(theta * (nc))

                    lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
                    lines.append([[xa_, ya_, 0.0], [xb_, yb_, 0.0]])
                if nr == n_hoops:
                    xa = xc + (r_oculus + nr * r_div) * math.cos(theta * nc)
                    xb = xc + (r_oculus + nr * r_div) * math.cos(theta * (nc + 1))
                    ya = yc + (r_oculus + nr * r_div) * math.sin(theta * nc)
                    yb = yc + (r_oculus + nr * r_div) * math.sin(theta * (nc + 1))
                    lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
            if nr == 0 and r_oculus > 0.0:
                # If oculus, this will be the compression ring
                xa = xc + (r_oculus) * math.cos(theta * (nc))
                xb = xc + (r_oculus) * math.cos(theta * (nc + 1))
                ya = yc + (r_oculus) * math.sin(theta * (nc))
                yb = yc + (r_oculus) * math.sin(theta * (nc + 1))
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])

    mesh = Mesh.from_lines(lines, delete_boundary_face=True)
    if r_oculus > 0.0:
        mesh.delete_face(1)

    return mesh
