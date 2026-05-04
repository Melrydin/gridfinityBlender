"""
Operators for Gridfinity addon
"""

import bpy
import bmesh

class GRIDFINITY_OT_create_container(bpy.types.Operator):
    """Create a new Gridfinity container base unit with exact specifications"""
    bl_idname = "gridfinity.create_container"
    bl_label = "Create Gridfinity Container"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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

        self.report({'INFO'}, "Gridfinity container unit created with precise dimensions.")
        return {'FINISHED'}


# List of all operators
classes = [
    GRIDFINITY_OT_create_container,
]


def register():
    """Register all operator classes"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all operator classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
