from gen.messages_pb2 import Mesh
from nodes.compute_volume import compute_volume


def test_unit_cube_volume_is_one(ax, unit_cube_stl):
    # Independent oracle: a 1x1x1 cube has volume 1 by definition.
    result = compute_volume(ax, Mesh(data=unit_cube_stl, format="STL"))
    assert result.volume == 1.0
    assert result.is_watertight is True


def test_compute_volume_rejects_malformed_data(ax):
    try:
        compute_volume(ax, Mesh(data=b"not a mesh", format="STL"))
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass


def test_compute_volume_rejects_missing_input(ax):
    try:
        compute_volume(ax, Mesh(format="STL"))
        assert False, "expected ValueError for missing data/url"
    except ValueError:
        pass
