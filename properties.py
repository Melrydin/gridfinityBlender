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
    bpy.types.Scene.gridfinity_bin_height = bpy.props.FloatProperty(
        name="Bin Height mm",
        description="Total height of the bin in millimeters",
        default=25.0,
        min=1.0
    )
    bpy.types.Scene.gridfinity_bin_wall_thickness = bpy.props.FloatProperty(
        name="Wall Thickness mm",
        description="Thickness of the bin walls in millimeters",
        default=1.2,
        min=0.4,
        max=2.5
    )
    bpy.types.Scene.gridfinity_drawer_x = bpy.props.FloatProperty(
        name="Drawer X mm",
        description="Maximum X dimension of the drawer",
        default=250.0,
        min=42.0
    )
    bpy.types.Scene.gridfinity_drawer_y = bpy.props.FloatProperty(
        name="Drawer Y mm",
        description="Maximum Y dimension of the drawer",
        default=250.0,
        min=42.0
    )
    bpy.types.Scene.gridfinity_export_path = bpy.props.StringProperty(
        name="Export Path",
        description="Directory to export the STL files",
        subtype='DIR_PATH',
        default="//"
    )
    bpy.types.Scene.gridfinity_use_magnets = bpy.props.BoolProperty(
        name="Include Magnets",
        description="Add magnetic baseplates to the bottom",
        default=False
    )
    bpy.types.Scene.gridfinity_use_infill = bpy.props.BoolProperty(
        name="Solid Infill",
        description="Use filled baseplates (flat T and filled X)",
        default=False
    )


def unregister():
    del bpy.types.Scene.gridfinity_x
    del bpy.types.Scene.gridfinity_y
    del bpy.types.Scene.gridfinity_bin_height
    del bpy.types.Scene.gridfinity_bin_wall_thickness
    del bpy.types.Scene.gridfinity_drawer_x
    del bpy.types.Scene.gridfinity_drawer_y
    del bpy.types.Scene.gridfinity_use_magnets
    del bpy.types.Scene.gridfinity_use_infill
