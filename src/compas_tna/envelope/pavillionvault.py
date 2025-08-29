import math

from numpy import array
from numpy import ones
from numpy import zeros

from compas.datastructures import Mesh
from compas_tna.diagrams.diagram_rectangular import create_cross_mesh
from compas_tna.envelope.envelope import Envelope


def create_pavillionvault_envelope(
    x_span: tuple = (0.0, 10.0),
    y_span: tuple = (0.0, 10.0),
    thickness: float = 0.50,
    min_lb: float = 0.0,
    n: int = 100,
    spr_angle: float = 0.0,
):
    """Create an envelope for a pavillion vault geometry with given parameters.

    Parameters
    ----------
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
    spr_angle : float, optional
        Springing angle, by default 0.0

    Returns
    -------
    intrados : Mesh
        Intrados mesh
    extrados : Mesh
        Extrados mesh
    middle : Mesh
        Middle mesh
    """
    # Create base topology
    base_topology = create_cross_mesh(x_span=x_span, y_span=y_span, n=n)
    xyz0, faces_i = base_topology.to_vertices_and_faces()
    xi, yi, _ = array(xyz0).transpose()

    # Create middle surface
    zt = pavillionvault_middle_update(xi, yi, x_span=x_span, y_span=y_span, spr_angle=spr_angle, tol=1e-6)
    xyzt = array([xi, yi, zt.flatten()]).transpose()
    middle = Mesh.from_vertices_and_faces(xyzt, faces_i)
    middle.update_default_vertex_attributes(thickness=thickness)

    # Create upper and lower bounds
    zub, zlb = pavillionvault_ub_lb_update(
        xi,
        yi,
        thickness,
        min_lb,
        x_span=x_span,
        y_span=y_span,
        spr_angle=spr_angle,
        tol=1e-6,
    )
    xyzub = array([xi, yi, zub.flatten()]).transpose()
    xyzlb = array([xi, yi, zlb.flatten()]).transpose()

    extrados = Mesh.from_vertices_and_faces(xyzub, faces_i)
    intrados = Mesh.from_vertices_and_faces(xyzlb, faces_i)

    return intrados, extrados, middle


def pavillionvault_middle_update(x, y, x_span=(0.0, 10.0), y_span=(0.0, 10.0), spr_angle=0.0, tol=1e-6):
    """Update middle of a pavillion vault based in the parameters

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    spr_angle : float, optional
        Springing angle, by default 0.0
    tol : float, optional
        Tolerance, by default 1e-6

    Returns
    -------
    z : array
        Values of the middle surface in the points
    """

    x0, x1 = x_span
    y0, y1 = y_span

    if spr_angle == 0.0:
        z_ = 0.0
    else:
        alpha = 1 / math.cos(math.radians(spr_angle))
        z_ = (x1 - x0) / 2 * math.tan(math.radians(spr_angle))
        L = x1 * alpha
        Ldiff = L - x1
        x0, x1 = -Ldiff / 2, x1 + Ldiff / 2
        y0, y1 = -Ldiff / 2, y1 + Ldiff / 2

    rx = (x1 - x0) / 2
    ry = (y1 - y0) / 2

    z = zeros((len(x), 1))

    for i in range(len(x)):
        xi, yi = x[i], y[i]
        if (yi - y0) <= y1 / x1 * (xi - x0) + tol and (yi - y0) <= (y1 - y0) - (xi - x0) + tol:  # Q1
            z[i] = math.sqrt((ry) ** 2 - ((yi - y0) - ry) ** 2) - z_
        elif (yi - y0) >= y1 / x1 * (xi - x0) - tol and (yi - y0) >= (y1 - y0) - (xi - x0) - tol:  # Q3
            z[i] = math.sqrt((ry) ** 2 - ((yi - y0) - ry) ** 2) - z_
        elif (yi - y0) <= y1 / x1 * (xi - x0) + tol and (yi - y0) >= (y1 - y0) - (xi - x0) - tol:  # Q2
            z[i] = math.sqrt((rx) ** 2 - ((xi - x0) - rx) ** 2) - z_
        elif (yi - y0) >= y1 / x1 * (xi - x0) - tol and (yi - y0) <= (y1 - y0) - (xi - x0) + tol:  # Q4
            z[i] = math.sqrt((rx) ** 2 - ((xi - x0) - rx) ** 2) - z_
        else:
            print("Error Q. (x,y) = ({0},{1})".format(xi, yi))

    return z


def pavillionvault_ub_lb_update(x, y, thk, min_lb, x_span=(0.0, 10.0), y_span=(0.0, 10.0), spr_angle=0.0, tol=1e-6):
    """Update upper and lower bounds of a pavillionvault based in the parameters

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the vault
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    spr_angle : float, optional
        Springing angle, by default 0.0
    tol : float, optional
        Tolerance, by default 1e-6

    Returns
    -------
    ub : array
        Values of the upper bound in the points
    lb : array
        Values of the lower bound in the points
    """

    x0, x1 = x_span
    y0, y1 = y_span

    if spr_angle == 0.0:
        z_ = 0.0
    else:
        alpha = 1 / math.cos(math.radians(spr_angle))
        z_ = (x1 - x0) / 2 * math.tan(math.radians(spr_angle))
        L = x1 * alpha
        Ldiff = L - x1
        x0, x1 = -Ldiff / 2, x1 + Ldiff / 2
        y0, y1 = -Ldiff / 2, y1 + Ldiff / 2

    y1_ub = y1 + thk / 2
    y0_ub = y0 - thk / 2
    x1_ub = x1 + thk / 2
    x0_ub = x0 - thk / 2

    y1_lb = y1 - thk / 2
    y0_lb = y0 + thk / 2
    x1_lb = x1 - thk / 2
    x0_lb = x0 + thk / 2

    rx_ub = (x1_ub - x0_ub) / 2
    ry_ub = (y1_ub - y0_ub) / 2
    rx_lb = (x1_lb - x0_lb) / 2
    ry_lb = (y1_lb - y0_lb) / 2

    ub = ones((len(x), 1))
    lb = ones((len(x), 1)) * -min_lb

    for i in range(len(x)):
        xi, yi = x[i], y[i]
        intrados_null = False
        if yi > y1_lb or xi > x1_lb or xi < x0_lb or yi < y0_lb:
            intrados_null = True
        if (yi - y0) <= y1 / x1 * (xi - x0) + tol and (yi - y0) <= (y1 - y0) - (xi - x0) + tol:  # Q1
            ub[i] = math.sqrt((ry_ub) ** 2 - ((yi - y0_ub) - ry_ub) ** 2) - z_
            if not intrados_null:
                lb[i] = math.sqrt((ry_lb) ** 2 - ((yi - y0_lb) - ry_lb) ** 2) - z_
        elif (yi - y0) >= y1 / x1 * (xi - x0) - tol and (yi - y0) >= (y1 - y0) - (xi - x0) - tol:  # Q3
            ub[i] = math.sqrt((ry_ub) ** 2 - ((yi - y0_ub) - ry_ub) ** 2) - z_
            if not intrados_null:
                lb[i] = math.sqrt((ry_lb) ** 2 - ((yi - y0_lb) - ry_lb) ** 2) - z_
        elif (yi - y0) <= y1 / x1 * (xi - x0) + tol and (yi - y0) >= (y1 - y0) - (xi - x0) - tol:  # Q2
            ub[i] = math.sqrt((rx_ub) ** 2 - ((xi - x0_ub) - rx_ub) ** 2) - z_
            if not intrados_null:
                lb[i] = math.sqrt((rx_lb) ** 2 - ((xi - x0_lb) - rx_lb) ** 2) - z_
        elif (yi - y0) >= y1 / x1 * (xi - x0) - tol and (yi - y0) <= (y1 - y0) - (xi - x0) + tol:  # Q4
            ub[i] = math.sqrt((rx_ub) ** 2 - ((xi - x0_ub) - rx_ub) ** 2) - z_
            if not intrados_null:
                lb[i] = math.sqrt((rx_lb) ** 2 - ((xi - x0_lb) - rx_lb) ** 2) - z_
        else:
            print("Error Q. (x,y) = ({0},{1})".format(xi, yi))

    return ub, lb


def pavillionvault_dub_dlb(x, y, thk, min_lb, x_span=(0.0, 10.0), y_span=(0.0, 10.0), tol=1e-6):
    """Computes the sensitivities of upper and lower bounds in the x, y coordinates and thickness specified.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the vault
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)
    tol : float, optional
        Tolerance, by default 1e-6

    Returns
    -------
    dub : array
        Values of the sensitivities for the upper bound in the points
    dlb : array
        Values of the sensitivities for the lower bound in the points
    """

    x0, x1 = x_span
    y0, y1 = y_span

    y1_ub = y1 + thk / 2
    y0_ub = y0 - thk / 2
    x1_ub = x1 + thk / 2
    x0_ub = x0 - thk / 2

    y1_lb = y1 - thk / 2
    y0_lb = y0 + thk / 2
    x1_lb = x1 - thk / 2
    x0_lb = x0 + thk / 2

    rx_ub = (x1_ub - x0_ub) / 2
    ry_ub = (y1_ub - y0_ub) / 2
    rx_lb = (x1_lb - x0_lb) / 2
    ry_lb = (y1_lb - y0_lb) / 2

    ub = ones((len(x), 1))
    lb = ones((len(x), 1)) * -min_lb
    dub = zeros((len(x), 1))
    dlb = zeros((len(x), 1))

    for i in range(len(x)):
        xi, yi = x[i], y[i]
        intrados_null = False
        if yi > y1_lb or xi > x1_lb or xi < x0_lb or yi < y0_lb:
            intrados_null = True
        if (yi - y0) <= y1 / x1 * (xi - x0) + tol and (yi - y0) <= (y1 - y0) - (xi - x0) + tol:  # Q1
            ub[i] = math.sqrt((ry_ub) ** 2 - ((yi - y0_ub) - ry_ub) ** 2)
            dub[i] = 1 / 2 * ry_ub / ub[i]
            if not intrados_null:
                lb[i] = math.sqrt((ry_lb) ** 2 - ((yi - y0_lb) - ry_lb) ** 2)
                dlb[i] = -1 / 2 * ry_lb / lb[i]
        elif (yi - y0) >= y1 / x1 * (xi - x0) - tol and (yi - y0) >= (y1 - y0) - (xi - x0) - tol:  # Q3
            ub[i] = math.sqrt((ry_ub) ** 2 - ((yi - y0_ub) - ry_ub) ** 2)
            dub[i] = 1 / 2 * ry_ub / ub[i]
            if not intrados_null:
                lb[i] = math.sqrt((ry_lb) ** 2 - ((yi - y0_lb) - ry_lb) ** 2)
                dlb[i] = -1 / 2 * ry_lb / lb[i]
        elif (yi - y0) <= y1 / x1 * (xi - x0) + tol and (yi - y0) >= (y1 - y0) - (xi - x0) - tol:  # Q2
            ub[i] = math.sqrt((rx_ub) ** 2 - ((xi - x0_ub) - rx_ub) ** 2)
            dub[i] = 1 / 2 * rx_ub / ub[i]
            if not intrados_null:
                lb[i] = math.sqrt((rx_lb) ** 2 - ((xi - x0_lb) - rx_lb) ** 2)
                dlb[i] = -1 / 2 * rx_lb / lb[i]
        elif (yi - y0) >= y1 / x1 * (xi - x0) - tol and (yi - y0) <= (y1 - y0) - (xi - x0) + tol:  # Q4
            ub[i] = math.sqrt((rx_ub) ** 2 - ((xi - x0_ub) - rx_ub) ** 2)
            dub[i] = 1 / 2 * rx_ub / ub[i]
            if not intrados_null:
                lb[i] = math.sqrt((rx_lb) ** 2 - ((xi - x0_lb) - rx_lb) ** 2)
                dlb[i] = -1 / 2 * rx_lb / lb[i]
        else:
            print("Error Q. (x,y) = ({0},{1})".format(xi, yi))

    return dub, dlb  # ub, lb


def pavillionvault_bound_react_update(x, y, thk, fixed, x_span=(0.0, 10.0), y_span=(0.0, 10.0)):
    """Computes the ``b`` of parameter x, y coordinates and thickness specified.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the vault
    fixed : list
        The list with indexes of the fixed vertices
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)

    Returns
    -------
    b : array
        Values of the ``b`` parameter
    """

    x0, x1 = x_span
    y0, y1 = y_span
    b = zeros((len(fixed), 2))

    for i in range(len(fixed)):
        index = fixed[i]
        xi, yi = x[index], y[index]
        if xi == x0:
            b[[i], :] += [-thk / 2, 0]
        elif xi == x1:
            b[i, :] += [+thk / 2, 0]
        if yi == y0:
            b[i, :] += [0, -thk / 2]
        elif yi == y1:
            b[i, :] += [0, +thk / 2]

    return abs(b)


def pavillionvault_db(x, y, thk, fixed, x_span=(0.0, 10.0), y_span=(0.0, 10.0)):
    """Computes the sensitivities of the ``b`` parameter in the x, y coordinates and thickness specified.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the vault
    fixed : list
        The list with indexes of the fixed vertices
    x_span : tuple, optional
        Span of the vault in x direction, by default (0.0, 10.0)
    y_span : tuple, optional
        Span of the vault in y direction, by default (0.0, 10.0)

    Returns
    -------
    db : array
        Values of the sensitivities of the ``b`` parameter in the points
    """

    x0, x1 = x_span
    y0, y1 = y_span
    db = zeros((len(fixed), 2))

    for i in range(len(fixed)):
        index = fixed[i]
        xi, yi = x[index], y[index]
        if xi == x0:
            db[i, :] += [-1 / 2, 0]
        elif xi == x1:
            db[i, :] += [+1 / 2, 0]
        if yi == y0:
            db[i, :] += [0, -1 / 2]
        elif yi == y1:
            db[i, :] += [0, +1 / 2]

    return abs(db)


class PavillionVaultEnvelope(Envelope):
    def __init__(
        self,
        x_span: tuple = (0.0, 10.0),
        y_span: tuple = (0.0, 10.0),
        thickness: float = 0.50,
        min_lb: float = 0.0,
        n: int = 100,
        spr_angle: float = 0.0,
        **kwargs,
    ):
        super().__init__(thickness=thickness, **kwargs)
        self.x_span = x_span
        self.y_span = y_span
        self.min_lb = min_lb
        self.n = n
        self.spr_angle = spr_angle

        intrados, extrados, middle = create_pavillionvault_envelope(x_span=x_span, y_span=y_span, thickness=thickness, min_lb=min_lb, n=n, spr_angle=spr_angle)

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
        data["spr_angle"] = self.spr_angle
        return data

    def __str__(self):
        return f"PavillionVaultEnvelope(name={self.name})"

    def callable_middle(self, x, y):
        return pavillionvault_middle_update(x, y, x_span=self.x_span, y_span=self.y_span, spr_angle=self.spr_angle, tol=1e-6)

    def callable_ub_lb(self, x, y, thickness):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pavillionvault_ub_lb_update(x, y, thickness, self.min_lb, x_span=self.x_span, y_span=self.y_span, spr_angle=self.spr_angle, tol=1e-6)

    def callable_dub_dlb(self, x, y, thickness):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pavillionvault_dub_dlb(x, y, thickness, self.min_lb, x_span=self.x_span, y_span=self.y_span, tol=1e-6)

    def callable_bound_react(self, x, y, thickness, fixed):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pavillionvault_bound_react_update(x, y, thickness, fixed, x_span=self.x_span, y_span=self.y_span, tol=1e-6)

    def callable_db(self, x, y, thickness, fixed):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return pavillionvault_db(x, y, thickness, fixed, x_span=self.x_span, y_span=self.y_span, tol=1e-6)
