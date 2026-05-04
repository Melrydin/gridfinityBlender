import bpy

class VIEW3D_PT_gridfinity_panel(bpy.types.Panel):
    bl_label = "Gridfinity Generator"
    bl_idname = "VIEW3D_PT_gridfinity"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gridfinity'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="Dimensions Units", icon='OBJECT_DATAMODE')
        row = box.row()
        row.prop(scene, "gridfinity_x", text="Width X")
        row.prop(scene, "gridfinity_y", text="Depth Y")

        layout.separator()
        layout.operator("gridfinity.create_container", text="Generate Baseplate", icon='MESH_GRID')

def register():
    bpy.utils.register_class(VIEW3D_PT_gridfinity_panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_gridfinity_panel)
