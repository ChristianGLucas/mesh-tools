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

## Use it from your agent or app

Every node in this package is a **live, auto-scaling API endpoint** on the
[Axiom](https://axiomide.com) marketplace — call it from an AI agent or your own
code, with nothing to self-host.

**📦 See it on the marketplace:**
https://dev.axiomide.com/marketplace/christiangeorgelucas/mesh-tools@0.1.0

**Hook it up to an AI agent (MCP).** Add Axiom's hosted MCP server to any MCP
client and every node becomes a typed tool your agent can call — search the
catalog, inspect a schema, and invoke it directly.

```bash
# Claude Code
claude mcp add --transport http axiom https://api.axiomide.com/mcp \
  --header "Authorization: Bearer $AXIOM_API_KEY"
```

Claude Desktop, Cursor, or any config-based client:

```json
{
  "mcpServers": {
    "axiom": {
      "type": "http",
      "url": "https://api.axiomide.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_AXIOM_API_KEY" }
    }
  }
}
```

**Call it from the CLI.**

```bash
axiom invoke christiangeorgelucas/mesh-tools/ConvertFormat --input '{ ... }'
```

**Call it over HTTP.**

```bash
curl -X POST https://api.axiomide.com/invocations/v1/nodes/christiangeorgelucas/mesh-tools/0.1.0/ConvertFormat \
  -H "Authorization: Bearer $AXIOM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{ ... }'
```

> Input/output schema for each node is on the marketplace page above, or via
> `axiom inspect node christiangeorgelucas/mesh-tools/ConvertFormat`.

### Get started free

Install the CLI:

```bash
# macOS / Linux — Homebrew
brew install axiomide/tap/axiom

# macOS / Linux — install script
curl -fsSL https://raw.githubusercontent.com/AxiomIDE/axiom-releases/main/install.sh | sh
```

**Windows:** download the `windows/amd64` `.zip` from the
[releases page](https://github.com/AxiomIDE/axiom-releases/releases), unzip it,
and put `axiom.exe` on your `PATH`.

Then `axiom version` to verify, `axiom login` (GitHub or Google) to authenticate,
and create an API key under **Console → API Keys**. Docs and sign-up at
**[axiomide.com](https://axiomide.com)**.

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
