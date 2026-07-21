import numpy as np

from gen.messages_pb2 import SamplePointsInput, Mesh
from nodes.sample_volume_points import sample_volume_points


def test_sample_volume_points_lie_inside_cube(ax, unit_cube_stl):
    result = sample_volume_points(
        ax, SamplePointsInput(mesh=Mesh(data=unit_cube_stl, format="STL"), count=200, seed=42)
    )
    assert len(result.points) > 0
    pts = np.array([[p.x, p.y, p.z] for p in result.points])
    # Independent oracle: any point inside a unit cube centered at the
    # origin must have every coordinate strictly within [-0.5, 0.5].
    assert np.all(np.abs(pts) <= 0.5 + 1e-9)


def test_sample_volume_points_deterministic_for_same_seed(ax, unit_cube_stl):
    input_msg = SamplePointsInput(mesh=Mesh(data=unit_cube_stl, format="STL"), count=50, seed=7)
    r1 = sample_volume_points(ax, input_msg)
    r2 = sample_volume_points(ax, input_msg)
    assert [(p.x, p.y, p.z) for p in r1.points] == [(p.x, p.y, p.z) for p in r2.points]


def test_sample_volume_points_rejects_non_watertight_mesh(ax, holey_cube_stl):
    try:
        sample_volume_points(
            ax, SamplePointsInput(mesh=Mesh(data=holey_cube_stl, format="STL"), count=10)
        )
        assert False, "expected ValueError for non-watertight mesh"
    except ValueError:
        pass


def test_sample_volume_points_rejects_malformed_data(ax):
    try:
        sample_volume_points(
            ax, SamplePointsInput(mesh=Mesh(data=b"not a mesh", format="STL"), count=10)
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
