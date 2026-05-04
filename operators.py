import bpy
import bmesh

class GRIDFINITY_OT_create_container(bpy.types.Operator):
    """Create a new Gridfinity container base unit with exact specifications"""
    bl_idname = "gridfinity.create_container"
    bl_label = "Create Gridfinity Container"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y

        mesh = bpy.data.meshes.new("Gridfinity_Unit_Mesh")
        obj = bpy.data.objects.new("Gridfinity_Unit", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)

        bmesh.ops.scale(bm, vec=(0.042, 0.042, 0.00225), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.005875), verts=bm.verts)

        vertical_edges = []
        for edge in bm.edges:
            z_difference = abs(edge.verts[0].co.z - edge.verts[1].co.z)
            if z_difference > 0.001:
                vertical_edges.append(edge)

        bmesh.ops.bevel(
            bm,
            geom=vertical_edges,
            offset=0.0038,
            segments=16,
            profile=0.5,
            affect='EDGES'
        )

        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        bottom_face = None
        for face in bm.faces:
            is_bottom = True
            for vert in face.verts:
                if abs(vert.co.z - 0.00475) > 0.0001:
                    is_bottom = False
                    break
            if is_bottom:
                bottom_face = face
                break

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

        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (0.042, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, 0.042, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

        self.report({'INFO'}, "Gridfinity container unit created with precise dimensions.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_container)

def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_container)
