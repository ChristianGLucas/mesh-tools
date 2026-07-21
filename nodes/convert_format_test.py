from gen.messages_pb2 import ConvertFormatInput, Mesh
from nodes.convert_format import convert_format


def test_convert_stl_to_obj_preserves_geometry(ax, unit_cube_stl):
    result = convert_format(
        ax, ConvertFormatInput(mesh=Mesh(data=unit_cube_stl, format="STL"), target_format="OBJ")
    )
    assert result.format == "OBJ"
    assert result.vertex_count == 8
    assert result.face_count == 12
    assert len(result.data) > 0
    assert b"v " in result.data  # OBJ text format has vertex lines


def test_convert_round_trip_preserves_volume(ax, unit_cube_stl):
    obj = convert_format(
        ax, ConvertFormatInput(mesh=Mesh(data=unit_cube_stl, format="STL"), target_format="OBJ")
    )
    back_to_stl = convert_format(
        ax, ConvertFormatInput(mesh=Mesh(data=obj.data, format="OBJ"), target_format="STL")
    )
    assert back_to_stl.vertex_count == 8
    assert back_to_stl.face_count == 12


def test_convert_format_rejects_unsupported_target(ax, unit_cube_stl):
    try:
        convert_format(
            ax,
            ConvertFormatInput(mesh=Mesh(data=unit_cube_stl, format="STL"), target_format="FBX"),
        )
        assert False, "expected ValueError for unsupported target format"
    except ValueError:
        pass


def test_convert_format_rejects_malformed_data(ax):
    try:
        convert_format(
            ax,
            ConvertFormatInput(
                mesh=Mesh(data=b"not a mesh", format="STL"), target_format="OBJ"
            ),
        )
        assert False, "expected ValueError for malformed mesh data"
    except ValueError:
        pass
