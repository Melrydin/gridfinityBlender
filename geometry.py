import bmesh
import os
import mathutils
import math
import bpy

GRIDFINITY_PITCH = 0.042
GRIDFINITY_CLEARANCE = 0.0005
GRIDFINITY_BASE_HEIGHT = 0.00475

_GEOMETRY_CACHE = {}


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


def create_bin_mesh(nx, ny, height_mm, thickness_mm, add_profile=False, add_label_tab=False):
    """
    Create a hollow Gridfinity bin bmesh.
    """
    bm, height = _create_base_bin_geometry(nx, ny, height_mm)
    thickness = thickness_mm * 0.001
    extrude_depth = height - thickness

    _apply_top_inset_and_bevel(bm, thickness, extrude_depth, add_profile)

    if add_label_tab:
        _apply_label_tab(bm)

    return bm


def create_solid_bin_mesh(nx, ny, height_mm, thickness_mm, add_profile=False):
    """
    Create a solid Gridfinity bin bmesh.
    """
    bm, _ = _create_base_bin_geometry(nx, ny, height_mm)
    thickness = thickness_mm * 0.001
    rim_depth = 0.002
    if add_profile:
        rim_depth += 0.0044


    _apply_top_inset_and_bevel(bm, thickness, rim_depth, add_profile)
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


def _apply_top_inset_and_bevel(bm, thickness, extrude_depth, add_profile):
    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)

    if add_profile:
        top_face.normal_flip()
        bm.normal_update()
        top_face, profile_depth = _apply_bin_top_profile(bm, top_face)
        extrude_depth -= profile_depth
    else:
        bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -extrude_depth), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    inner_bottom_edges = [e for e in bm.edges if e.verts[0] in extruded_verts and e.verts[1] in extruded_verts]

    if inner_bottom_edges:
        bmesh.ops.bevel(
            bm,
            geom=inner_bottom_edges,
            offset=0.001,
            segments=8,
            profile=0.5,
            affect='EDGES'
        )

    if add_profile:
        bm.normal_update()
        bm.faces.ensure_lookup_table()

        flat_faces = [f for f in bm.faces if abs(f.normal.z) > 0.9]

        if flat_faces:
            flat_faces.sort(key=lambda f: f.calc_area(), reverse=True)
            largest_candidates = flat_faces[:2]
            target_face = max(largest_candidates, key=lambda f: f.calc_center_median().z)

            verts_to_delete = list(target_face.verts)
            bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

def _apply_bin_top_profile(bm, top_face):
    """
    Creates the stacking lip profile on the top face of the bin.
    Returns the inner face and the Z depth of the profile.
    """

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.0019, depth=0.0019)

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.0, depth=0.0018)

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.0007, depth=0.0007)

    extrude_drop = bmesh.ops.extrude_face_region(bm, geom=[top_face])
    drop_verts = [elem for elem in extrude_drop['geom'] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.00045), verts=drop_verts)

    profile_depth = 0.0044
    return top_face, profile_depth

def _apply_label_tab(bm):
    """
    Creates an angled label tab strictly on the inner front wall of the bin
    with triangular tapered top corners.
    """
    bm.faces.ensure_lookup_table()

    front_faces = [
        f for f in bm.faces
        if f.normal.y > 0.999
        and f.calc_center_median().z > 0.005
        and f.calc_center_median().y < 0.0
    ]

    if not front_faces:
        return

    main_front_face = max(front_faces, key=lambda f: f.calc_area())

    cavity_top_z = max(v.co.z for v in main_front_face.verts)
    cavity_bottom_z = min(v.co.z for v in main_front_face.verts)

    tab_height = 0.01
    tab_angle_depth = 0.006

    tab_top_z = cavity_top_z - 0.001
    tab_bottom_z = tab_top_z - tab_height

    if tab_bottom_z <= cavity_bottom_z:
        tab_bottom_z = cavity_bottom_z + 0.001

    all_geom_1 = bm.faces[:] + bm.edges[:] + bm.verts[:]
    bmesh.ops.bisect_plane(bm, geom=all_geom_1, plane_co=(0.0, 0.0, tab_bottom_z), plane_no=(0.0, 0.0, 1.0))

    bm.faces.ensure_lookup_table()
    all_geom_2 = bm.faces[:] + bm.edges[:] + bm.verts[:]
    bmesh.ops.bisect_plane(bm, geom=all_geom_2, plane_co=(0.0, 0.0, tab_top_z), plane_no=(0.0, 0.0, 1.0))

    bm.faces.ensure_lookup_table()

    target_faces = [
        f for f in bm.faces
        if f.normal.y > 0.999
        and f.calc_center_median().z > tab_bottom_z + 0.0001
        and f.calc_center_median().z < tab_top_z - 0.0001
        and f.calc_center_median().y < 0.0
    ]

    if not target_faces:
        return

    extrude_res = bmesh.ops.extrude_face_region(bm, geom=target_faces)
    extruded_verts = [elem for elem in extrude_res['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.delete(bm, geom=target_faces, context='FACES_ONLY')

    bmesh.ops.translate(bm, vec=(0.0, tab_angle_depth, 0.0), verts=extruded_verts)

    bottom_verts = [v for v in extruded_verts if abs(v.co.z - tab_bottom_z) < 0.0005]
    bmesh.ops.translate(bm, vec=(0.0, -tab_angle_depth, 0.0), verts=bottom_verts)

    min_x = min(v.co.x for v in extruded_verts)
    max_x = max(v.co.x for v in extruded_verts)
    side_margin = 0.004

    left_top_verts = [v for v in extruded_verts if abs(v.co.x - min_x) < 0.0005 and v not in bottom_verts]
    right_top_verts = [v for v in extruded_verts if abs(v.co.x - max_x) < 0.0005 and v not in bottom_verts]

    bmesh.ops.translate(bm, vec=(side_margin, 0.0, 0.0), verts=left_top_verts)
    bmesh.ops.translate(bm, vec=(-side_margin, 0.0, 0.0), verts=right_top_verts)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

def create_tab_text_object(params):
    """
    Creates a text curve object positioned and rotated for the label tab.
    Does not link to the scene or evaluate modifiers.
    """

    total_height = GRIDFINITY_BASE_HEIGHT + (params['height_mm'] * 0.001)
    tab_top_z = total_height - 0.001

    center_z = tab_top_z

    depth_y = (params['ny'] * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    inner_front_y = -(depth_y / 2.0) + (params['thickness_mm'] * 0.001)
    center_y = inner_front_y + 0.0025

    curve = bpy.data.curves.new(type="FONT", name="LabelCurve")
    curve.body = params['label_text']
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'

    extrude_depth = min(0.6, params['thickness_mm'] * 0.5) * 0.001
    curve.extrude = extrude_depth

    text_obj = bpy.data.objects.new("LabelObj_Temp", curve)
    text_obj.location = (0.0, center_y, center_z)

    text_obj.scale = (0.005, 0.005, 1.0)
    text_obj.rotation_euler = (0.0, 0.0, math.radians(180))

    return text_obj

def create_lid_mesh(nx, ny, thickness_mm, wall_thickness_mm, tolerance_mm):
    """
    Create a Gridfinity lid base and extrude the inner alignment plug.
    """
    bm = bmesh.new()

    width = (nx * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    depth = (ny * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    thickness = thickness_mm * 0.001
    plug_height = 0.003

    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width, depth, thickness), verts=bm.verts)

    center_z = plug_height + (thickness / 2.0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, center_z), verts=bm.verts)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.0001]

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.faces.ensure_lookup_table()
    bottom_face = min(bm.faces, key=lambda f: f.calc_center_median().z)

    inset_thickness = (wall_thickness_mm + (tolerance_mm / 2.0)) * 0.001
    bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=inset_thickness)

    extrude_result = bmesh.ops.extrude_face_region(bm, geom=[bottom_face])
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -plug_height), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return bm

def apply_stacking_profile_to_lid(bm):
    """
    Extends the top face of the lid upwards and extrudes the
    Gridfinity negative profile cavity into it.
    """
    bm.faces.ensure_lookup_table()

    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)

    lip_total_height = 0.0044
    extrude_up = bmesh.ops.extrude_face_region(bm, geom=[top_face])
    top_verts = [elem for elem in extrude_up['geom'] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, lip_total_height), verts=top_verts)

    current_top_face = None
    for elem in extrude_up['geom']:
        if isinstance(elem, bmesh.types.BMFace) and elem.normal.z > 0.9:
            current_top_face = elem
            break

    if not current_top_face:
        return bm

    bmesh.ops.inset_region(bm, faces=[current_top_face], thickness=0.0019, depth=-0.0019)

    bmesh.ops.inset_region(bm, faces=[current_top_face], thickness=0.0, depth=-0.0018)

    bmesh.ops.inset_region(bm, faces=[current_top_face], thickness=0.0007, depth=-0.0007)

    extrude_drop = bmesh.ops.extrude_face_region(bm, geom=[current_top_face])
    drop_verts = [elem for elem in extrude_drop['geom'] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.00045), verts=drop_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return bm

def generate_lip_array(nx, ny, use_magnets, use_infill, stackable_baseplate):
    """
    Generates the merged lip array purely via data structures and matrix math.
    Uses highly optimized list comprehensions and a separate cache function.
    """
    precalc_data = get_cached_geometry(use_magnets, use_infill, stackable_baseplate)

    grid = [[True for _ in range(ny)] for _ in range(nx)]

    def cell_exists(cx, cy):
        if 0 <= cx < nx and 0 <= cy < ny:
            return grid[cx][cy]
        return False

    all_verts = []
    all_faces = []
    vert_offset = 0

    pitch = GRIDFINITY_PITCH
    append_verts = all_verts.extend
    append_faces = all_faces.extend

    for x in range(nx + 1):
        tx = x * pitch
        for y in range(ny + 1):
            tr = cell_exists(x, y)
            tl = cell_exists(x - 1, y)
            bl = cell_exists(x - 1, y - 1)
            br = cell_exists(x, y - 1)

            state = (tr, tl, bl, br)

            if state not in precalc_data:
                continue

            base_verts, base_faces = precalc_data[state]
            ty = y * pitch

            append_verts([(vx + tx, vy + ty, vz) for vx, vy, vz in base_verts])
            append_faces([[fv + vert_offset for fv in face] for face in base_faces])

            vert_offset += len(base_verts)

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

def get_cached_geometry(use_magnets, use_infill, stackable_baseplate):
    """
    Retrieves precalculated geometry from the cache or generates it if missing.
    Handles all Blender API interactions and disk I/O.
    """
    global _GEOMETRY_CACHE

    cache_key = (use_magnets, use_infill, stackable_baseplate)

    if cache_key not in _GEOMETRY_CACHE:
        suffix_stack = "_stackable" if stackable_baseplate else ""
        suffix_mag = "_magnet" if use_magnets else ""
        suffix_fill = "_filled" if use_infill else ""

        obj_l = load_reference_object(f"Gridfinity_baseplate_L{suffix_mag}{suffix_stack}")
        obj_t = load_reference_object(f"Gridfinity_baseplate_T{suffix_mag}{suffix_fill}{suffix_stack}")
        obj_x = load_reference_object(f"Gridfinity_baseplate_X{suffix_mag}{suffix_fill}{suffix_stack}")

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

        precalc_data = {}
        for state, (obj, rot_z) in state_lookup.items():
            rot_mat = mathutils.Matrix.Rotation(rot_z, 4, 'Z')
            base_verts = [(rot_mat @ v.co)[:] for v in obj.data.vertices]
            base_faces = [list(p.vertices) for p in obj.data.polygons]
            precalc_data[state] = (base_verts, base_faces)

        _GEOMETRY_CACHE[cache_key] = precalc_data

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

    return _GEOMETRY_CACHE[cache_key]
