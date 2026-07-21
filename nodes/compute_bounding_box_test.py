from gen.messages_pb2 import Mesh
from nodes.compute_bounding_box import compute_bounding_box


def test_unit_cube_bounding_box_matches_definition(ax, unit_cube_stl):
    # Independent oracle: a 1x1x1 cube centered at the origin spans exactly
    # [-0.5, 0.5] on every axis, extents (1,1,1), box volume 1.
    result = compute_bounding_box(ax, Mesh(data=unit_cube_stl, format="STL"))
    assert (result.min.x, result.min.y, result.min.z) == (-0.5, -0.5, -0.5)
    assert (result.max.x, result.max.y, result.max.z) == (0.5, 0.5, 0.5)
    assert (result.extents.x, result.extents.y, result.extents.z) == (1.0, 1.0, 1.0)
    assert result.volume == 1.0


def test_compute_bounding_box_rejects_malformed_data(ax):
    try:
        compute_bounding_box(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
