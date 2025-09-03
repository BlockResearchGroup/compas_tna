import math

from numpy import array
from numpy import ones
from numpy import zeros

from compas.datastructures import Mesh
from compas_tna.diagrams.diagram_circular import create_circular_radial_spaced_mesh
from compas_tna.envelope.parametricenvelope import ParametricEnvelope


def dome_envelope(
    center: tuple = (5.0, 5.0),
    radius: float = 5.0,
    thickness: float = 0.50,
    min_lb: float = 0.0,
    n_hoops: int = 24,
    n_parallels: int = 40,
    r_oculus: float = 0.0,
):
    """Create an envelope for a dome geometry with given parameters.

    Parameters
    ----------
    center : tuple, optional
        x, y coordinates of the center of the dome, by default (5.0, 5.0)
    radius : float, optional
        The radius of the dome, by default 5.0
    thickness : float, optional
        Thickness of the dome, by default 0.50
    min_lb : float, optional
        Parameter for lower bound in nodes in the boundary, by default 0.0
    n_hoops : int, optional
        Number of hoops for the mesh, by default 24
    n_parallels : int, optional
        Number of parallels for the mesh, by default 40
    r_oculus : float, optional
        Radius of the oculus (opening at the top), by default 0.0

    Returns
    -------
    middle : Mesh
        Middle mesh
    intrados : Mesh
        Intrados mesh
    extrados : Mesh
        Extrados mesh
    """
    # Create meshes for different radii
    for radius_current in [radius, radius - thickness / 2, radius + thickness / 2]:
        base_topology = create_circular_radial_spaced_mesh(
            center=center,
            radius=radius_current,
            n_hoops=n_hoops,
            n_parallels=n_parallels,
            r_oculus=r_oculus,
        )
        xyz0, faces_i = base_topology.to_vertices_and_faces()
        xi, yi, _ = array(xyz0).transpose()
        zt = dome_middle(xi, yi, radius_current, center=center)
        xyzt = array([xi, yi, zt.flatten()]).transpose()

        if radius_current == radius:
            middle = Mesh.from_vertices_and_faces(xyzt, faces_i)
        elif radius_current == radius - thickness / 2:
            intrados = Mesh.from_vertices_and_faces(xyzt, faces_i)
        elif radius_current == radius + thickness / 2:
            extrados = Mesh.from_vertices_and_faces(xyzt, faces_i)

    # Set thickness attributes
    middle.update_default_vertex_attributes(thickness=thickness)
    intrados.update_default_vertex_attributes(thickness=thickness)
    extrados.update_default_vertex_attributes(thickness=thickness)

    return intrados, extrados, middle


def dome_middle(x, y, radius, center=(5.0, 5.0)):
    """Compute middle of the dome based on the parameters.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    radius : float, optional
        The radius of the dome, by default 5.0
    center : tuple, optional
        x, y coordinates of the center of the dome, by default (5.0, 5.0)

    Returns
    -------
    zt : array
        Values of the middle surface in the points
    """

    xc = center[0]
    yc = center[1]
    zt = ones((len(x), 1))

    for i in range(len(x)):
        zt2 = radius**2 - (x[i] - xc) ** 2 - (y[i] - yc) ** 2
        if zt2 > 0:
            zt[i] = math.sqrt(zt2)
        else:
            zt[i] = 0.0

    return zt


def dome_bounds(x, y, thk, min_lb, center=(5.0, 5.0), radius=5.0):
    """Compute upper and lower bounds of the dome based on the parameters.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the dome
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    center : tuple, optional
        x, y coordinates of the center of the dome, by default (5.0, 5.0)
    radius : float, optional
        The radius of the dome, by default 5.0

    Returns
    -------
    ub : array
        Values of the upper bound in the points
    lb : array
        Values of the lower bound in the points
    """

    xc = center[0]
    yc = center[1]
    ri = radius - thk / 2
    re = radius + thk / 2
    ub = ones((len(x), 1))
    lb = ones((len(x), 1)) * -min_lb

    for i in range(len(x)):
        zi2 = ri**2 - (x[i] - xc) ** 2 - (y[i] - yc) ** 2
        ze2 = re**2 - (x[i] - xc) ** 2 - (y[i] - yc) ** 2
        ub[i] = math.sqrt(ze2)
        if zi2 > 0.0:
            lb[i] = math.sqrt(zi2)

    return ub, lb


def dome_bounds_derivatives(x, y, thk, min_lb, center=(5.0, 5.0), radius=5.0):
    """Compute sensitivities of upper and lower bounds of the dome based on the parameters.

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the dome
    min_lb : float
        Parameter for lower bound in nodes in the boundary
    center : tuple, optional
        x, y coordinates of the center of the dome, by default (5.0, 5.0)
    radius : float, optional
        The radius of the dome, by default 5.0

    Returns
    -------
    dub : array
        Values of the sensitivities of upper bound in the points
    dlb : array
        Values of the sensitivities of lower bound in the points
    """

    xc = center[0]
    yc = center[1]
    ri = radius - thk / 2
    re = radius + thk / 2
    dub = zeros((len(x), 1))
    dlb = zeros((len(x), 1))
    dubdx = zeros((len(x), len(x)))
    dubdy = zeros((len(x), len(x)))
    dlbdx = zeros((len(x), len(x)))
    dlbdy = zeros((len(x), len(x)))

    for i in range(len(x)):
        zi2 = ri**2 - (x[i] - xc) ** 2 - (y[i] - yc) ** 2
        ze2 = re**2 - (x[i] - xc) ** 2 - (y[i] - yc) ** 2
        ze = math.sqrt(ze2)
        dub[i] = 1 / 2 * re / ze
        dubdx[i, i] = 1 / 2 / ze * -2 * (x[i] - xc)
        dubdy[i, i] = 1 / 2 / ze * -2 * (y[i] - yc)
        if zi2 > 0.0:
            zi = math.sqrt(zi2)
            dlb[i] = -1 / 2 * ri / zi
            dlbdx[i, i] = 1 / 2 / zi * -2 * (x[i] - xc)
            dlbdy[i, i] = 1 / 2 / zi * -2 * (y[i] - yc)

    return dub, dlb


def dome_bound_react(x, y, thk, fixed, center=(5.0, 5.0), radius=5.0):
    """Computes the reaction bounds of a dome for a given thickness

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the dome
    fixed : list
        List with indexes of the fixed vertices
    center : tuple, optional
        x, y coordinates of the center of the dome, by default (5.0, 5.0)
    radius : float, optional
        The radius of the dome, by default 5.0

    Returns
    -------
    b : array
        The reaction bounds
    """

    [xc, yc] = center[:2]
    b = zeros((len(fixed), 2))

    for i in range(len(fixed)):
        i_ = fixed[i]
        theta = math.atan2((y[i_] - yc), (x[i_] - xc))
        x_ = abs(thk / 2 * math.cos(theta))
        y_ = abs(thk / 2 * math.sin(theta))
        b[i, 0] = x_
        b[i, 1] = y_

    return b


def dome_bound_react_derivatives(x, y, thk, fixed, center=(5.0, 5.0), radius=5.0):
    """Computes the reaction bounds derivatives of a dome for a given thickness

    Parameters
    ----------
    x : list
        x-coordinates of the points
    y : list
        y-coordinates of the points
    thk : float
        Thickness of the dome
    fixed : list
        List with indexes of the fixed vertices
    center : tuple, optional
        x, y coordinates of the center of the dome, by default (5.0, 5.0)
    radius : float, optional
        The radius of the dome, by default 5.0

    Returns
    -------
    db : array
        The sensitivity of the reaction bounds
    """

    [xc, yc] = center[:2]
    db = zeros((len(fixed), 2))

    for i in range(len(fixed)):
        i_ = fixed[i]
        theta = math.atan2((y[i_] - yc), (x[i_] - xc))
        x_ = abs(1 / 2 * math.cos(theta))
        y_ = abs(1 / 2 * math.sin(theta))
        db[i, :] = [x_, y_]

    return db


class DomeEnvelope(ParametricEnvelope):
    def __init__(
        self,
        center: tuple = (5.0, 5.0),
        radius: float = 5.0,
        thickness: float = 0.50,
        min_lb: float = 0.0,
        n_hoops: int = 24,
        n_parallels: int = 40,
        r_oculus: float = 0.0,
        **kwargs,
    ):
        super().__init__(thickness=thickness, **kwargs)
        self.center = center
        self.radius = radius
        self.min_lb = min_lb
        self.n_hoops = n_hoops
        self.n_parallels = n_parallels
        self.r_oculus = r_oculus

        self.update_envelope()  # Generate the intra/extra/middle meshes

    @property
    def __data__(self):
        data = super().__data__
        data["center"] = self.center
        data["radius"] = self.radius
        data["min_lb"] = self.min_lb
        data["n_hoops"] = self.n_hoops
        data["n_parallels"] = self.n_parallels
        data["r_oculus"] = self.r_oculus
        return data

    def __str__(self):
        return f"DomeEnvelope(name={self.name})"

    def update_envelope(self):
        intrados, extrados, middle = dome_envelope(
            center=self.center,
            radius=self.radius,
            thickness=self.thickness,
            min_lb=self.min_lb,
            n_hoops=self.n_hoops,
            n_parallels=self.n_parallels,
            r_oculus=self.r_oculus,
        )
        self.intrados = intrados
        self.extrados = extrados
        self.middle = middle

    def compute_middle(self, x, y):
        return dome_middle(x, y, self.radius, self.center)

    def compute_bounds(self, x, y, thickness=None):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return dome_bounds(x, y, thickness, self.min_lb, self.center, self.radius)

    def compute_bounds_derivatives(self, x, y, thickness=None):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return dome_bounds_derivatives(x, y, thickness, self.min_lb, self.center, self.radius)

    def compute_bound_react(self, x, y, thickness=None, fixed=None):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return dome_bound_react(x, y, thickness, fixed, self.center, self.radius)

    def compute_bound_react_derivatives(self, x, y, thickness=None, fixed=None):
        if thickness is None:
            thickness = self.thickness
        else:
            self.thickness = thickness
        return dome_bound_react_derivatives(x, y, thickness, fixed, self.center, self.radius)
