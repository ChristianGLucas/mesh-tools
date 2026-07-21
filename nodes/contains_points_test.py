from gen.messages_pb2 import ContainsPointsInput, Mesh, Point3
from nodes.contains_points import contains_points


def test_contains_points_distinguishes_inside_and_outside(ax, unit_cube_stl):
    # Independent oracle: the origin is inside a unit cube centered on it;
    # (10,10,10) is far outside.
    result = contains_points(
        ax,
        ContainsPointsInput(
            mesh=Mesh(data=unit_cube_stl, format="STL"),
            points=[Point3(x=0, y=0, z=0), Point3(x=10, y=10, z=10)],
        ),
    )
    assert list(result.inside) == [True, False]
    assert result.is_watertight is True


def test_contains_points_rejects_no_points(ax, unit_cube_stl):
    try:
        contains_points(ax, ContainsPointsInput(mesh=Mesh(data=unit_cube_stl, format="STL")))
        assert False, "expected ValueError for zero points"
    except ValueError:
        pass


def test_contains_points_rejects_malformed_data(ax):
    try:
        contains_points(
            ax,
            ContainsPointsInput(
                mesh=Mesh(data=b"not a mesh", format="STL"), points=[Point3(x=0, y=0, z=0)]
            ),
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
