from gen.messages_pb2 import Mesh
from nodes.compute_oriented_bounding_box import compute_oriented_bounding_box


def test_unit_cube_obb_matches_aabb(ax, unit_cube_stl):
    # Independent oracle: an axis-aligned cube's minimum-volume OBB IS its
    # own AABB (no rotation can shrink it further) -> extents (1,1,1),
    # volume 1, and a 16-value (4x4) transform.
    result = compute_oriented_bounding_box(ax, Mesh(data=unit_cube_stl, format="STL"))
    assert len(result.transform) == 16
    assert abs(result.extents.x - 1.0) < 1e-6
    assert abs(result.extents.y - 1.0) < 1e-6
    assert abs(result.extents.z - 1.0) < 1e-6
    assert abs(result.volume - 1.0) < 1e-6


def test_compute_oriented_bounding_box_rejects_malformed_data(ax):
    try:
        compute_oriented_bounding_box(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
