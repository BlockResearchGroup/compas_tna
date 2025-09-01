import numpy as np

from compas_tna.diagrams import FormDiagram
from compas_tna.envelope import Envelope


class ParametricEnvelope(Envelope):
    """Pure geometric envelope representing masonry structure boundaries created parametrically."""

    def __init__(self, thickness: float = 0.50, **kwargs):
        super().__init__(**kwargs)

        self._thickness = thickness
        self.is_parametric = True

    def __str__(self):
        return f"ParametricEnvelope(name={self.name})"

    @property
    def __data__(self):
        data = super().__data__
        data["thickness"] = self._thickness
        data["is_parametric"] = self.is_parametric
        return data

    # =============================================================================
    # Parametric Common Prepoperties
    # =============================================================================

    @property
    def thickness(self) -> float:
        """Get the thickness of the envelope.

        Returns
        -------
        float
            The thickness of the envelope.
        """
        return self._thickness

    @thickness.setter
    def thickness(self, value: float) -> None:
        """Set the thickness of the envelope.

        Parameters
        -------
        value : float
            The thickness value to set.
        """
        self._thickness = value

    # =============================================================================
    # Envelope Generator
    # =============================================================================

    def update_envelope(self) -> None:
        """Update the envelope based on the appropriate method."""

        raise NotImplementedError("Implement update_envelope for specific envelope type.")

    # =============================================================================
    # Geometry operations
    # =============================================================================

    def compute_volume(self) -> float:
        """Compute and returns the volume of the structure based on the area and thickness in the data.

        Returns
        -------
        float
            The total volume of the structure.

        """
        if self.middle is None:
            self.update_envelope()

        return self.compute_area() * self.thickness

    def compute_selfweight(self) -> float:
        """Compute and returns the total selfweight of the structure based on the area and thickness in the data.

        Returns
        -------
        float
            The total selfweight of the structure.

        """
        if self.middle is None:
            self.update_envelope()

        return self.compute_volume() * self.rho

    def compute_area(self) -> float:
        """Compute and returns the total selfweight of the structure based on the area and thickness in the data.

        Returns
        -------
        float
            The total selfweight of the structure.
        """
        if self.middle is None:
            self.update_envelope()

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
        # Step 2: Compute the selfweight of the shell
        total_selfweight = self.compute_selfweight()

        # Step 3: Copy the form diagram and project it onto the middle mesh vertically
        form_: FormDiagram = formdiagram.copy()

        xy = np.array(form_.vertices_attributes("xy"))
        zt = list(self.compute_middle(xy[:, 0], xy[:, 1]).flatten().tolist())
        for i, key in enumerate(form_.vertices()):
            form_.vertex_attribute(key, "z", zt[i])

        # Step 4: Compute and lump selfweight at vertices
        total_pz = 0.0
        for vertex in form_.vertices():
            vertex_area = form_.vertex_area(vertex)
            thickness = self.thickness
            pz = -vertex_area * thickness * self.rho
            formdiagram.vertex_attribute(vertex, "pz", pz)
            total_pz += abs(pz)

        # Step 5: Scale to match total selfweight if normalize=True
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

        xy = np.array(formdiagram.vertices_attributes("xy"))
        zub, zlb = self.compute_ub_lb(xy[:, 0], xy[:, 1])
        for i, key in enumerate(formdiagram.vertices()):
            formdiagram.vertex_attribute(key, "ub", float(zub[i]))
            formdiagram.vertex_attribute(key, "lb", float(zlb[i]))
        # TODO: Future Cached properties could be added here

    def apply_target_heights_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply target heights to a form diagram based on the Envelope middle surface.

        This method projects the form diagram onto the Envelope middle surface
        and assigns the heights to 'target' property. This assignment can later be used to compute a bestfit optimization.
        """

        xy = np.array(formdiagram.vertices_attributes("xy"))
        zt = list(self.compute_middle(xy[:, 0], xy[:, 1]).flatten().tolist())
        for i, key in enumerate(formdiagram.vertices()):
            formdiagram.vertex_attribute(key, "z", zt[i])
        # TODO: Future Cached properties could be added here

    def apply_reaction_bounds_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply reaction bounds to a form diagram based on the Envelope middle surface.

        This method projects the form diagram onto the Envelope middle surface
        and assigns the heights to 'target' property. This assignment can later be used to compute a bestfit optimization.
        """
        raise NotImplementedError("Implement apply_reaction_bounds_to_formdiagram for specific envelope type.")
        ## TODO: Implement this

    def compute_middle(self, x, y):
        raise NotImplementedError("Implement compute_middle for specific envelope type.")

    def compute_ub_lb(self, x, y, thickness):
        raise NotImplementedError("Implement compute_ub_lb for specific envelope type.")

    def compute_dub_dlb(self, x, y):
        raise NotImplementedError("Implement compute_dub_dlb for specific envelope type.")

    def compute_bound_react(self, x, y, thickness, fixed):
        raise NotImplementedError("Implement compute_bound_react for specific envelope type.")

    def compute_db(self, x, y, thickness, fixed):
        return
