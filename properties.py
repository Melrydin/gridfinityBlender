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

def unregister():
    del bpy.types.Scene.gridfinity_x
    del bpy.types.Scene.gridfinity_y
