from gen.messages_pb2 import SimplifyMeshInput, Mesh
from nodes.simplify_mesh import simplify_mesh


def test_simplify_reduces_sphere_to_target_face_count(ax, sphere_stl, sphere_face_count):
    assert sphere_face_count == 1280  # icosphere(subdivisions=3) — known face count
    result = simplify_mesh(
        ax,
        SimplifyMeshInput(mesh=Mesh(data=sphere_stl, format="STL"), target_face_count=100),
    )
    assert result.face_count <= 100
    assert result.face_count > 0
    assert len(result.mesh.data) > 0


def test_simplify_clamps_target_above_original_face_count(ax, unit_cube_stl):
    # 12-face cube, asking for 10000 faces should clamp to the original.
    result = simplify_mesh(
        ax,
        SimplifyMeshInput(mesh=Mesh(data=unit_cube_stl, format="STL"), target_face_count=10000),
    )
    assert result.face_count <= 12


def test_simplify_mesh_rejects_non_positive_target(ax, unit_cube_stl):
    try:
        simplify_mesh(
            ax,
            SimplifyMeshInput(mesh=Mesh(data=unit_cube_stl, format="STL"), target_face_count=0),
        )
        assert False, "expected ValueError for non-positive target_face_count"
    except ValueError:
        pass


def test_simplify_mesh_rejects_malformed_data(ax):
    try:
        simplify_mesh(
            ax, SimplifyMeshInput(mesh=Mesh(data=b"not a mesh", format="STL"), target_face_count=4)
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
