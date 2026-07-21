import numpy as np

from gen.messages_pb2 import SamplePointsInput, Mesh
from nodes.sample_surface_points import sample_surface_points


def test_sample_surface_points_lie_on_cube_surface(ax, unit_cube_stl):
    result = sample_surface_points(
        ax, SamplePointsInput(mesh=Mesh(data=unit_cube_stl, format="STL"), count=200, seed=42)
    )
    assert len(result.points) == 200
    assert len(result.face_indices) == 200
    pts = np.array([[p.x, p.y, p.z] for p in result.points])
    # Independent oracle: every point sampled from a unit cube's surface
    # must lie within the cube's own bounds, AND touch at least one face
    # (be at the +/-0.5 boundary on at least one axis).
    assert np.all(np.abs(pts) <= 0.5 + 1e-9)
    on_boundary = np.any(np.isclose(np.abs(pts), 0.5, atol=1e-9), axis=1)
    assert np.all(on_boundary)


def test_sample_surface_points_deterministic_for_same_seed(ax, unit_cube_stl):
    input_msg = SamplePointsInput(mesh=Mesh(data=unit_cube_stl, format="STL"), count=50, seed=7)
    r1 = sample_surface_points(ax, input_msg)
    r2 = sample_surface_points(ax, input_msg)
    assert [(p.x, p.y, p.z) for p in r1.points] == [(p.x, p.y, p.z) for p in r2.points]
    assert list(r1.face_indices) == list(r2.face_indices)


def test_sample_surface_points_rejects_non_positive_count(ax, unit_cube_stl):
    try:
        sample_surface_points(
            ax, SamplePointsInput(mesh=Mesh(data=unit_cube_stl, format="STL"), count=0)
        )
        assert False, "expected ValueError for count <= 0"
    except ValueError:
        pass


def test_sample_surface_points_rejects_malformed_data(ax):
    try:
        sample_surface_points(
            ax, SamplePointsInput(mesh=Mesh(data=b"not a mesh", format="STL"), count=10)
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
