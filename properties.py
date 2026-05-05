import bpy

def register():
    bpy.types.Scene.gridfinity_x = bpy.props.IntProperty(
        name="X Units",
        description="Number of units in X direction",
        default=2,
        min=1,
        max=50
    )
    bpy.types.Scene.gridfinity_y = bpy.props.IntProperty(
        name="Y Units",
        description="Number of units in Y direction",
        default=2,
        min=1,
        max=50
    )
    bpy.types.Scene.gridfinity_box_height = bpy.props.FloatProperty(
        name="Box Height mm",
        description="Total height of the box in millimeters",
        default=25.0,
        min=1.0
    )
    bpy.types.Scene.gridfinity_box_thickness = bpy.props.FloatProperty(
        name="Wall Thickness mm",
        description="Thickness of the box walls in millimeters",
        default=1.2,
        min=0.4
    )

def unregister():
    del bpy.types.Scene.gridfinity_x
    del bpy.types.Scene.gridfinity_y
    del bpy.types.Scene.gridfinity_box_height
    del bpy.types.Scene.gridfinity_box_thickness
