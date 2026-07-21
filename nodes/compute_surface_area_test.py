from gen.messages_pb2 import Mesh
from nodes.compute_surface_area import compute_surface_area


def test_unit_cube_surface_area_is_six(ax, unit_cube_stl):
    # Independent oracle: a 1x1x1 cube has 6 unit-square faces -> area 6.
    result = compute_surface_area(ax, Mesh(data=unit_cube_stl, format="STL"))
    assert result.area == 6.0


def test_compute_surface_area_rejects_malformed_data(ax):
    try:
        compute_surface_area(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
