import bmesh
import os
import mathutils
import math
import bpy

GRIDFINITY_PITCH = 0.042
GRIDFINITY_CLEARANCE = 0.0005
GRIDFINITY_BASE_HEIGHT = 0.00475


def create_baseplate_unit_mesh():
    """
    Create a single Gridfinity baseplate unit bmesh restricted to 4.75mm height.
    """
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.5]

    bmesh.ops.scale(bm, vec=(GRIDFINITY_PITCH, GRIDFINITY_PITCH, 0.00001), verts=bm.verts)
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

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)

    min_z = min(v.co.z for v in bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -min_z), verts=bm.verts)

    center_x = sum(v.co.x for v in bm.verts) / len(bm.verts)
    center_y = sum(v.co.y for v in bm.verts) / len(bm.verts)
    bmesh.ops.translate(bm, vec=(-center_x, -center_y, 0.0), verts=bm.verts)

    return bm


def create_magnet_cutter():
    """
    Creates the cutter bmesh for the magnet holes.
    """
    c_bm = bmesh.new()
    offsets = [(0.013, 0.013), (0.013, -0.013), (-0.013, 0.013), (-0.013, -0.013)]

    for ox, oy in offsets:
        mag = bmesh.ops.create_cone(c_bm, cap_ends=True, cap_tris=False, segments=64, radius1=0.00325, radius2=0.00325, depth=0.0034)
        bmesh.ops.translate(c_bm, vec=(ox, oy, 0.0007), verts=mag['verts'])

    return c_bm


def create_bin_mesh(nx, ny, height_mm, thickness_mm):
    """
    Create a hollow Gridfinity bin bmesh.
    """
    bm, height = _create_base_bin_geometry(nx, ny, height_mm)
    thickness = thickness_mm * 0.001
    extrude_depth = height - thickness

    _apply_top_inset_and_bevel(bm, thickness, extrude_depth)
    return bm


def create_solid_bin_mesh(nx, ny, height_mm, thickness_mm):
    """
    Create a solid Gridfinity bin bmesh.
    """
    bm, height = _create_base_bin_geometry(nx, ny, height_mm)
    thickness = thickness_mm * 0.001
    rim_depth = 0.002

    _apply_top_inset_and_bevel(bm, thickness, rim_depth)
    return bm


def _create_base_bin_geometry(nx, ny, height_mm):
    width = (nx * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    depth = (ny * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    height = height_mm * 0.001

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

    center_z = GRIDFINITY_BASE_HEIGHT + (height / 2.0)
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

    return bm, height


def _apply_top_inset_and_bevel(bm, thickness, extrude_depth):
    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -extrude_depth), verts=extruded_verts)

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


def generate_lip_array(nx, ny, use_magnets, use_infill):
    """
    Generates the merged lip array purely via data structures and matrix math,
    returning raw vertex coordinates and face indices.
    """
    if use_magnets:
        if use_infill:
            obj_l = load_reference_object("Gridfinity_baseplate_L_magnet")
            obj_t = load_reference_object("Gridfinity_baseplate_T_magnet_filled")
            obj_x = load_reference_object("Gridfinity_baseplate_X_magnet_filled")
        else:
            obj_l = load_reference_object("Gridfinity_baseplate_L_magnet")
            obj_t = load_reference_object("Gridfinity_baseplate_T_magnet")
            obj_x = load_reference_object("Gridfinity_baseplate_X_magnet")
    else:
        if use_infill:
            obj_l = load_reference_object("Gridfinity_baseplate_L")
            obj_t = load_reference_object("Gridfinity_baseplate_T_filled")
            obj_x = load_reference_object("Gridfinity_baseplate_X_filled")
        else:
            obj_l = load_reference_object("Gridfinity_baseplate_L")
            obj_t = load_reference_object("Gridfinity_baseplate_T")
            obj_x = load_reference_object("Gridfinity_baseplate_X")

    grid = [[True for _ in range(ny)] for _ in range(nx)]

    def cell_exists(cx, cy):
        if 0 <= cx < nx and 0 <= cy < ny:
            return grid[cx][cy]
        return False

    state_lookup = {
        (True, False, False, False): (obj_l, math.radians(180)),
        (False, True, False, False): (obj_l, math.radians(-90)),
        (False, False, True, False): (obj_l, math.radians(0)),
        (False, False, False, True): (obj_l, math.radians(90)),
        (True, True, False, False):  (obj_t, math.radians(180)),
        (False, True, True, False):  (obj_t, math.radians(-90)),
        (False, False, True, True):  (obj_t, math.radians(0)),
        (True, False, False, True):  (obj_t, math.radians(90)),
        (True, True, True, True):    (obj_x, math.radians(0))
    }

    all_verts = []
    all_faces = []
    vert_offset = 0

    for x in range(nx + 1):
        for y in range(ny + 1):
            tr = cell_exists(x, y)
            tl = cell_exists(x - 1, y)
            bl = cell_exists(x - 1, y - 1)
            br = cell_exists(x, y - 1)

            state = (tr, tl, bl, br)

            if state not in state_lookup:
                continue

            source_obj, rotation_z = state_lookup[state]
            source_mesh = source_obj.data

            matrix = mathutils.Matrix.Translation((x * GRIDFINITY_PITCH, y * GRIDFINITY_PITCH, 0.0)) @ mathutils.Matrix.Rotation(rotation_z, 4, 'Z')

            for v in source_mesh.vertices:
                all_verts.append(matrix @ v.co)

            for p in source_mesh.polygons:
                all_faces.append([v + vert_offset for v in p.vertices])

            vert_offset += len(source_mesh.vertices)

    mesh_l = obj_l.data
    mesh_t = obj_t.data
    mesh_x = obj_x.data

    bpy.data.objects.remove(obj_l, do_unlink=True)
    bpy.data.objects.remove(obj_t, do_unlink=True)
    bpy.data.objects.remove(obj_x, do_unlink=True)

    if mesh_l.users == 0:
        bpy.data.meshes.remove(mesh_l)
    if mesh_t.users == 0:
        bpy.data.meshes.remove(mesh_t)
    if mesh_x.users == 0:
        bpy.data.meshes.remove(mesh_x)

    return all_verts, all_faces


def load_reference_object(object_name):
    """
    Appends geometry safely from the internal geometry.blend file using bpy.data.libraries.
    Raises exceptions instead of returning None on failure.
    """
    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, "geometry", "geometry.blend")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Blend file missing at: {filepath}")

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        if object_name not in data_from.objects:
            raise ValueError(f"Object '{object_name}' not found in geometry.blend")

        data_to.objects = [object_name]

    if not data_to.objects or data_to.objects[0] is None:
        raise RuntimeError(f"Failed to load object '{object_name}'")

    return data_to.objects[0]
