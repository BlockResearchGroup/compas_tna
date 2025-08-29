# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added `Envelope` class for masonry structure boundaries with intrados, extrados, and middle meshes
* Added direct envelope creation methods to `Envelope` class:
  * `from_crossvault()` - Creates cross vault envelopes with configurable spans and thickness
  * `from_dome()` - Creates dome envelopes with configurable radius, center, and oculus
  * `from_pavillionvault()` - Creates pavillion vault envelopes with spring angle support
  * `from_pointedvault()` - Creates pointed vault envelopes with height control parameters
* Added envelope creation functions for each vault type:
  * `create_crossvault_envelope()` - Generates cross vault meshes and callables
  * `create_dome_envelope()` - Generates dome meshes with circular topology
  * `create_pavillionvault_envelope()` - Generates pavillion vault meshes with expanded option
  * `create_pointedvault_envelope()` - Generates pointed vault meshes with height parameters
* Added vault-specific update functions for optimization:
  * `crossvault_middle_update()`, `crossvault_ub_lb_update()`, `crossvault_dub_dlb()`
  * `dome_middle_update()`, `dome_ub_lb_update()`, `dome_dub_dlb()`
  * `pavillionvault_middle_update()`, `pavillionvault_ub_lb_update()`, `pavillionvault_dub_dlb()`
  * `pointedvault_middle_update()`, `pointedvault_ub_lb_update()`, `pointedvault_dub_dlb()`

* Added comprehensive form diagram creation methods to `FormDiagram` class:
  * `create_cross()` - Creates cross discretisation with orthogonal arrangement and quad diagonals
  * `create_fan()` - Creates fan discretisation with straight lines to corners
  * `create_parametric_fan()` - Creates parametric fan diagrams with lambda parameter control
  * `create_cross_with_diagonal()` - Creates cross discretisation with diagonal lines
  * `create_ortho()` - Creates orthogonal discretisation
  * `create_circular_radial()` - Creates circular radial form diagrams with equally spaced hoops
  * `create_circular_radial_spaced()` - Creates circular radial form diagrams with hemispheric spacing
  * `create_circular_spiral()` - Creates circular spiral form diagrams
  * `create_arch()` - Creates arch form diagrams with semicircular projection
  * `create_arch_equally_spaced()` - Creates arch form diagrams with equally spaced nodes
* Added support assignment methods:
  * `assign_support_type()` - Assigns supports based on type ("corners" or "all")
* Added corner detection functionality:
  * `corner_vertices()` - Identifies corner vertices on boundary with configurable angle threshold
* Added comprehensive mesh creation functions in `diagram_rectangular.py`:
  * `create_cross_mesh()` - Creates cross pattern meshes
  * `create_fan_mesh()` - Creates fan pattern meshes
  * `create_parametric_fan_mesh()` - Creates parametric fan meshes with lambda interpolation
  * `create_cross_with_diagonal_mesh()` - Creates cross meshes with diagonals
  * `create_ortho_mesh()` - Creates orthogonal grid meshes
* Added circular mesh creation functions in `diagram_circular.py`:
  * `create_circular_radial_mesh()` - Creates circular radial meshes
  * `create_circular_radial_spaced_mesh()` - Creates hemispherically spaced circular meshes
  * `create_circular_spiral_mesh()` - Creates circular spiral meshes
* Added arch mesh creation functions in `diagram_arch.py`:
  * `create_arch_linear_mesh()` - Creates arch meshes with semicircular projection
  * `create_arch_linear_equally_spaced_mesh()` - Creates arch meshes with equally spaced nodes

### Changed

* Refactored parameter passing from `xy_span=[[x0, x1], [y0, y1]]` to `x_span=(x0, x1), y_span=(y0, y1)` for better API consistency
* Changed `center` parameter from list to tuple in circular diagram functions for immutability and consistency
* Updated function signatures to use single-line format for Black compatibility
* Improved code formatting and linting across all diagram generation files
* Fixed various spelling errors and documentation formatting issues
* Renamed `create_delta_form()` to `create_cross_with_diagonal()` for better clarity
* Updated support assignment to use `is_support` attribute instead of deprecated `is_fixed`
* Removed deprecated `form.parameters` usage from all form creation methods

### Removed


## [0.6.0] 2025-02-03

### Added

### Changed

* Changed assignment of defaults in base scene object for Form Diagrams.
* Changed assignment of defaults in base scene object for Force Diagrams.

### Removed


## [0.5.2] 2024-11-10

### Added

### Changed

### Removed


## [0.5.1] 2024-11-10

### Added

### Changed

### Removed

* Removed `compas` from requirements to solve problem in Rhino plugins.


## [0.5.0] 2024-07-08

### Added

* Added `compas_tna.diagrams.FormDiagram.from_mesh` factory.

### Changed

* Fixed bug in `compas_tna.rhino.scene.FormObject`.
* Changed `from compas.utilities` to `from compas.itertools`.

### Removed

## [0.4.1] 2024-07-08

### Added

* Added `compas_tna.diagrams.FormDiagram.from_mesh`.

### Changed

### Removed

## [0.4.0] 2024-03-01

### Added

### Changed

### Removed

## [0.3.0] 2024-02-09

### Added

### Changed

### Removed

## [0.2.0] 2022-12-02

### Added

### Changed

* Updated workflow.

### Removed
