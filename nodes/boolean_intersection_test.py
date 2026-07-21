from gen.messages_pb2 import BooleanInput, Mesh
from nodes.boolean_intersection import boolean_intersection


def test_intersection_of_half_overlapping_cubes(ax, unit_cube_stl, offset_cube_stl):
    # Independent oracle: two unit cubes offset by 0.5 on x overlap in
    # exactly a 0.5x1x1 region -> intersection volume 0.5, computed by hand.
    result = boolean_intersection(
        ax,
        BooleanInput(
            a=Mesh(data=unit_cube_stl, format="STL"),
            b=Mesh(data=offset_cube_stl, format="STL"),
        ),
    )
    assert abs(result.volume - 0.5) < 1e-6
    assert result.is_watertight is True


def test_boolean_intersection_rejects_malformed_data(ax, unit_cube_stl):
    try:
        boolean_intersection(
            ax,
            BooleanInput(
                a=Mesh(data=unit_cube_stl, format="STL"), b=Mesh(data=b"garbage", format="STL")
            ),
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
