from gen.messages_pb2 import Mesh, OrientedBoundingBoxOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3


def compute_oriented_bounding_box(ax: AxiomContext, input: Mesh) -> OrientedBoundingBoxOutput:
    """Compute the minimum-volume oriented bounding box of a mesh: the 4x4
    world transform of the box frame (row-major) and its extents/volume.
    The OBB volume is always <= the axis-aligned bounding box volume.
    """
    mesh = load_trimesh(input)
    obb = mesh.bounding_box_oriented
    transform = obb.primitive.transform.reshape(-1).tolist()
    extents = obb.primitive.extents
    return OrientedBoundingBoxOutput(
        transform=transform, extents=point3(*extents), volume=float(obb.volume)
    )
