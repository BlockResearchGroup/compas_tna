import math

from compas.datastructures import Mesh
from compas.geometry import closest_point_in_cloud
from compas.geometry import distance_point_point_xy
from compas.geometry import intersection_segment_segment_xy
from compas.geometry import mirror_points_line
from compas.geometry import rotate_points_xy
from compas.geometry import sort_points_xy


def mirror_4x(line, line_hor, line_ver, lines):
    """Helper to mirror an object 4 times."""

    lines.append(line)
    a_mirror, b_mirror = mirror_points_line(line, line_hor)
    lines.append([a_mirror, b_mirror])
    a_mirror, b_mirror = mirror_points_line([a_mirror, b_mirror], line_ver)
    lines.append([a_mirror, b_mirror])
    a_mirror, b_mirror = mirror_points_line(line, line_ver)
    lines.append([a_mirror, b_mirror])

    return lines


def mirror_8x(line, origin, line_hor, line_ver, lines):
    """Helper to mirror an object 8 times."""

    lines = mirror_4x(line, line_hor, line_ver, lines)
    rot = rotate_points_xy(line, math.pi / 2, origin=origin)
    lines = mirror_4x(rot, line_hor, line_ver, lines)

    return lines


def append_mirrored_lines(line, list_, line_hor, line_ver):
    """Helper to mirror an object 8 times and add to the list"""
    mirror_a = mirror_points_line(line, line_hor)
    mirror_b = mirror_points_line(mirror_a, line_ver)
    mirror_c = mirror_points_line(line, line_ver)
    list_.append(mirror_a)
    list_.append(mirror_b)
    list_.append(mirror_c)


def is_point_in_cloud(point, cloud, tol=1e-6):
    if len(cloud) == 0:
        return False
    return closest_point_in_cloud(point, cloud)[0] < tol


def split_intersection_lines(lines, tol=1e-6):
    """Split lines at their intersection

    Parameters
    ----------
    lines : [[list]]
        List of lines

    Returns
    -------
    clean_lines
        Lines split at the intersections
    """

    lines = [[[pt1[0], pt1[1], 0.0], [pt2[0], pt2[1], 0.0]] for pt1, pt2 in lines]
    clean_lines = []
    dict_lines = {i: [] for i in range(len(lines))}  # dict to store the inner points intersected

    # find intersections and store them as the inner points of given segments
    i = 0
    for line in lines:
        for line_ in lines:
            if line == line_:
                continue
            pt = intersection_segment_segment_xy(line, line_)
            if pt:
                if is_point_in_cloud(pt, line):
                    continue
                if not is_point_in_cloud(pt, dict_lines[i]):  # pt not in dict_lines[i]:
                    dict_lines[i].append(pt)
        i += 1

    # split lines containing inner intersections
    for key in dict_lines:
        line = lines[key]
        intpoints = dict_lines[key]
        if intpoints:
            np = len(intpoints)
            intsorted = sort_points_xy(line[0], dict_lines[key])
            startline = [line[0], intsorted[0][1]]
            endline = [intsorted[-1][1], line[1]]
            if distance_point_point_xy(*startline) > tol:
                clean_lines.append(startline)
            if distance_point_point_xy(*endline) > tol:
                clean_lines.append(endline)
            if np > 1:
                for k in range(np - 1):
                    intline = [intsorted[k][1], intsorted[k + 1][1]]
                    if distance_point_point_xy(*intline) > tol:
                        clean_lines.append(intline)
        else:
            if distance_point_point_xy(*line) > tol:
                clean_lines.append(line)

    return clean_lines


def create_cross_mesh(x_span=(0.0, 10.0), y_span=(0.0, 10.0), n=10) -> Mesh:
    """Construct a Mesh based on cross discretisation with orthogonal arrangement and diagonal.

    Parameters
    ----------
    x_span : tuple, optional
        Tuple with initial- and end-points of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Tuple with initial- and end-points of the vault in y direction, by default (0.0, 10.0)
    n : int, optional
        Set the density of the grid in x and y directions, by default 10

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    Notes
    -----
    Position of the quadrants is as in the schema below:

        Q3
    Q2      Q1
        Q4
    """

    y1 = float(y_span[1])
    y0 = float(y_span[0])
    x1 = float(x_span[1])
    x0 = float(x_span[0])
    x_span_length = x1 - x0
    y_span_length = y1 - y0
    dx = x_span_length / n
    dy = y_span_length / n

    lines = []

    for i in range(n + 1):
        for j in range(n + 1):
            if i < n and j < n:
                # Vertical Members:
                xa = x0 + dx * i
                ya = y0 + dy * j
                xb = x0 + dx * (i + 1)
                yb = y0 + dy * j
                # Horizontal Members:
                xc = x0 + dx * i
                yc = y0 + dy * j
                xd = x0 + dx * i
                yd = y0 + dy * (j + 1)
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
                lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
                if i == j:
                    # Diagonal Members in + Direction:
                    xc = x0 + dx * i
                    yc = y0 + dy * j
                    xd = x0 + dx * (i + 1)
                    yd = y0 + dy * (j + 1)
                    lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
                if i + j == n:
                    # Diagonal Members in - Direction:
                    xc = x0 + dx * i
                    yc = y0 + dy * j
                    xd = x0 + dx * (i - 1)
                    yd = y0 + dy * (j + 1)
                    lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
                    if i == (n - 1):
                        xc = x0 + dx * i
                        yc = y0 + dy * j
                        xd = x0 + dx * (i + 1)
                        yd = y0 + dy * (j - 1)
                        lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
            else:
                if i == n and j < n:
                    # Vertical Members on last column:
                    xa = x0 + dx * j
                    ya = y0 + dy * i
                    xb = x0 + dx * (j + 1)
                    yb = y0 + dy * i
                    # Horizontal Members:
                    xc = x0 + dx * i
                    yc = y0 + dy * j
                    xd = x0 + dx * i
                    yd = y0 + dy * (j + 1)
                    lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
                    lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])

    mesh = Mesh.from_lines(lines, delete_boundary_face=True)

    return mesh


def create_cross_diagonal_mesh(x_span=(0.0, 10.0), y_span=(0.0, 10.0), partial_bracing_modules=None, n=10) -> Mesh:
    """Construct a Mesh based on a mixture of cross and fan discretisation

    Parameters
    ----------
    x_span : tuple, optional
        Tuple with initial- and end-points of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Tuple with initial- and end-points of the vault in y direction, by default (0.0, 10.0)
    n : int, optional
        Set the density of the grid in x and y directions, by default 10
    partial_bracing_modules : str, optional
        If partial bracing modules are included, by default None

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    """
    y1 = float(y_span[1])
    y0 = float(y_span[0])
    x1 = float(x_span[1])
    x0 = float(x_span[0])
    x_span_length = x1 - x0
    y_span_length = y1 - y0
    dx = x_span_length / n
    dy = y_span_length / n

    xc0 = x0 + x_span_length / 2
    yc0 = y0 + y_span_length / 2

    nx = ny = int(n / 2)
    if partial_bracing_modules is None:
        nstop = 0
    else:
        nstop = nx - partial_bracing_modules  # Test to stop

    line_hor = [[x0, yc0, 0.0], [xc0, yc0, 0.0]]
    line_ver = [[xc0, y0, 0.0], [xc0, yc0, 0.0]]
    origin = [xc0, yc0, 0.0]

    lines = []

    for i in range(nx):
        for j in range(ny + 1):
            if j <= i:
                if i >= nstop and j >= nstop:
                    # Diagonal Members:
                    xa = x0 + dx * i
                    ya = y0 + dy * 1 * (i - j) / (nx - j) + dy * j
                    xb = x0 + dx * (i + 1)
                    yb = y0 + dy * 1 * (i - j + 1) / (nx - j) + dy * j
                    lin = [[xa, ya, 0.0], [xb, yb, 0.0]]
                    lines = mirror_8x(lin, origin, line_hor, line_ver, lines)

                if i == j and i < nx - 1:
                    # Main diagonal:
                    xa = x0 + dx * i
                    ya = y0 + dy * j
                    xb = x0 + dx * (i + 1)
                    yb = y0 + dy * (j + 1)
                    lin = [[xa, ya, 0.0], [xb, yb, 0.0]]
                    lines = mirror_4x(lin, line_hor, line_ver, lines)

                # Horizontal Members:
                xa = x0 + dx * i
                ya = y0 + dy * j
                xb = x0 + dx * (i + 1)
                yb = y0 + dy * j
                lin = [[xa, ya, 0.0], [xb, yb, 0.0]]
                lines = mirror_8x(lin, origin, line_hor, line_ver, lines)

                i += 1
                # Vertical Members:
                xa = x0 + dx * i
                ya = y0 + dy * j
                xb = x0 + dx * i
                yb = y0 + dy * (j + 1)

                if i >= nstop and j >= nstop:
                    x_ = xa
                    y_ = y0 + dy * 1 * (i - j) / (nx - j) + dy * j
                    lin = [[xa, ya, 0.0], [x_, y_, 0.0]]
                    lines = mirror_8x(lin, origin, line_hor, line_ver, lines)
                    lin = [[x_, y_, 0.0], [xb, yb, 0.0]]
                    lines = mirror_8x(lin, origin, line_hor, line_ver, lines)
                else:
                    lin = [[xa, ya, 0.0], [xb, yb, 0.0]]
                    lines = mirror_8x(lin, origin, line_hor, line_ver, lines)

                i -= 1

    mesh = Mesh.from_lines(lines, delete_boundary_face=True)
    mesh.remove_duplicate_vertices()

    return mesh


def create_cross_with_diagonal_mesh(x_span=(0.0, 10.0), y_span=(0.0, 10.0), n=10) -> Mesh:
    """Construct a Mesh based on cross discretisation with diagonals.

    Parameters
    ----------
    x_span : tuple, optional
        Tuple with initial- and end-points of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Tuple with initial- and end-points of the vault in y direction, by default (0.0, 10.0)
    n : int, optional
        Set the density of the mesh, by default 10

    Returns
    -------
    mesh : Mesh
        The Mesh created.
    """

    y1 = float(y_span[1])
    y0 = float(y_span[0])
    x1 = float(x_span[1])
    x0 = float(x_span[0])
    x_span_length = x1 - x0
    y_span_length = y1 - y0
    dx = x_span_length / n
    dy = y_span_length / n

    lines = []

    for i in range(n + 1):
        for j in range(n + 1):
            if i < n and j < n:
                # Hor Members:
                xa = x0 + dx * i
                ya = y0 + dy * j
                xb = x0 + dx * (i + 1)
                yb = y0 + dy * j
                # Ver Members:
                xc = x0 + dx * i
                yc = y0 + dy * j
                xd = x0 + dx * i
                yd = y0 + dy * (j + 1)
                lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
                lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
                if (i < n / 2 and j < n / 2) or (i >= n / 2 and j >= n / 2):
                    # Diagonal Members in + Direction:
                    xc = x0 + dx * i
                    yc = y0 + dy * j
                    xd = x0 + dx * (i + 1)
                    yd = y0 + dy * (j + 1)
                    lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
                else:
                    # Diagonal Members in - Direction:
                    xc = x0 + dx * i
                    yc = y0 + dy * (j + 1)
                    xd = x0 + dx * (i + 1)
                    yd = y0 + dy * j
                    lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])
            else:
                if i == n and j < n:
                    # Vertical Members on last column:
                    xa = x0 + dx * j
                    ya = y0 + dy * i
                    xb = x0 + dx * (j + 1)
                    yb = y0 + dy * i
                    # Horizontal Members:
                    xc = x0 + dx * i
                    yc = y0 + dy * j
                    xd = x0 + dx * i
                    yd = y0 + dy * (j + 1)
                    lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
                    lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])

    mesh = Mesh.from_lines(lines, delete_boundary_face=True)

    return mesh


def create_fan_mesh(x_span=(0.0, 10.0), y_span=(0.0, 10.0), n_fans=10, n_hoops=10) -> Mesh:
    """Helper to construct a Mesh based on fan discretisation with straight lines to the corners.

    Parameters
    ----------
    x_span : tuple, optional
        Tuple with initial- and end-points of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Tuple with initial- and end-points of the vault in y direction, by default (0.0, 10.0)
    n_fans : int, optional
        Number of segments from ridge to supports, by default 10
    n_hoops : int, optional
        Number of hoop divisions that cut across the spikes, by default 10

    Returns
    -------
    mesh : Mesh
        The Mesh created.
    """

    if n_fans % 2 != 0 or n_hoops % 2 != 0:
        msg = "Warning!: discretisation of this form diagram has to be even."
        raise ValueError(msg)

    y1 = float(y_span[1])
    y0 = float(y_span[0])
    x1 = float(x_span[1])
    x0 = float(x_span[0])

    x_span_length = x1 - x0
    y_span_length = y1 - y0
    xc0 = x0 + x_span_length / 2
    yc0 = y0 + y_span_length / 2
    division_fans = n_fans
    division_hoops = n_hoops
    dxf = float(x_span_length / division_fans)
    dyh = float(y_span_length / division_hoops)
    dyf = float(y_span_length / division_fans)
    dxh = float(x_span_length / division_hoops)

    nfans = int(division_fans / 2)
    nhoops = int(division_hoops / 2)
    line_hor = [[x0, yc0, 0.0], [xc0, yc0, 0.0]]
    line_ver = [[xc0, y0, 0.0], [xc0, yc0, 0.0]]

    lines = []

    for nf in range(nfans + 1):
        for nh in range(nhoops):
            # Diagonal Members:
            xa = x0 + dxh * nh
            ya = y0 + dyf * nf * nh / nhoops
            xb = x0 + dxh * (nh + 1)
            yb = y0 + dyf * nf * (nh + 1) / nhoops
            lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])

            a_mirror, b_mirror = mirror_points_line([[xa, ya, 0.0], [xb, yb, 0.0]], line_hor)
            lines.append([a_mirror, b_mirror])
            a_mirror, b_mirror = mirror_points_line([a_mirror, b_mirror], line_ver)
            lines.append([a_mirror, b_mirror])
            a_mirror, b_mirror = mirror_points_line([[xa, ya, 0.0], [xb, yb, 0.0]], line_ver)
            lines.append([a_mirror, b_mirror])

            xa_ = x0 + dxf * nf * nh / nhoops
            ya_ = y0 + dyh * nh
            xb_ = x0 + dxf * nf * (nh + 1) / nhoops
            yb_ = y0 + dyh * (nh + 1)
            lines.append([[xa_, ya_, 0.0], [xb_, yb_, 0.0]])

            a_mirror, b_mirror = mirror_points_line([[xa_, ya_, 0.0], [xb_, yb_, 0.0]], line_hor)
            lines.append([a_mirror, b_mirror])
            a_mirror, b_mirror = mirror_points_line([a_mirror, b_mirror], line_ver)
            lines.append([a_mirror, b_mirror])
            a_mirror, b_mirror = mirror_points_line([[xa_, ya_, 0.0], [xb_, yb_, 0.0]], line_ver)
            lines.append([a_mirror, b_mirror])

            if nf < nfans:
                # Vertical Members:
                xc = x0 + dxh * (nh + 1)
                yc = y0 + dyf * nf * (nh + 1) / nhoops
                xd = x0 + dxh * (nh + 1)
                yd = y0 + dyf * (nf + 1) * (nh + 1) / nhoops
                lines.append([[xc, yc, 0.0], [xd, yd, 0.0]])

                c_mirror, d_mirror = mirror_points_line([[xc, yc, 0.0], [xd, yd, 0.0]], line_hor)
                lines.append([c_mirror, d_mirror])
                c_mirror, d_mirror = mirror_points_line([c_mirror, d_mirror], line_ver)
                lines.append([c_mirror, d_mirror])
                c_mirror, d_mirror = mirror_points_line([[xc, yc, 0.0], [xd, yd, 0.0]], line_ver)
                lines.append([c_mirror, d_mirror])

                # Horizontal Members:
                xc_ = x0 + dxf * nf * (nh + 1) / nhoops
                yc_ = y0 + dyh * (nh + 1)
                xd_ = x0 + dxf * (nf + 1) * (nh + 1) / nhoops
                yd_ = y0 + dyh * (nh + 1)
                lines.append([[xc_, yc_, 0.0], [xd_, yd_, 0.0]])

                c_mirror, d_mirror = mirror_points_line([[xc_, yc_, 0.0], [xd_, yd_, 0.0]], line_hor)
                lines.append([c_mirror, d_mirror])
                c_mirror, d_mirror = mirror_points_line([c_mirror, d_mirror], line_ver)
                lines.append([c_mirror, d_mirror])
                c_mirror, d_mirror = mirror_points_line([[xc_, yc_, 0.0], [xd_, yd_, 0.0]], line_ver)
                lines.append([c_mirror, d_mirror])

    form = Mesh.from_lines(lines, delete_boundary_face=True)

    return form


def create_ortho_mesh(x_span=(0.0, 10.0), y_span=(0.0, 10.0), nx=10, ny=10) -> Mesh:
    """Helper to construct a Mesh based on a simple orthogonal discretisation.

    Parameters
    ----------
    x_span : tuple, optional
        Tuple with initial- and end-points of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Tuple with initial- and end-points of the vault in y direction, by default (0.0, 10.0)
    nx : int, optional
        Set the density of the mesh in the x direction, by default 10
    ny : int, optional
        Set the density of the mesh in the y direction, by default 10

    Returns
    -------
    mesh : Mesh
        The Mesh created.
    """

    y1 = float(y_span[1])
    y0 = float(y_span[0])
    x1 = float(x_span[1])
    x0 = float(x_span[0])
    x_span_length = x1 - x0
    y_span_length = y1 - y0
    dx = float(x_span_length / nx)
    dy = float(y_span_length / ny)

    vertices = []
    faces = []

    for j in range(ny + 1):
        for i in range(nx + 1):
            xi = x0 + dx * i
            yi = y0 + dy * j
            vertices.append([xi, yi, 0.0])
            if i < nx and j < ny:
                p1 = j * (nx + 1) + i
                p2 = j * (nx + 1) + i + 1
                p3 = (j + 1) * (nx + 1) + i + 1
                p4 = (j + 1) * (nx + 1) + i
                face = [p1, p2, p3, p4, p1]
                faces.append(face)

    form = Mesh.from_vertices_and_faces(vertices, faces)

    return form


def create_parametric_fan_mesh(x_span=(0.0, 10.0), y_span=(0.0, 10.0), n=10, lambd=0.5) -> Mesh:
    """Create a parametric mesh based on the inclination lambda of the arches

    Parameters
    ----------
    x_span : tuple, optional
        Tuple with initial- and end-points of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Tuple with initial- and end-points of the vault in y direction, by default (0.0, 10.0)
    n : int, optional
        Set the density of the mesh, by default 10
    lambd : float, optional
        Inclination of the arches in the diagram (0.0 will result in cross and 1.0 in fan diagrams), by default 0.5

    Returns
    -------
    mesh : Mesh
        The Mesh created.

    Notes
    -----
        Diagram implemented after `N. A. Nodargi et al., 2022 <https://doi.org/10.1016/j.engstruct.2022.114878>`_.
    """
    if 0.0 > lambd or lambd > 1.0:
        raise ValueError("Lambda should be between 0.0 and 1.0")

    lx = x_span[1] - x_span[0]
    ly = y_span[1] - y_span[0]

    x0, x1 = x_span[0], x_span[1]
    y0, y1 = y_span[0], y_span[1]

    xc = (x1 + x0) / 2
    yc = (y1 + y0) / 2
    division_x = n
    division_y = n
    dx = float(lx / division_x)
    dy = float(ly / division_y)
    nx = int(division_x / 2)
    line_hor = [[x0, yc, 0.0], [xc, yc, 0.0]]
    line_ver = [[xc, y0, 0.0], [xc, yc, 0.0]]

    lines = []

    for i in range(nx + 1):
        j = i

        xa = xc
        ya = yc - dy * j

        xa_ = xc - dx * i
        ya_ = yc

        xb = (xa_ - x0) * (1 - lambd) + x0
        yb = (ya - y0) * (1 - lambd) + y0

        xd = xa_
        yd = y0 + ly / lx * (xa_ - x0)

        xe = xd
        ye = y0

        xe_ = x0
        ye_ = yd

        if distance_point_point_xy([xa, ya], [xb, yb]):
            lines.append([[xa, ya, 0.0], [xb, yb, 0.0]])
            append_mirrored_lines([[xa, ya, 0.0], [xb, yb, 0.0]], lines, line_hor, line_ver)

        if distance_point_point_xy([xa_, ya_], [xb, yb]):
            lines.append([[xa_, ya_, 0.0], [xb, yb, 0.0]])
            append_mirrored_lines([[xa_, ya_, 0.0], [xb, yb, 0.0]], lines, line_hor, line_ver)

        if distance_point_point_xy([xd, yd], [xe, ye]):
            lines.append([[xd, yd, 0.0], [xe, ye, 0.0]])
            append_mirrored_lines([[xd, yd, 0.0], [xe, ye, 0.0]], lines, line_hor, line_ver)

        if distance_point_point_xy([xd, yd], [xe_, ye_]):
            lines.append([[xd, yd, 0.0], [xe_, ye_, 0.0]])
            append_mirrored_lines([[xd, yd, 0.0], [xe_, ye_, 0.0]], lines, line_hor, line_ver)

        if i == 0:
            if distance_point_point_xy([x0, y0], [xb, yb]):
                lines.append([[x0, y0, 0.0], [xb, yb, 0.0]])
                append_mirrored_lines([[x0, y0, 0.0], [xb, yb, 0.0]], lines, line_hor, line_ver)

    clean_lines = split_intersection_lines(lines)

    mesh = Mesh.from_lines(clean_lines, delete_boundary_face=True)

    mesh.weld()

    return mesh
