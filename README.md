# mesh-tools

Composable [Axiom](https://axiomide.com) nodes for 3D triangle-mesh geometry —
load, inspect, measure, repair, simplify, boolean-combine, sample, and
ray/point-query STL/OBJ/PLY/GLB meshes. Built for the Axiom marketplace under
the `christiangeorgelucas` handle.

All nodes wrap [trimesh](https://trimesh.org) (MIT), with permissively
-licensed optional backends: [manifold3d](https://github.com/elalish/manifold)
(Apache-2.0) for boolean operations and
[fast-simplification](https://github.com/pyvista/fast-simplification) (MIT)
for mesh decimation. Deliberately **not** a dependency: `rtree` (LGPL-2.1,
trimesh's default ray/spatial-index backend) and `shapely`/`GEOS` (LGPL-2.1,
needed for plane-slicing/cross-sections) — see `nodes/_mesh.py` for how
ray-casting and point-containment avoid needing `rtree` at all, via a
pure-numpy broad-phase substitute that still lets trimesh's own ray-triangle
math do the real work.

## The `Mesh` envelope

Every node that returns a mesh returns the same canonical `Mesh` message
(bytes + format + vertex/face counts, with an input-only `url` convenience
field), and every node that consumes a mesh accepts it — so flows compose
with a trivial single-field edge.

## Nodes

- **ConvertFormat** — re-encode a mesh between STL/OBJ/PLY/GLB.
- **InspectMesh** — structural + topological summary (vertex/face counts,
  bounds, watertightness, winding consistency, Euler number, body count).
- **ComputeVolume**, **ComputeSurfaceArea**, **ComputeCenterOfMass**,
  **ComputeMomentOfInertia** — standard solid-geometry properties.
- **ComputeBoundingBox**, **ComputeOrientedBoundingBox** — axis-aligned and
  minimum-volume oriented bounding boxes.
- **ComputeConvexHull** — the mesh's convex hull as a new watertight mesh.
- **FixNormals**, **FillHoles** — winding/hole repair.
- **SimplifyMesh** — quadric-error-metric decimation to a target face count.
- **BooleanUnion**, **BooleanIntersection**, **BooleanDifference** — exact
  boolean combination of two watertight meshes (via manifold3d).
- **SampleSurfacePoints**, **SampleVolumePoints** — deterministic seeded
  point sampling over a mesh's surface or enclosed volume.
- **RayIntersect** — ray/mesh intersection points, triangle indices, per-ray
  hit flags.
- **ContainsPoints** — point-in-mesh (inside/outside) testing.

## License

MIT — see [LICENSE](./LICENSE).
