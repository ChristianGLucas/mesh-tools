from gen.messages_pb2 import Mesh
from nodes.fill_holes import fill_holes


def test_fill_holes_closes_single_missing_face(ax, holey_cube_stl):
    # Independent oracle: removing one triangular face from a cube leaves a
    # single planar-quad hole; filling it exactly reconstructs the original
    # closed cube (8 vertices, watertight, volume 1).
    result = fill_holes(ax, Mesh(data=holey_cube_stl, format="STL"))
    assert result.fully_filled is True
    assert result.is_watertight is True
    assert result.mesh.vertex_count == 8


def test_fill_holes_rejects_malformed_data(ax):
    try:
        fill_holes(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
