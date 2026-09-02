import pytest

from compas_tna.envelope import CrossVaultEnvelope
from compas_tna.envelope import MeshEnvelope


@pytest.mark.parametrize(
    ("x_span", "y_span"),
    [
        ((0.0, 10.0), (0.0, 10.0)),
        ((0.0, 10.0), (0.0, 6.0)),
    ],
)
def test_interpolate_middle_mesh_projects_vertically(x_span, y_span):
    analytical = CrossVaultEnvelope(x_span=x_span, y_span=y_span, thickness=0.5, n=10)
    envelope = MeshEnvelope.from_meshes(analytical.intrados, analytical.extrados)

    assert envelope.middle.vertices_attributes("xy") == analytical.intrados.vertices_attributes("xy")

    boundary = set(envelope.middle.vertices_on_boundary())
    differences = [
        abs(envelope.middle.vertex_attribute(vertex, "z") - analytical.middle.vertex_attribute(vertex, "z")) for vertex in envelope.middle.vertices() if vertex not in boundary
    ]
    thicknesses = envelope.middle.vertices_attribute("thickness")

    assert sum(differences) / len(differences) < 0.01
    assert min(thicknesses) > 0.0
