"""
Geometry generation functions for Gridfinity objects.
Handles all mesh creation and manipulation logic.
"""

import bpy
import bmesh


def create_baseplate_unit_mesh(context):
    """
    Create a single Gridfinity baseplate unit restricted to 4.75mm height.
    Origin is at (0, 0, 0) - center of geometry in X/Y, bottom at Z=0.

    Args:
        context: Blender context

    Returns:
        bpy.types.Object: The created baseplate unit object
    """
    mesh = bpy.data.meshes.new("Gridfinity_Baseplate_Mesh")
    obj = bpy.data.objects.new("Gridfinity_Baseplate", mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    # Identify vertical edges before scaling to avoid floating point precision issues
    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.5]

    # Scale to correct X and Y but use minimal Z thickness for top face creation
    bmesh.ops.scale(bm, vec=(0.0415, 0.0415, 0.00001), verts=bm.verts)

    # Translate to position Z at bottom (not +0.00475)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.0), verts=bm.verts)

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    bottom_face = min(bm.faces, key=lambda f: f.calc_center_median().z)

    if bottom_face:
        bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=0.00215)
        for vert in bottom_face.verts:
            vert.co.z -= 0.00215

        bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=0.00001)
        for vert in bottom_face.verts:
            vert.co.z -= 0.0018

        bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=0.0008)
        for vert in bottom_face.verts:
            vert.co.z -= 0.0008

    # Merge the micro thickness to create a perfectly flat solid top face
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)

    # Zero out the precise height to align perfectly with the floor
    min_z = min(v.co.z for v in bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -min_z), verts=bm.verts)

    # Center X and Y
    center_x = sum(v.co.x for v in bm.verts) / len(bm.verts)
    center_y = sum(v.co.y for v in bm.verts) / len(bm.verts)
    bmesh.ops.translate(bm, vec=(-center_x, -center_y, 0.0), verts=bm.verts)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return obj


def create_bin_mesh(context, nx, ny, height_mm, thickness_mm):
    """
    Create a hollow Gridfinity bin on top of the baseplate with inner bottom bevel.
    Origin is at (0, 0, 0) - center of geometry in X/Y, bottom at Z=0.

    Args:
        context: Blender context
        nx: Number of units in X direction
        ny: Number of units in Y direction
        height_mm: Bin height in millimeters
        thickness_mm: Bin wall thickness in millimeters

    Returns:
        bpy.types.Object: The created bin object
    """
    unit_size = 0.0415
    spacing = 0.001
    pitch = unit_size + spacing

    width = unit_size + (nx - 1) * pitch
    depth = unit_size + (ny - 1) * pitch
    height = height_mm * 0.001
    thickness = thickness_mm * 0.001
    base_height = 0.00475

    mesh = bpy.data.meshes.new("Gridfinity_Bin_Mesh")
    obj = bpy.data.objects.new("Gridfinity_Bin", mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

    # Position at Z=0 bottom, centered X/Y at origin
    center_z = base_height + (height / 2.0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, center_z), verts=bm.verts)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.001]

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -(height - thickness)), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    inner_bottom_edges = [e for e in bm.edges if e.verts[0] in extruded_verts and e.verts[1] in extruded_verts]

    bmesh.ops.bevel(
        bm,
        geom=inner_bottom_edges,
        offset=0.001,
        segments=8,
        profile=0.5,
        affect='EDGES'
    )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return obj


def create_solid_bin_mesh(context, nx, ny, height_mm, thickness_mm):
    """
    Create a solid Gridfinity bin with a 2mm top rim and inner bottom bevel.
    Origin is at (0, 0, 0) - center of geometry in X/Y, bottom at Z=0.

    Args:
        context: Blender context
        nx: Number of units in X direction
        ny: Number of units in Y direction
        height_mm: Bin height in millimeters
        thickness_mm: Bin wall thickness in millimeters

    Returns:
        bpy.types.Object: The created solid bin object
    """
    unit_size = 0.0415
    spacing = 0.001
    pitch = unit_size + spacing

    width = unit_size + (nx - 1) * pitch
    depth = unit_size + (ny - 1) * pitch
    height = height_mm * 0.001
    thickness = thickness_mm * 0.001
    base_height = 0.00475
    rim_depth = 0.002

    mesh = bpy.data.meshes.new("Gridfinity_Solid_Bin_Mesh")
    obj = bpy.data.objects.new("Gridfinity_Solid_Bin", mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

    # Position at Z=0 bottom, centered X/Y at origin
    center_z = base_height + (height / 2.0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, center_z), verts=bm.verts)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.001]

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -rim_depth), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    inner_bottom_edges = [e for e in bm.edges if e.verts[0] in extruded_verts and e.verts[1] in extruded_verts]

    bmesh.ops.bevel(
        bm,
        geom=inner_bottom_edges,
        offset=0.001,
        segments=8,
        profile=0.5,
        affect='EDGES'
    )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return obj


def create_stacking_lip_mesh(context):
    """
    Create full Gridfinity stacking lip profile generation with closed manifold bottom.

    Args:
        context: Blender context

    Returns:
        bpy.types.Object: The created stacking lip object
    """
    mesh = bpy.data.meshes.new("Gridfinity_Stacking_Lip")
    obj = bpy.data.objects.new("Gridfinity_Stacking_Lip", mesh)
    context.collection.objects.link(obj)

    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()

    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.021)
    bmesh.ops.bevel(bm, geom=bm.verts, offset=0.008, segments=32, profile=0.5, affect='VERTICES')

    bm.faces.ensure_lookup_table()
    bottom_face = bm.faces[0]

    res = bmesh.ops.extrude_face_region(bm, geom=[bottom_face])
    ext_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.005), verts=ext_verts)

    top_face = [f for f in bm.faces if all(v in ext_verts for v in f.verts) and f.normal.z > 0.5][0]

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.00215)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.00215), verts=top_face.verts)

    bm.faces.ensure_lookup_table()

    bottom_faces = [f for f in bm.faces if abs(f.calc_center_median().z) < 0.0001]

    bmesh.ops.delete(bm, geom=bottom_faces, context='FACES')

    bm.faces.ensure_lookup_table()

    horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

    if horizontal_faces:

        top_face = max(horizontal_faces, key=lambda f: f.calc_area())

        res = bmesh.ops.extrude_face_region(bm, geom=[top_face])
        ext_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.0018), verts=ext_verts)

        bmesh.ops.delete(bm, geom=[top_face], context='FACES')

    horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

    if horizontal_faces:

        top_face = max(horizontal_faces, key=lambda f: f.calc_area())

        res = bmesh.ops.extrude_face_region(bm, geom=[top_face])
        ext_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
        current_z = ext_verts[0].co.z
        bmesh.ops.translate(bm, vec=(0.0, 0.0, -current_z), verts=ext_verts)

        bmesh.ops.delete(bm, geom=[top_face], context='FACES')

    bm.faces.ensure_lookup_table()
    bm.normal_update()

    horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

    if horizontal_faces:
        top_face = max(horizontal_faces, key=lambda f: f.calc_area())

        inner_edges = [e for e in top_face.edges if e.calc_length() < 0.040]

        bmesh.ops.bevel(
            bm,
            geom=inner_edges,
            offset=0.0008,
            segments=1,
            profile=0.5,
            affect='EDGES'
        )

    horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

    if horizontal_faces:
        top_face = max(horizontal_faces, key=lambda f: f.calc_area())
        bmesh.ops.delete(bm, geom=[top_face], context='FACES')

    bm.edges.ensure_lookup_table()
    bottom_edges = [e for e in bm.edges if abs(e.verts[0].co.z) < 0.0001 and abs(e.verts[1].co.z) < 0.0001]

    if len(bottom_edges) > 0:
        bmesh.ops.bridge_loops(bm, edges=bottom_edges)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return obj
