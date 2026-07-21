from gen.messages_pb2 import Mesh
from nodes.fix_normals import fix_normals


def test_fix_normals_repairs_inconsistent_winding(ax, inconsistent_winding_stl):
    # Independent oracle: a mesh with one face's winding reversed relative
    # to its neighbors is NOT winding-consistent; trimesh's adjacency-graph
    # repair should make it consistent again.
    result = fix_normals(ax, Mesh(data=inconsistent_winding_stl, format="STL"))
    assert result.is_winding_consistent is True
    assert len(result.mesh.data) > 0
    assert result.mesh.face_count == 12


def test_fix_normals_rejects_malformed_data(ax):
    try:
        fix_normals(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
