from gen.messages_pb2 import Mesh
from nodes.compute_convex_hull import compute_convex_hull


def test_convex_hull_of_cube_equals_cube(ax, unit_cube_stl):
    # Independent oracle: a cube is already convex, so its hull has the same
    # volume (1) and surface area (6) as the cube itself.
    result = compute_convex_hull(ax, Mesh(data=unit_cube_stl, format="STL"))
    assert abs(result.volume - 1.0) < 1e-9
    assert abs(result.area - 6.0) < 1e-9
    assert result.hull.face_count > 0
    assert result.hull.format == "STL"
    assert len(result.hull.data) > 0


def test_compute_convex_hull_rejects_malformed_data(ax):
    try:
        compute_convex_hull(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
