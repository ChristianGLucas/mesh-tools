from gen.messages_pb2 import BooleanInput, Mesh
from nodes.boolean_difference import boolean_difference


def test_difference_of_half_overlapping_cubes(ax, unit_cube_stl, offset_cube_stl):
    # Independent oracle: a - b where a and b are unit cubes overlapping in
    # a 0.5x1x1 region -> difference volume = 1 - 0.5 = 0.5, computed by hand.
    result = boolean_difference(
        ax,
        BooleanInput(
            a=Mesh(data=unit_cube_stl, format="STL"),
            b=Mesh(data=offset_cube_stl, format="STL"),
        ),
    )
    assert abs(result.volume - 0.5) < 1e-6
    assert result.is_watertight is True


def test_boolean_difference_rejects_malformed_data(ax, unit_cube_stl):
    try:
        boolean_difference(
            ax,
            BooleanInput(
                a=Mesh(data=unit_cube_stl, format="STL"), b=Mesh(data=b"garbage", format="STL")
            ),
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
