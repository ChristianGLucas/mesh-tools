import numpy as np

from gen.messages_pb2 import SamplePointsInput, VolumePointsOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3_from_array, MAX_SAMPLE_COUNT


def sample_volume_points(ax: AxiomContext, input: SamplePointsInput) -> VolumePointsOutput:
    """Sample up to `count` points uniformly at random from a mesh's
    enclosed volume via rejection sampling: draw uniform points in the
    mesh's bounding box and keep the ones trimesh's `contains()` reports as
    inside. Requires (and is only meaningful for) a watertight mesh. Mirrors
    trimesh.sample.volume_mesh's exact algorithm but with a local, seeded
    RNG for determinism, so it may return fewer than `count` points for a
    single rejection pass over a low fill-ratio (thin/sparse) mesh — never more.
    """
    mesh = load_trimesh(input.mesh)
    if input.count <= 0:
        raise ValueError("count must be > 0")
    if input.count > MAX_SAMPLE_COUNT:
        raise ValueError(f"count too large: {input.count} (max {MAX_SAMPLE_COUNT})")
    if not mesh.is_watertight:
        raise ValueError("mesh must be watertight to sample its volume")
    rng = np.random.default_rng(int(input.seed))
    candidates = (rng.random((input.count, 3)) * mesh.extents) + mesh.bounds[0]
    inside = mesh.contains(candidates)
    points = candidates[inside][: input.count]
    return VolumePointsOutput(points=point3_from_array(points))
