from gen.messages_pb2 import Mesh
from nodes.compute_center_of_mass import compute_center_of_mass


def test_unit_cube_center_of_mass_is_origin(ax, unit_cube_stl):
    # Independent oracle: a cube centered at the origin has its center of
    # mass at the origin by symmetry.
    result = compute_center_of_mass(ax, Mesh(data=unit_cube_stl, format="STL"))
    assert abs(result.center_of_mass.x) < 1e-9
    assert abs(result.center_of_mass.y) < 1e-9
    assert abs(result.center_of_mass.z) < 1e-9
    assert result.is_watertight is True


def test_compute_center_of_mass_rejects_malformed_data(ax):
    try:
        compute_center_of_mass(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
