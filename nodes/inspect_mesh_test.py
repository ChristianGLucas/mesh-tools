from gen.messages_pb2 import Mesh
from nodes.inspect_mesh import inspect_mesh


def test_inspect_unit_cube_matches_known_topology(ax, unit_cube_stl):
    result = inspect_mesh(ax, Mesh(data=unit_cube_stl, format="STL"))
    # Independent oracle: a cube has 8 vertices, 12 triangular faces, is a
    # closed genus-0 solid (Euler number V-E+F = 8-18+12 = 2), one body,
    # and is watertight with consistent winding.
    assert result.vertex_count == 8
    assert result.face_count == 12
    assert result.is_watertight is True
    assert result.is_winding_consistent is True
    assert result.euler_number == 2
    assert result.body_count == 1
    assert (result.bounds_min.x, result.bounds_min.y, result.bounds_min.z) == (-0.5, -0.5, -0.5)
    assert (result.bounds_max.x, result.bounds_max.y, result.bounds_max.z) == (0.5, 0.5, 0.5)
    assert (result.extents.x, result.extents.y, result.extents.z) == (1.0, 1.0, 1.0)


def test_inspect_ascii_stl_variant_parses_correctly(ax, unit_cube_ascii_stl):
    # Regression test: trimesh's ASCII-STL loader path needs
    # charset_normalizer (pinned in requirements.txt) to detect text
    # encoding — without it this variant fails to parse in a deployed
    # environment that lacks the transitive dep, even though it's a
    # legitimate, common STL variant.
    result = inspect_mesh(ax, Mesh(data=unit_cube_ascii_stl, format="STL"))
    assert result.vertex_count == 8
    assert result.face_count == 12
    assert result.is_watertight is True


def test_inspect_holey_mesh_is_not_watertight(ax, holey_cube_stl):
    result = inspect_mesh(ax, Mesh(data=holey_cube_stl, format="STL"))
    assert result.is_watertight is False


def test_inspect_mesh_rejects_missing_data_and_url(ax):
    try:
        inspect_mesh(ax, Mesh(format="STL"))
        assert False, "expected ValueError for missing data/url"
    except ValueError:
        pass


def test_inspect_mesh_rejects_malformed_data(ax):
    try:
        inspect_mesh(ax, Mesh(data=b"garbage", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
