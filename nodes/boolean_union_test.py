from gen.messages_pb2 import BooleanInput, Mesh
from nodes.boolean_union import boolean_union


def test_union_of_half_overlapping_cubes(ax, unit_cube_stl, offset_cube_stl):
    # Independent oracle: two unit cubes, the second offset +0.5 on x,
    # overlap in a 0.5x1x1 region (volume 0.5). Union volume by
    # inclusion-exclusion = 1 + 1 - 0.5 = 1.5, computed by hand, not trimesh.
    result = boolean_union(
        ax,
        BooleanInput(
            a=Mesh(data=unit_cube_stl, format="STL"),
            b=Mesh(data=offset_cube_stl, format="STL"),
        ),
    )
    assert abs(result.volume - 1.5) < 1e-6
    assert result.is_watertight is True
    assert len(result.mesh.data) > 0


def test_boolean_union_rejects_malformed_data(ax, unit_cube_stl):
    try:
        boolean_union(
            ax,
            BooleanInput(
                a=Mesh(data=unit_cube_stl, format="STL"), b=Mesh(data=b"garbage", format="STL")
            ),
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
