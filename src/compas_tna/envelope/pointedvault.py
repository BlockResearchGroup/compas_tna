import math

from numpy import array
from numpy import ones
from numpy import zeros

from compas.datastructures import Mesh
from compas_tna.diagrams.diagram_rectangular import create_cross_mesh
from compas_tna.envelope.envelope import Envelope


def create_pointedvault_envelope(
    x_span: tuple = (0.0, 10.0),
    y_span: tuple = (0.0, 10.0),
    thickness: float = 0.50,
    min_lb: float = 0.0,
    n: int = 100,
    hc: float = 8.0,
    he: list = None,
    hm: list = None,
):
    """Create an envelope for a pointed cross vault geometry with given parameters.

    Parameters
    ----------
    cls : class
        The Envelope class to use for creating the envelope.
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    thickness : float, optional
        Thickness of the vault, by default 0.50
    min_lb : float, optional
        Parameter for lower bound in nodes in the boundary, by default 0.0
    n : int, optional
        Number of vertices for the mesh, by default 100
    hc : float, optional
        Height in the middle point of the vault, by default 8.0
    he : list, optional
        Height of the opening mid-span for each of the quadrants, by default None
    hm : list, optional
        Height of each quadrant center (spadrel), by default None
    rho : float, optional
        Density of the material in kN/m³, by default 25.0

    Returns
    -------
    envelope : Envelope
        The created envelope with intrados, extrados, and middle meshes.
    """
    # Create base topology
    base_topology = create_cross_mesh(x_span=x_span, y_span=y_span, n=n)
    xyz0, faces_i = base_topology.to_vertices_and_faces()
    xi, yi, _ = array(xyz0).transpose()

    # Create middle surface
    zt = pointedvault_middle_update(xi, yi, min_lb, x_span=x_span, y_span=y_span, hc=hc, he=he, hm=hm, tol=1e-6)
    xyzt = array([xi, yi, zt.flatten()]).transpose()
    middle = Mesh.from_vertices_and_faces(xyzt, faces_i)
    middle.update_default_vertex_attributes(thickness=thickness)

    # Create upper and lower bounds
    zub, zlb = pointedvault_ub_lb_update(
        xi,
        yi,
        thickness,
        min_lb,
        x_span=x_span,
        y_span=y_span,
        hc=hc,
        he=he,
        hm=hm,
        tol=1e-6,
    )
    xyzub = array([xi, yi, zub.flatten()]).transpose()
    xyzlb = array([xi, yi, zlb.flatten()]).transpose()

    extrados = Mesh.from_vertices_and_faces(xyzub, faces_i)
    intrados = Mesh.from_vertices_and_faces(xyzlb, faces_i)

    return intrados, extrados, middle


def pointedvault_middle_update(
    x,
    y,
    min_lb,
    x_span=(0.0, 10.0),
    y_span=(0.0, 10.0),
    hc=8.0,
    he=None,
    hm=None,
    tol=1e-6,
):
    """Update middle of a pointed vault based in the parameters

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    hc : float, optional
        Height in the middle point of the vault, by default 8.0
    he : [float, float, float, float], optional
        Height of the opening mid-span for each of the quadrants, by default None
    hm : [float, float, float, float], optional
        Height of each quadrant center (spadrel), by default None
    tol : float, optional
        Tolerance, by default 1e-6

    Returns
    -------
    middle : array
        Values of the middle surface in the points
    """

    y1 = y_span[1]
    y0 = y_span[0]
    x1 = x_span[1]
    x0 = x_span[0]
    lx = x1 - x0
    ly = y1 - y0

    if he and hm is None:
        h1, k1, r1 = _circle_3points_xy([x0, he[1]], [(x1 + x0) / 2, hc], [x1, he[0]])
        h2, k2, r2 = h1, k1, r1
        h3, k3, r3 = _circle_3points_xy([y0, he[3]], [(y1 + y0) / 2, hc], [y1, he[2]])
        h4, k4, r4 = h3, k3, r3
    elif hm and he:
        h1, k1, r1 = _circle_3points_xy([(x1 + x0) / 2, hc], [3 * (x1 + x0) / 4, hm[0]], [x1, he[0]])
        h2, k2, r2 = _circle_3points_xy([(x1 + x0) / 2, hc], [1 * (x1 + x0) / 4, hm[1]], [x0, he[1]])
        h3, k3, r3 = _circle_3points_xy([(y1 + y0) / 2, hc], [3 * (y1 + y0) / 4, hm[2]], [y1, he[2]])
        h4, k4, r4 = _circle_3points_xy([(y1 + y0) / 2, hc], [1 * (y1 + y0) / 4, hm[3]], [y0, he[3]])

    middle = zeros((len(x), 1))

    for i in range(len(x)):
        xi, yi = x[i], y[i]

        if yi <= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) + tol and yi >= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) - tol:  # Q1
            # Equation (xi - hx) ** 2 + (hi - kx) ** 2 = rx **2 to find the height of the pointed part (middle of quadrant) with that height one find the equivalent radius
            if he:
                hi = k1 + math.sqrt(r1**2 - (xi - h1) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, ly)  # This in the equation ri ** 2 =  (xi - xc_) ** 2 + (zi - zc_) ** 2  -> zc = 0.0 and xc_ = (x0 + x1)/2
            if yi <= (y1 + y0) / 2:
                zi = _sqrt((ri) ** 2 - (yi - (y0 + ri)) ** 2)
            else:
                zi = _sqrt((ri) ** 2 - (yi - (y1 - ri)) ** 2)

        elif yi >= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) - tol and yi >= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) - tol:  # Q3
            # Equation (xi - hy) ** 2 + (hi - ky) ** 2 = ry **2 to find the height of the pointed part (middle of quadrant) with that height one find the equivalent radius
            if he:
                hi = k3 + math.sqrt(r3**2 - (yi - h3) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, lx)  # This in the equation ri ** 2 =  (xi - xc_) ** 2 + (zi - zc_) ** 2  -> zc = 0.0 and xc_ = (x0 + x1)/2
            if xi <= (x0 + x1) / 2:
                zi = _sqrt((ri) ** 2 - (xi - (x0 + ri)) ** 2)
            else:
                zi = _sqrt((ri) ** 2 - (xi - (x1 - ri)) ** 2)

        elif yi >= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) - tol and yi <= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) + tol:  # Q2
            if he:
                hi = k2 + math.sqrt(r2**2 - (xi - h2) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, ly)
            if yi <= (y1 + y0) / 2:
                zi = _sqrt((ri) ** 2 - (yi - (y0 + ri)) ** 2)
            else:
                zi = _sqrt((ri) ** 2 - (yi - (y1 - ri)) ** 2)

        elif yi <= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) + tol and yi <= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) + tol:  # Q4
            if he:
                hi = k4 + math.sqrt(r4**2 - (yi - h4) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, lx)
            if xi <= (x0 + x1) / 2:
                zi = _sqrt((ri) ** 2 - (xi - (x0 + ri)) ** 2)
            else:
                zi = _sqrt((ri) ** 2 - (xi - (x1 - ri)) ** 2)

        else:
            print("Vertex did not belong to any Q. (x,y) = ({0},{1})".format(xi, yi))

        middle[i] = zi

    return middle


def pointedvault_ub_lb_update(
    x,
    y,
    thk,
    min_lb,
    x_span=(0.0, 10.0),
    y_span=(0.0, 10.0),
    hc=8.0,
    he=None,
    hm=None,
    tol=1e-6,
):
    """Update upper and lower bounds of a pointed vault based in the parameters

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the arch
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    hc : float, optional
        Height in the middle point of the vault, by default 8.0
    he : [float, float, float, float], optional
        Height of the opening mid-span for each of the quadrants, by default None
    hm : [float, float, float, float], optional
        Height of each quadrant center (spadrel), by default None
    tol : float, optional
        Tolerance, by default 1e-6

    Returns
    -------
    ub : array
        Values of the upper bound in the points
    lb : array
        Values of the lower bound in the points
    """

    y1 = y_span[1]
    y0 = y_span[0]
    x1 = x_span[1]
    x0 = x_span[0]

    y1_lb = y1 - thk / 2
    y0_lb = y0 + thk / 2
    x1_lb = x1 - thk / 2
    x0_lb = x0 + thk / 2

    lx = x1 - x0
    ly = y1 - y0

    if he:
        he_ub = he.copy()
        he_lb = he.copy()
        for i in range(len(he)):
            he_ub[i] += thk / 2
            he_lb[i] -= thk / 2
    if hm:
        raise NotImplementedError()

    if he and hm is None:
        h1, k1, r1 = _circle_3points_xy([x0, he[1]], [(x1 + x0) / 2, hc], [x1, he[0]])
        h2, k2, r2 = h1, k1, r1
        h3, k3, r3 = _circle_3points_xy([y0, he[3]], [(y1 + y0) / 2, hc], [y1, he[2]])
        h4, k4, r4 = h3, k3, r3

    ub = ones((len(x), 1))
    lb = ones((len(x), 1)) * -min_lb

    for i in range(len(x)):
        xi, yi = x[i], y[i]

        if yi <= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) + tol and yi >= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) - tol:  # Q1
            if he:
                hi = k1 + math.sqrt(r1**2 - (xi - h1) ** 2)
            else:
                hi = hc

            ri = _find_r_given_h_l(hi, ly)
            ri_ub = ri + thk / 2
            ri_lb = ri - thk / 2
            if yi <= (y1 + y0) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y1 - ri)) ** 2)

        elif yi >= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) - tol and yi >= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) - tol:  # Q3
            if he:
                hi = k3 + math.sqrt(r3**2 - (yi - h3) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, lx)
            ri_ub = ri + thk / 2
            ri_lb = ri - thk / 2
            if xi <= (x0 + x1) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x1 - ri)) ** 2)

        elif yi >= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) - tol and yi <= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) + tol:  # Q2
            if he:
                hi = k2 + math.sqrt(r2**2 - (xi - h2) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, ly)
            ri_lb = ri - thk / 2
            ri_ub = ri + thk / 2
            if yi <= (y1 + y0) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y1 - ri)) ** 2)

        elif yi <= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) + tol and yi <= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) + tol:  # Q4
            if he:
                hi = k4 + math.sqrt(r4**2 - (yi - h4) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, lx)
            ri_ub = ri + thk / 2
            ri_lb = ri - thk / 2
            if xi <= (x0 + x1) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x1 - ri)) ** 2)
        else:
            print("Vertex did not belong to any Q. (x,y) = ({0},{1})".format(xi, yi))

        if ((yi) > y1_lb and ((xi) > x1_lb or (xi) < x0_lb)) or ((yi) < y0_lb and ((xi) > x1_lb or (xi) < x0_lb)):
            lb[i] = -1 * min_lb

    return ub, lb


def pointedvault_dub_dlb(
    x,
    y,
    thk,
    min_lb,
    x_span=(0.0, 10.0),
    y_span=(0.0, 10.0),
    hc=8.0,
    he=None,
    hm=None,
    tol=1e-6,
):
    """Computes the sensitivities of upper and lower bounds in the x, y coordinates and thickness specified.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the arch
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    hc : float, optional
        Height in the middle point of the vault, by default 8.0
    he : [float, float, float, float], optional
        Height of the opening mid-span for each of the quadrants, by default None
    hm : [float, float, float, float], optional
        Height of each quadrant center (spadrel), by default None
    tol : float, optional
        Tolerance, by default 1e-6

    Returns
    -------
    dub : array
        Values of the sensitivities for the upper bound in the points
    dlb : array
        Values of the sensitivities for the lower bound in the points
    """

    y1 = y_span[1]
    y0 = y_span[0]
    x1 = x_span[1]
    x0 = x_span[0]

    y1_lb = y1 - thk / 2
    y0_lb = y0 + thk / 2
    x1_lb = x1 - thk / 2
    x0_lb = x0 + thk / 2

    lx = x1 - x0
    ly = y1 - y0

    if he:
        he_ub = he.copy()
        he_lb = he.copy()
        for i in range(len(he)):
            he_ub[i] += thk / 2
            he_lb[i] -= thk / 2
    if hm:
        raise NotImplementedError()
        hm_ub = hm.copy()
        hm_lb = hm.copy()
        for i in range(len(hm)):
            hm_ub[i] += thk / 2
            hm_lb[i] -= thk / 2

    if he and hm is None:
        h1, k1, r1 = _circle_3points_xy([x0, he[1]], [(x1 + x0) / 2, hc], [x1, he[0]])
        h2, k2, r2 = h1, k1, r1
        h3, k3, r3 = _circle_3points_xy([y0, he[3]], [(y1 + y0) / 2, hc], [y1, he[2]])
        h4, k4, r4 = h3, k3, r3

    ub = ones((len(x), 1))
    lb = ones((len(x), 1)) * -min_lb
    dub = zeros((len(x), 1))
    dlb = zeros((len(x), 1))

    for i in range(len(x)):
        xi, yi = x[i], y[i]

        if yi <= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) + tol and yi >= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) - tol:  # Q1
            if he:
                hi = k1 + math.sqrt(r1**2 - (xi - h1) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, ly)
            ri_ub = ri + thk / 2
            ri_lb = ri - thk / 2
            if yi <= (y1 + y0) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y1 - ri)) ** 2)
            dub[i] = 1 / 2 * ri_ub / ub[i]
            dlb[i] = -1 / 2 * ri_lb / lb[i]

        elif yi >= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) - tol and yi >= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) - tol:  # Q3
            if he:
                hi = k3 + math.sqrt(r3**2 - (yi - h3) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, lx)
            ri_ub = ri + thk / 2
            ri_lb = ri - thk / 2
            if xi <= (x0 + x1) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x1 - ri)) ** 2)
            dub[i] = 1 / 2 * ri_ub / ub[i]
            dlb[i] = -1 / 2 * ri_lb / lb[i]

        elif yi >= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) - tol and yi <= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) + tol:  # Q2
            if he:
                hi = k2 + math.sqrt(r2**2 - (xi - h2) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, ly)
            ri_lb = ri - thk / 2
            ri_ub = ri + thk / 2
            if yi <= (y1 + y0) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (yi - (y1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (yi - (y1 - ri)) ** 2)
            dub[i] = 1 / 2 * ri_ub / ub[i]
            dlb[i] = -1 / 2 * ri_lb / lb[i]

        elif yi <= y0 + (y1 - y0) / (x1 - x0) * (xi - x0) + tol and yi <= y1 - (y1 - y0) / (x1 - x0) * (xi - x0) + tol:  # Q4
            if he:
                hi = k4 + math.sqrt(r4**2 - (yi - h4) ** 2)
            else:
                hi = hc
            ri = _find_r_given_h_l(hi, lx)
            ri_ub = ri + thk / 2
            ri_lb = ri - thk / 2
            if xi <= (x0 + x1) / 2:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x0 + ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x0 + ri)) ** 2)
            else:
                ub[i] = _sqrt((ri_ub) ** 2 - (xi - (x1 - ri)) ** 2)
                lb[i] = _sqrt((ri_lb) ** 2 - (xi - (x1 - ri)) ** 2)
            dub[i] = 1 / 2 * ri_ub / ub[i]
            dlb[i] = -1 / 2 * ri_lb / lb[i]
        else:
            print("Vertex did not belong to any Q. (x,y) = ({0},{1})".format(xi, yi))

        if ((yi) > y1_lb and ((xi) > x1_lb or (xi) < x0_lb)) or ((yi) < y0_lb and ((xi) > x1_lb or (xi) < x0_lb)):
            lb[i] = -1 * min_lb
            dlb[i] = 0.0

    return dub, dlb  # ub, lb


def pointedvault_bound_react_update(
    x,
    y,
    thk,
    min_lb,
    x_span=(0.0, 10.0),
    y_span=(0.0, 10.0),
    hc=8.0,
    he=None,
    hm=None,
    tol=1e-6,
):
    """Compute the bounds on the reaction vector of the pointed cross vault."""
    pass


def pointedvault_db(
    x,
    y,
    thk,
    min_lb,
    x_span=(0.0, 10.0),
    y_span=(0.0, 10.0),
    hc=8.0,
    he=None,
    hm=None,
    tol=1e-6,
):
    """Compute the sensitivities of the bounds on the reaction vector of the pointed cross vault."""
    pass


def _find_r_given_h_l(h, length):
    r = h**2 / length + length / 4

    return r


def _circle_3points_xy(p1, p2, p3):
    x1 = p1[0]
    z1 = p1[1]
    x2 = p2[0]
    z2 = p2[1]
    x3 = p3[0]
    z3 = p3[1]

    x12 = x1 - x2
    x13 = x1 - x3
    z12 = z1 - z2
    z13 = z1 - z3
    z31 = z3 - z1
    z21 = z2 - z1
    x31 = x3 - x1
    x21 = x2 - x1

    sx13 = x1**2 - x3**2
    sz13 = z1**2 - z3**2
    sx21 = x2**2 - x1**2
    sz21 = z2**2 - z1**2

    f = ((sx13) * (x12) + (sz13) * (x12) + (sx21) * (x13) + (sz21) * (x13)) / (2 * ((z31) * (x12) - (z21) * (x13)))
    g = ((sx13) * (z12) + (sz13) * (z12) + (sx21) * (z13) + (sz21) * (z13)) / (2 * ((x31) * (z12) - (x21) * (z13)))
    c = -(x1**2) - z1**2 - 2 * g * x1 - 2 * f * z1
    h = -g
    k = -f
    r2 = h * h + k * k - c
    r = math.sqrt(r2)

    return h, k, r


def _sqrt(x):
    try:
        sqrt_x = math.sqrt(x)
    except BaseException:
        if x > -10e4:
            sqrt_x = math.sqrt(abs(x))
        else:
            sqrt_x = 0.0
    return sqrt_x


class PointedVaultEnvelope(Envelope):
    def __init__(
        self,
        x_span: tuple = (0.0, 10.0),
        y_span: tuple = (0.0, 10.0),
        thickness: float = 0.50,
        min_lb: float = 0.0,
        n: int = 100,
        hc: float = 5.0,
        he: list = None,
        hm: list = None,
        **kwargs,
    ):
        super().__init__(thickness=thickness, **kwargs)
        self.x_span = x_span
        self.y_span = y_span
        self.min_lb = min_lb
        self.n = n
        self.hc = hc
        self.he = he
        self.hm = hm

        intrados, extrados, middle = create_pointedvault_envelope(
            x_span=x_span,
            y_span=y_span,
            thickness=thickness,
            min_lb=min_lb,
            n=n,
            hc=hc,
            he=he,
            hm=hm,
        )
        self.intrados = intrados
        self.extrados = extrados
        self.middle = middle

    @property
    def __data__(self):
        data = super().__data__
        data["x_span"] = self.x_span
        data["y_span"] = self.y_span
        data["min_lb"] = self.min_lb
        data["n"] = self.n
        data["hc"] = self.hc
        data["he"] = self.he
        data["hm"] = self.hm
        return data

    def __str__(self):
        return f"PointedVaultEnvelope(name={self.name})"

    def callable_middle(self, x, y):
        return pointedvault_middle_update(x, y, self.min_lb, self.x_span, self.y_span, self.hc, self.he, self.hm)

    def callable_ub_lb(self, x, y, thickness):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pointedvault_ub_lb_update(x, y, thickness, self.min_lb, self.x_span, self.y_span, self.hc, self.he, self.hm)

    def callable_dub_dlb(self, x, y, thickness):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pointedvault_dub_dlb(x, y, thickness, self.min_lb, self.x_span, self.y_span, self.hc, self.he, self.hm)

    def callable_bound_react(self, x, y, thickness, fixed):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pointedvault_bound_react_update(x, y, thickness, self.min_lb, self.x_span, self.y_span, self.hc, self.he, self.hm)

    def callable_db(self, x, y, thickness, fixed):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pointedvault_db(x, y, thickness, self.min_lb, self.x_span, self.y_span, self.hc, self.he, self.hm)
