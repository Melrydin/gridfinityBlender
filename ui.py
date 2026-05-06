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

        box_unit = layout.box()
        box_unit.label(text="Standard Units", icon='OBJECT_DATAMODE')
        row = box_unit.row()
        row.prop(scene, "gridfinity_x", text="Width X")
        row.prop(scene, "gridfinity_y", text="Depth Y")

        layout.separator()

        box_ui = layout.box()
        box_ui.label(text="Complete Gridfinity", icon='PACKAGE')
        box_ui.prop(scene, "gridfinity_box_height", text="Height mm")
        box_ui.prop(scene, "gridfinity_box_thickness", text="Thickness mm")
        box_ui.operator("gridfinity.create_container_with_box", text="Base + Hollow Box", icon='PACKAGE')
        box_ui.operator("gridfinity.create_container_with_solid_box", text="Base + Solid Box", icon='CUBE')

        layout.separator()

        box_comp = layout.box()
        box_comp.label(text="Standalone Components", icon='MESH_DATA')
        box_comp.operator("gridfinity.create_container", text="Baseplate Only", icon='MESH_GRID')
        box_comp.operator("gridfinity.create_box", text="Hollow Box Only", icon='MESH_CUBE')
        box_comp.operator("gridfinity.create_solid_box", text="Solid Box Only", icon='CUBE')
        box_comp.operator("gridfinity.create_basegrid", text="Stacking Lip", icon='MOD_EDGESPLIT')

def register():
    bpy.utils.register_class(VIEW3D_PT_gridfinity_panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_gridfinity_panel)
