from gen.messages_pb2 import ConvertFormatInput, Mesh
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, encode


def convert_format(ax: AxiomContext, input: ConvertFormatInput) -> Mesh:
    """Re-encode a mesh (STL/OBJ/PLY/GLB, inline `data` or fetched `url`) into
    another of those formats, returning the converted bytes as a canonical
    Mesh. Geometry is preserved as-is; no processing/repair is applied.
    """
    mesh = load_trimesh(input.mesh)
    return Mesh(**encode(mesh, input.target_format))
