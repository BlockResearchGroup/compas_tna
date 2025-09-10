# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Update docs to include envelope

### Changed

### Removed


## [0.7.0] 2025-09-06

### Added

* Added `Envelope` base class for masonry structure boundaries with intrados, extrados, and middle meshes
* Added especialized `MeshEnvelope`, `ParametricEnvelope`, and `BrepEnvelope` to deal with different evelope inputs.
* Added direct parametric envelope creation methods inheriting from `ParametricEnvelope` class:
  * `CrossVaultEnvelope` - Creates cross vault envelopes with configurable spans and thickness
  * `DomeEnvelope` - Creates dome envelopes with configurable radius, center, and oculus
  * `PavillionVaultEnvelope` - Creates pavillion vault envelopes with spring angle support
  * `PointedVaultEnvelope` - Creates pointed vault envelopes with height control parameters
* The infrastructure around these classes has been updated to enable assigning constraints to the form diagrams.
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
* Added circular mesh creation functions in `diagram_circular.py` and corrected oculus and diagonal properties.
* Added arch mesh creation functions in `diagram_arch.py`:
* Added option to add `fill` to envelope. TODO: properly deal with 'pz' summation in future

### Changed

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
