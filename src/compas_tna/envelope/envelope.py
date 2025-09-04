from typing import Optional
from typing import Tuple

import numpy as np

from compas.data import Data
from compas_tna.diagrams import FormDiagram


class Envelope(Data):
    """Pure geometric envelope representing masonry structure boundaries."""

    def __init__(self, rho: Optional[float] = 20.0, rho_fill: Optional[float] = 14.0, is_parametric: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.rho = rho
        self.rho_fill = rho_fill
        self._is_parametric = is_parametric

        # Computed properties (cached)
        self._area = 0.0
        self._volume = 0.0
        self._total_selfweight = 0.0

    @property
    def __data__(self):
        data = {}
        data["rho"] = self.rho
        data["rho_fill"] = self.rho_fill
        data["is_parametric"] = self.is_parametric
        return data

    def __str__(self):
        return f"Envelope(name={self.name})"

    # =============================================================================
    # Properties
    # =============================================================================

    @property
    def area(self):
        if not self._area:
            self._area = self.compute_area()
        return self._area

    @property
    def volume(self):
        if not self._volume:
            self._volume = self.compute_volume()
        return self._volume

    @property
    def selfweight(self):
        if not self._total_selfweight:
            self._total_selfweight = self.compute_selfweight()
        return self._total_selfweight

    @property
    def is_parametric(self) -> bool:
        return self._is_parametric

    @is_parametric.setter
    def is_parametric(self, value: bool) -> None:
        self._is_parametric = value

    # =============================================================================
    # Geometry operations
    # =============================================================================

    def compute_area(self) -> float:
        """Compute and returns the total area of the structure based on the appropriate method."""

        raise NotImplementedError("Implement compute_area for specific envelope type.")

    def compute_volume(self) -> float:
        """Compute and returns the total volume of the structure based on the appropriate method."""

        raise NotImplementedError("Implement compute_volume for specific envelope type.")

    def compute_selfweight(self) -> float:
        """Compute and returns the total selfweight of the structure based on the appropriate method."""

        raise NotImplementedError("Implement compute_selfweight for specific envelope type.")

    # =============================================================================
    # TNA-related operations (accept formdiagram)
    # =============================================================================

    def apply_selfweight_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply selfweight to the nodes of a form diagram based on the appropriate method."""

        raise NotImplementedError("Implement apply_selfweight_to_formdiagram for specific envelope type.")
    
    def apply_fill_weight_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply selfweight to the nodes of a form diagram based on the appropriate method."""

        raise NotImplementedError("Implement apply_fill_weight_to_formdiagram for specific envelope type.")

    def apply_bounds_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply envelope bounds to a form diagram based on the appropriate method."""

        raise NotImplementedError("Implement apply_envelope_to_formdiagram for specific envelope type.")

    def apply_target_heights_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply target heights to a form diagram based on the appropriate method."""

        raise NotImplementedError("Implement apply_target_heights_to_formdiagram for specific envelope type.")

    def apply_reaction_bounds_to_formdiagram(self, formdiagram: FormDiagram) -> None:
        """Apply reaction bounds to a form diagram based on the appropriate method."""

        raise NotImplementedError("Implement apply_reaction_bounds_to_formdiagram for specific envelope type.")

    # =============================================================================
    # Numerical methods to be implemented at sub classes
    # =============================================================================

    def compute_middle(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Compute the middle of the envelope based on the appropriate method."""

        raise NotImplementedError("Implement compute_middle for specific envelope type.")

    def compute_bounds(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute the upper and lower bounds of the envelope based on the appropriate method."""

        raise NotImplementedError("Implement compute_bounds for specific envelope type.")

    def compute_bounds_derivatives(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute the upper and lower bounds  derivativesof the envelope based on the appropriate method."""

        raise NotImplementedError("Implement compute_bounds_derivatives for specific envelope type.")

    def compute_bound_react(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Compute the reaction bounds of the envelope based on the appropriate method."""

        raise NotImplementedError("Implement compute_bound_react for specific envelope type.")

    def compute_bound_react_derivatives(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Compute the bound_react_derivatives of the envelope based on the appropriate method."""

        raise NotImplementedError("Implement compute_bound_react_derivatives for specific envelope type.")
