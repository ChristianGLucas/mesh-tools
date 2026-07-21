from gen.messages_pb2 import RayIntersectInput, Mesh, Point3
from nodes.ray_intersect import ray_intersect


def test_ray_through_cube_hits_top_and_bottom(ax, unit_cube_stl):
    # Independent oracle: a vertical ray through the center of a unit cube
    # (centered at the origin) enters at z=+0.5 and exits at z=-0.5 —
    # exactly two hits at those exact coordinates.
    result = ray_intersect(
        ax,
        RayIntersectInput(
            mesh=Mesh(data=unit_cube_stl, format="STL"),
            origins=[Point3(x=0, y=0, z=5)],
            directions=[Point3(x=0, y=0, z=-1)],
        ),
    )
    assert len(result.locations) == 2
    zs = sorted(round(p.z, 6) for p in result.locations)
    assert zs == [-0.5, 0.5]
    for p in result.locations:
        assert abs(p.x) < 1e-9 and abs(p.y) < 1e-9
    assert list(result.ray_hit) == [True]


def test_ray_missing_cube_reports_no_hit(ax, unit_cube_stl):
    result = ray_intersect(
        ax,
        RayIntersectInput(
            mesh=Mesh(data=unit_cube_stl, format="STL"),
            origins=[Point3(x=100, y=100, z=100)],
            directions=[Point3(x=0, y=0, z=-1)],
        ),
    )
    assert len(result.locations) == 0
    assert list(result.ray_hit) == [False]


def test_ray_intersect_rejects_mismatched_ray_arrays(ax, unit_cube_stl):
    try:
        ray_intersect(
            ax,
            RayIntersectInput(
                mesh=Mesh(data=unit_cube_stl, format="STL"),
                origins=[Point3(x=0, y=0, z=5), Point3(x=1, y=1, z=5)],
                directions=[Point3(x=0, y=0, z=-1)],
            ),
        )
        assert False, "expected ValueError for mismatched origins/directions lengths"
    except ValueError:
        pass


def test_ray_intersect_rejects_no_rays(ax, unit_cube_stl):
    try:
        ray_intersect(ax, RayIntersectInput(mesh=Mesh(data=unit_cube_stl, format="STL")))
        assert False, "expected ValueError for zero rays"
    except ValueError:
        pass


def test_ray_intersect_rejects_malformed_data(ax):
    try:
        ray_intersect(
            ax,
            RayIntersectInput(
                mesh=Mesh(data=b"not a mesh", format="STL"),
                origins=[Point3(x=0, y=0, z=5)],
                directions=[Point3(x=0, y=0, z=-1)],
            ),
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
