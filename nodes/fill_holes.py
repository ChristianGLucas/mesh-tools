from gen.messages_pb2 import Mesh, FillHolesOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, encode


def fill_holes(ax: AxiomContext, input: Mesh) -> FillHolesOutput:
    """Triangulate and close boundary holes (trimesh.Trimesh.fill_holes),
    attempting to make the mesh watertight. Returns the repaired mesh, plus
    whether every hole was successfully filled and the resulting
    watertight status.
    """
    mesh = load_trimesh(input)
    fully_filled = bool(mesh.fill_holes())
    out_fmt = input.format or "STL"
    return FillHolesOutput(
        mesh=Mesh(**encode(mesh, out_fmt)),
        fully_filled=fully_filled,
        is_watertight=bool(mesh.is_watertight),
    )
