import math
from typing import Optional

from numpy import asarray
from scipy.interpolate import griddata

from compas.datastructures import Mesh
from compas_tna.diagrams import FormDiagram
from compas_tna.envelope import Envelope


# TODO: What if intrados and extrados are surfaces?
def interpolate_middle_mesh(intrados: Mesh, extrados: Mesh) -> Mesh:
    """Interpolate a middle mesh between intrados and extrados meshes.

    This function properly calculates thickness by considering the normal vector
    at each point, ensuring accurate thickness measurements on curved surfaces.

    Parameters
    ----------
    intrados : Mesh
        The intrados surface mesh.
    extrados : Mesh
        The extrados surface mesh.

    Returns
    -------
    Mesh
        The interpolated middle mesh with proper normal-based thickness stored.
    """
    # Use the intrados as base topology
    middle = intrados.copy()

    # Get point clouds for interpolation
    intrados_points = asarray(intrados.vertices_attributes("xyz"))
    extrados_points = asarray(extrados.vertices_attributes("xyz"))

    # Get XY coordinates of middle mesh
    middle_xy = asarray(middle.vertices_attributes("xy"))

    # Interpolate Z coordinates from both surfaces
    zi = griddata(intrados_points[:, :2], intrados_points[:, 2], middle_xy, method="linear")
    ze = griddata(extrados_points[:, :2], extrados_points[:, 2], middle_xy, method="linear")

    # First loop: set middle Z as average
    for i, key in enumerate(middle.vertices()):
        middle_z = (zi[i] + ze[i]) / 2.0
        middle.vertex_attribute(key, "z", middle_z)

    # Second loop: calculate and set thickness using correct normals
    for i, key in enumerate(middle.vertices()):
        nx, ny, nz = middle.vertex_normal(key)
        z_diff = ze[i] - zi[i]
        if abs(nz) > 0.1:
            thickness = abs(z_diff) * abs(nz)
        else:
            thickness = abs(z_diff)
        middle.vertex_attribute(key, "thickness", thickness)

    return middle


# TODO: What if middle is a surface and not a mesh?
def offset_from_middle(middle: Mesh, fixed_xy: bool = True) -> tuple[Mesh, Mesh]:
    """
    Offset a middle surface mesh to obtain extrados and intrados meshes using thickness attributes.

    This function properly handles curved surfaces by using the normal vector
    and the thickness measured perpendicular to the surface.

    Parameters
    ----------
    middle : Mesh
        The middle surface mesh with thickness attributes per vertex.
    fixed_xy : bool, optional
        If True, extrados/intrados will have the same XY as the middle mesh,
        and only Z will be offset (with normal correction).
        If False, full 3D normal offset is used.

    Returns
    -------
    tuple[Mesh, Mesh]
        (intrados, extrados) offset meshes.
    """
    extrados = middle.copy()
    intrados = middle.copy()

    for key in middle.vertices():
        x, y, z = middle.vertex_coordinates(key)
        nx, ny, nz = middle.vertex_normal(key)

        # Get thickness for this specific vertex (should be normal-based)
        thickness = middle.vertex_attribute(key, "thickness")
        if thickness is None:
            thickness = 0.5
        half_thick = 0.5 * thickness

        if fixed_xy:
            # Prevent division by zero for horizontal normals
            if abs(nz) < 1e-8:
                raise ValueError(f"Normal at vertex {key} is (almost) horizontal: {nx, ny, nz}")
            dz = half_thick / nz
            extrados_z = z + dz
            intrados_z = z - dz
            extrados.vertex_attribute(key, "z", extrados_z)
            intrados.vertex_attribute(key, "z", intrados_z)
        else:
            # Full 3D normal offset - this is the most accurate for curved surfaces
            extrados.vertex_attributes(
                key,
                "xyz",
                [x + half_thick * nx, y + half_thick * ny, z + half_thick * nz],
            )
            intrados.vertex_attributes(
                key,
                "xyz",
                [x - half_thick * nx, y - half_thick * ny, z - half_thick * nz],
            )

    return intrados, extrados


# TODO: What if the target is a surface and not a mesh?
def project_mesh_to_target_vertical(mesh: Mesh, target: Mesh) -> None:
    """Project a mesh vertically (in Z direction) onto a target mesh.

    Parameters
    ----------
    mesh : Mesh
        The mesh to be projected.
    target : Mesh
        The target mesh to project onto.

    Returns
    -------
    None
        The mesh is modified in place.
    """
    # Get target mesh vertices for simple vertical projection
    target_vertices = list(target.vertices())
    target_points = [target.vertex_point(v) for v in target_vertices]

    for vertex in mesh.vertices():
        point = mesh.vertex_point(vertex)

        # Find the closest target vertex in XY plane
        min_distance = float("inf")
        closest_z = point.z

        for target_point in target_points:
            # Calculate XY distance (ignore Z)
            xy_distance = ((point.x - target_point.x) ** 2 + (point.y - target_point.y) ** 2) ** 0.5

            if xy_distance < min_distance:
                min_distance = xy_distance
                closest_z = target_point.z

        # Update vertex to closest Z value
        new_point = point.copy()
        new_point.z = closest_z
        mesh.vertex_attributes(vertex, "xyz", new_point)


def pattern_inverse_height_thickness(pattern: Mesh, tmin: Optional[float] = None, tmax: Optional[float] = None) -> None:
    """Set variable thickness based on inverse height.

    Parameters
    ----------
    pattern : Mesh
        The mesh to apply thickness to.
    tmin : float, optional
        Minimum thickness. If None, will be calculated as 3/1000 of the diagonal of the xy bounding box.
    tmax : float, optional
        Maximum thickness. If None, will be calculated as 50/1000 of the diagonal of the xy bounding box.
    """
    x: list[float] = pattern.vertices_attribute(name="x")
    xmin = min(x)
    xmax = max(x)
    dx = xmax - xmin

    y: list[float] = pattern.vertices_attribute(name="y")
    ymin = min(y)
    ymax = max(y)
    dy = ymax - ymin

    d = (dx**2 + dy**2) ** 0.5

    tmin = tmin or 3 * d / 1000
    tmax = tmax or 50 * d / 1000

    pattern.update_default_vertex_attributes(thickness=0)
    zvalues: list[float] = pattern.vertices_attribute(name="z")
    zmin = min(zvalues)
    zmax = max(zvalues)

    for vertex in pattern.vertices():
        point = pattern.vertex_point(vertex)
        z = (point.z - zmin) / (zmax - zmin)
        thickness = (1 - z) * (tmax - tmin) + tmin
        pattern.vertex_attribute(vertex, name="thickness", value=thickness)


class MeshEnvelope(Envelope):
    """An Envelope defined by meshes at intrados and extrados."""

    def __init__(self, intrados: Mesh = None, extrados: Mesh = None, middle: Mesh = None, fill: Mesh = None, thickness: float = 0.5, **kwargs):
        super().__init__(**kwargs)

        self.intrados = intrados
        self.extrados = extrados
        self.middle = middle
        self.fill = fill

        # Thickness property
        self._thickness = thickness

    @property
    def __data__(self):
        data = super().__data__
        data["intrados"] = self.intrados
        data["extrados"] = self.extrados
        data["middle"] = self.middle
        data["fill"] = self.fill
        data["thickness"] = self._thickness
        return data

    def __str__(self):
        return f"Envelope(name={self.name})"

    # =============================================================================
    # Factory methods
    # =============================================================================

    @classmethod
    def from_meshes(cls, intrados: Mesh, extrados: Mesh, middle: Optional[Mesh] = None) -> "Envelope":
        """Construct an envelope from intrados and extrados meshes.

        Parameters
        ----------
        intrados : Mesh
            The intrados surface mesh of the envelope.
        extrados : Mesh
            The extrados surface mesh of the envelope.
        middle : Mesh, optional
            The middle surface mesh of the envelope.

        Returns
        -------
        :class:`Envelope`

        """
        envelope = cls()
        envelope.intrados = intrados
        envelope.extrados = extrados
        if middle is not None:
            envelope.middle = middle
        else:
            envelope.middle = interpolate_middle_mesh(intrados, extrados)

        return envelope

    @classmethod
    def from_middle_mesh(cls, mesh: Mesh, thickness: Optional[float] = None) -> "Envelope":
        """Construct an envelope from a mesh with specified thickness.

        Parameters
        ----------
        formdiagram : FormDiagram
            The form diagram to create the envelope from.
        thickness : float, optional
            The thickness of the envelope. If None, uses thickness values stored in formdiagram vertices.

        Returns
        -------
        :class:`Envelope`

        """
        envelope = cls()

        envelope.middle = mesh.copy(cls=Mesh)

        if thickness is not None:
            envelope.thickness = thickness

            # Create intrados and extrados using thickness from middle mesh
            intrados, extrados = offset_from_middle(envelope.middle)
            envelope.intrados = intrados
            envelope.extrados = extrados

        return envelope

    @classmethod
    def from_formdiagram(cls, formdiagram: FormDiagram, thickness: Optional[float] = None) -> "Envelope":
        """Construct an envelope from a FormDiagram with specified thickness.

        Parameters
        ----------
        formdiagram : FormDiagram
            The form diagram to create the envelope from.
        thickness : float, optional
            The thickness of the envelope. If None, uses thickness values stored in formdiagram vertices.

        Returns
        -------
        :class:`Envelope`

        """
        return cls.from_middle_mesh(formdiagram, thickness)

    # =============================================================================
    # Properties
    # =============================================================================

    @property
    def thickness(self) -> float:
        """Get the average thickness of the envelope.

        Returns
        -------
        float
            The average thickness of the envelope.
        """
        if self.middle is not None:
            # Return average thickness from middle mesh vertices
            thicknesses = []
            for key in self.middle.vertices():
                thickness = self.middle.vertex_attribute(key, "thickness")
                if thickness is not None:
                    thicknesses.append(thickness)

            if thicknesses:
                return sum(thicknesses) / len(thicknesses)

        return self._thickness

    @thickness.setter
    def thickness(self, value: float) -> None:
        """Set a uniform thickness for all vertices of the envelope.

        Parameters
        -------
        value : float
            The thickness value to set for all vertices.
        """
        self._thickness = value

        # Update middle mesh if it exists
        if self.middle is not None:
            for key in self.middle.vertices():
                self.middle.vertex_attribute(key, "thickness", value)

    @property
    def is_parametric(self) -> bool:
        """Check if the envelope is parametric."""
        return False

    # =============================================================================
    # Geometric operations
    # =============================================================================

    def set_variable_thickness(self, tmin: Optional[float] = None, tmax: Optional[float] = None) -> None:
        """Set variable thickness based on inverse height using the pattern_inverse_height_thickness function.

        This method applies thickness variation based on the height of vertices in the middle mesh,
        where higher vertices get thinner thickness and lower vertices get thicker thickness.

        Parameters
        -------
        tmin : float, optional
            Minimum thickness. If None, will be calculated as 3/1000 of the diagonal of the xy bounding box.
        tmax : float, optional
            Maximum thickness. If None, will be calculated as 50/1000 of the diagonal of the xy bounding box.
        """
        if self.middle is None:
            raise ValueError("Middle mesh is not available. Cannot set variable thickness.")

        # Apply the pattern_inverse_height_thickness function to the middle mesh
        pattern_inverse_height_thickness(self.middle, tmin=tmin, tmax=tmax)

        # Update intrados and extrados meshes
        self.intrados, self.extrados = offset_from_middle(self.middle)

    def compute_volume(self) -> float:
        """Compute and returns the volume of the structure based on the area and thickness in the data.

        Returns
        -------
        float
            The total volume of the structure.

        """
        if self.middle is None:
            raise ValueError("Middle mesh is not available. Cannot compute volume.")

        middle = self.middle
        total_volume = 0.0

        # Use variable thickness from middle mesh vertices
        for vertex in middle.vertices():
            thickness = middle.vertex_attribute(vertex, "thickness")
            if thickness is None:
                thickness = self._thickness
            vertex_area = middle.vertex_area(vertex)  # should be projected area
            vertex_volume = thickness * vertex_area
            total_volume += vertex_volume

        return total_volume

    def compute_selfweight(self) -> float:
        """Compute and returns the total selfweight of the structure based on the area and thickness in the data.

        Returns
        -------
        float
            The total selfweight of the structure.

        """
        if self.middle is None:
            if self.intrados is not None and self.extrados is not None:
                self.middle = interpolate_middle_mesh(self.intrados, self.extrados)
            else:
                raise ValueError("Middle mesh is not available and cannot be interpolated.")

        middle = self.middle
        rho = self.rho
        total_selfweight = 0.0

        # Use variable thickness from middle mesh vertices
        for vertex in middle.vertices():
            thickness = middle.vertex_attribute(vertex, "thickness")
            if thickness is None:
                thickness = self._thickness
            vertex_area = middle.vertex_area(vertex)
            vertex_volume = thickness * vertex_area
            vertex_weight = vertex_volume * rho
            total_selfweight += vertex_weight

        return total_selfweight

    def compute_area(self) -> float:
        """Compute and returns the total selfweight of the structure based on the area and thickness in the data.

        Returns
        -------
        float
            The total selfweight of the structure.
        """
        if self.middle is None:
            raise ValueError("Middle mesh is not available. Cannot compute area.")

        return self.middle.area()

    # =============================================================================
    # TNA-specific operations (accept formdiagram as parameter)
    # =============================================================================

    def apply_selfweight_to_formdiagram(self, formdiagram: FormDiagram, normalize=True) -> None:
        """Apply selfweight to the nodes of a form diagram based on the middle surface and local thicknesses.

        Parameters
        ----------
        formdiagram : FormDiagram
            The form diagram to apply selfweight to.
        normalize : bool, optional
            Whether or not normalize the selfweight to match the computed total selfweight, by default True

        Returns
        -------
        None
            The FormDiagram is modified in place

        """
        # Step 1: Check that middle mesh is present
        if self.middle is None:
            if self.intrados is not None and self.extrados is not None:
                self.middle = interpolate_middle_mesh(self.intrados, self.extrados)
            else:
                raise ValueError("Middle mesh is not set. Please set the middle mesh before applying selfweight.")

        # Step 2: Compute the selfweight of the shell
        total_selfweight = self.compute_selfweight()

        # Step 3: Sync thickness to the form diagram
        self.sync_thickness_to_formdiagram(formdiagram)

        # Step 4: Copy the form diagram and project it onto the middle mesh vertically
        form_ = formdiagram.copy()
        project_mesh_to_target_vertical(form_, self.middle)

        # Step 5: Compute and lump selfweight at vertices
        total_pz = 0.0
        for vertex in form_.vertices():
            # Get vertex area and thickness
            vertex_area = form_.vertex_area(vertex)
            thickness = form_.vertex_attribute(vertex, "thickness")

            # Compute selfweight contribution (negative for downward direction)
            pz = -vertex_area * thickness * self.rho

            # Store in form diagram
            formdiagram.vertex_attribute(vertex, "pz", pz)
            total_pz += abs(pz)  # Sum absolute values for normalization

        # Step 6: Scale to match total selfweight if normalize=True
        if normalize and total_pz > 0:
            scale_factor = total_selfweight / total_pz
            if scale_factor != 1.0:
                print(f"Scaled selfweight by factor: {scale_factor}")

            for vertex in formdiagram.vertices():
                pz = formdiagram.vertex_attribute(vertex, "pz")
                formdiagram.vertex_attribute(vertex, "pz", pz * scale_factor)

        print(f"Selfweight applied to form diagram. Total load: {sum(abs(formdiagram.vertex_attribute(vertex, 'pz')) for vertex in formdiagram.vertices())}")

    def apply_bounds_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply envelope bounds to a form diagram based on the intrados and extrados surfaces.

        This method projects the form diagram onto both intrados and extrados surfaces
        and assigns the heights to 'ub' (upper bound) and 'lb' (lower bound) properties.

        Parameters
        ----------
        formdiagram : FormDiagram
            The form diagram to apply bounds to.

        Returns
        -------
        None
            The FormDiagram is modified in place.
        """
        # Step 1: Check that intrados and extrados are present
        if self.intrados is None or self.extrados is None:
            raise ValueError("Intra/Extrados not set. Please set them before applying bounds.")

        # Step 2: Copy the form diagram for projection
        form_ub = formdiagram.copy()  # For upper bound (extrados)
        form_lb = formdiagram.copy()  # For lower bound (intrados)

        # Step 3: Project form diagram onto extrados (upper bound)
        project_mesh_to_target_vertical(form_ub, self.extrados)
        project_mesh_to_target_vertical(form_lb, self.intrados)

        # Step 4: Collect heights and assign to form diagram
        for vertex in formdiagram.vertices():
            if vertex in form_ub.vertices() and vertex in form_lb.vertices():
                # Get z coordinates from projected meshes
                _, _, z_ub = form_ub.vertex_coordinates(vertex)
                _, _, z_lb = form_lb.vertex_coordinates(vertex)

                # Assign to form diagram
                formdiagram.vertex_attribute(vertex, "ub", z_ub)
                formdiagram.vertex_attribute(vertex, "lb", z_lb)
            else:
                print(f"Warning: Vertex {vertex} not found in projected meshes")
                # Set default values if vertex not found
                formdiagram.vertex_attribute(vertex, "ub", float("inf"))
                formdiagram.vertex_attribute(vertex, "lb", float("-inf"))

    def apply_target_heights_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply target heights to a form diagram based on the Envelope middle surface.

        This method projects the form diagram onto the Envelope middle surface
        and assigns the heights to 'target' property. This assignment can later be used to compute a bestfit optimization.
        """
        if self.middle is None:
            raise ValueError("Middle mesh is not set. Please set the middle mesh before applying target heights.")

        # Step 1: Copy the form diagram for projection
        form_target = formdiagram.copy()  # For upper bound (extrados)

        project_mesh_to_target_vertical(form_target, self.middle)

        # Step 2: Collect heights and assign to form diagram
        for vertex in formdiagram.vertices():
            if vertex in form_target.vertices():
                z_target = form_target.vertex_attribute(vertex, "z")
                formdiagram.vertex_attribute(vertex, "target", z_target)

    def apply_reaction_bounds_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply reaction bounds to a form diagram based on the Envelope middle surface.

        This method projects the form diagram onto the Envelope middle surface
        and assigns the heights to 'target' property. This assignment can later be used to compute a bestfit optimization.
        """

        # if not self.callable_bound_react:
        #     raise ValueError("Callable bound reaction is not set. Please set this limit manually.")

        ## TODO: Implement this

    def sync_thickness_to_formdiagram(self, formdiagram: FormDiagram, method="linear", extrapolate=True) -> None:
        """Synchronize thickness attributes from middle mesh to form diagram using continuous interpolation.

        This method creates a continuous thickness map from the middle mesh and interpolates
        thickness values at the form diagram vertex locations. This ensures compatibility
        even when the middle mesh and form diagram have different topologies.

        Parameters
        -------
        formdiagram : FormDiagram
            The form diagram to sync thickness to.
        """
        if self.middle is None:
            raise ValueError("Middle mesh must be set to sync thickness.")

        # Get middle mesh XY coordinates and thickness values
        middle_xy = self.middle.vertices_attributes("xy")
        middle_thickness = self.middle.vertices_attribute("thickness")

        # Validate data
        if not middle_xy or not middle_thickness:
            raise ValueError("Middle mesh must have both 'xy' and 'thickness' attributes.")

        # Convert to numpy arrays
        middle_xy_array = asarray(middle_xy)
        middle_thickness_array = asarray(middle_thickness)

        # Get form diagram XY coordinates
        form_xy = formdiagram.vertices_attributes("xy")
        if not form_xy:
            raise ValueError("Form diagram must have 'xy' attributes.")

        form_xy_array = asarray(form_xy)

        # Use griddata for 2D interpolation
        interpolated_thickness = griddata(
            middle_xy_array,
            middle_thickness_array,
            form_xy_array,
            method=method,
            fill_value=self._thickness,  # Use default thickness for points outside convex hull
            # extrapolate=extrapolate
        )

        # Assign interpolated thickness values to form diagram vertices
        for i, vertex in enumerate(formdiagram.vertices()):
            thickness_value = float(interpolated_thickness[i])
            # Ensure thickness is positive and reasonable
            if thickness_value <= 0 or math.isnan(thickness_value):
                thickness_value = self._thickness
            formdiagram.vertex_attribute(vertex, "thickness", thickness_value)

    def compute_middle(self, x, y):
        raise NotImplementedError("Implement compute_middle for specific envelope type.")

    def compute_bounds(self, x, y, thickness):
        raise NotImplementedError("Implement compute_bounds for specific envelope type.")

    def compute_bounds_derivatives(self, x, y):
        raise NotImplementedError("Implement compute_bounds_derivatives for specific envelope type.")

    def compute_bound_react(self, x, y, thickness, fixed):
        raise NotImplementedError("Implement compute_bound_react for specific envelope type.")

    def compute_bound_react_derivatives(self, x, y, thickness, fixed):
        raise NotImplementedError("Implement compute_bound_react_derivatives for specific envelope type.")
