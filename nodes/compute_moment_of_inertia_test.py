from gen.messages_pb2 import Mesh
from nodes.compute_moment_of_inertia import compute_moment_of_inertia


def test_unit_cube_inertia_tensor_matches_closed_form(ax, unit_cube_stl):
    # Independent oracle: the solid-cube moment-of-inertia formula gives
    # I_xx = I_yy = I_zz = (1/6) * mass * side^2 = 1/6 for a unit-density,
    # unit-side cube, with all off-diagonal (product-of-inertia) terms 0 by
    # symmetry. This is a textbook physics formula, not derived from trimesh.
    result = compute_moment_of_inertia(ax, Mesh(data=unit_cube_stl, format="STL"))
    tensor = list(result.tensor)
    assert len(tensor) == 9
    expected_diag = 1.0 / 6.0
    for i in (0, 4, 8):  # Ixx, Iyy, Izz on the row-major diagonal
        assert abs(tensor[i] - expected_diag) < 1e-9
    for i in (1, 2, 3, 5, 6, 7):  # off-diagonal products of inertia
        assert abs(tensor[i]) < 1e-9
    assert result.is_watertight is True


def test_compute_moment_of_inertia_rejects_malformed_data(ax):
    try:
        compute_moment_of_inertia(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
