import trimesh.sample as sample

from gen.messages_pb2 import SamplePointsInput, SurfacePointsOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3_from_array, MAX_SAMPLE_COUNT


def sample_surface_points(ax: AxiomContext, input: SamplePointsInput) -> SurfacePointsOutput:
    """Sample `count` points uniformly at random (by triangle area) from a
    mesh's surface, via trimesh.sample.sample_surface. Deterministic for a
    given (mesh, count, seed).
    """
    mesh = load_trimesh(input.mesh)
    if input.count <= 0:
        raise ValueError("count must be > 0")
    if input.count > MAX_SAMPLE_COUNT:
        raise ValueError(f"count too large: {input.count} (max {MAX_SAMPLE_COUNT})")
    points, face_indices = sample.sample_surface(mesh, input.count, seed=int(input.seed))
    return SurfacePointsOutput(
        points=point3_from_array(points), face_indices=[int(i) for i in face_indices]
    )
