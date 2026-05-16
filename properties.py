import bpy

class GridfinityProperties(bpy.types.PropertyGroup):
    x: bpy.props.IntProperty(
        name="X Units",
        description="Number of units in X direction",
        default=2,
        min=1,
        max=50
    )
    y: bpy.props.IntProperty(
        name="Y Units",
        description="Number of units in Y direction",
        default=2,
        min=1,
        max=50
    )
    bin_height: bpy.props.FloatProperty(
        name="Bin Height mm",
        description="Total height of the bin in millimeters",
        default=25.0,
        min=1.0
    )
    bin_wall_thickness: bpy.props.FloatProperty(
        name="Wall Thickness mm",
        description="Thickness of the bin walls in millimeters",
        default=1.2,
        min=0.4,
        max=2.5
    )
    drawer_x: bpy.props.FloatProperty(
        name="Drawer X mm",
        description="Maximum X dimension of the drawer",
        default=250.0,
        min=42.0
    )
    drawer_y: bpy.props.FloatProperty(
        name="Drawer Y mm",
        description="Maximum Y dimension of the drawer",
        default=250.0,
        min=42.0
    )
    export_path: bpy.props.StringProperty(
        name="Export Path",
        description="Directory to export the STL files",
        subtype='DIR_PATH',
        default="//"
    )
    use_magnets: bpy.props.BoolProperty(
        name="Include Magnets",
        description="Add magnetic baseplates to the bottom",
        default=False
    )
    use_infill: bpy.props.BoolProperty(
        name="Solid Infill",
        description="Use filled baseplates (flat T and filled X)",
        default=False
    )
    lid_thickness: bpy.props.FloatProperty(
        name="Lid Thickness",
        default=2.0
    )
    lid_tolerance: bpy.props.FloatProperty(
        name="Fit Tolerance",
        default=0.15
    )
    lid_add_profile: bpy.props.BoolProperty(
    name="Add Stacking Profile",
    description="Add a top profile for stacking bins on the lid",
    default=False
    )
    bin_add_profile: bpy.props.BoolProperty(
    name="Add Stacking Profile",
    description="Add the top profile for stacking bins",
    default=False
    )
    use_official_height: bpy.props.BoolProperty(
    name="Use Official Units",
    description="Use official Gridfinity Z units instead of absolute millimeters",
    default=True
    )
    gridfinity_z: bpy.props.IntProperty(
        name="Gridfinity Z Units",
        description="Height in 7mm Gridfinity standard units",
        default=6,
        min=1
    )
    stackable_baseplate: bpy.props.BoolProperty(
    name="Stackable Baseplate",
    description="Generates the standard Gridfinity profile on the underside",
    default=False
    )
    bin_add_label_tab: bpy.props.BoolProperty(
        name="Add Label Tab",
        description="Add an angled inner tab for adhesive labels",
        default=False
    )
    label_text: bpy.props.StringProperty(
        name="Label Text",
        description="Text to engrave or emboss on the tab",
        default=""
    )
    label_style: bpy.props.EnumProperty(
        name="Label Style",
        description="Choose between raised or engraved text",
        items=[
            ('EMBOSSED', "Embossed", "Raised text"),
            ('DEBOSSED', "Debossed", "Engraved text")
        ],
        default='DEBOSSED'
    )

def register():
    bpy.utils.register_class(GridfinityProperties)
    bpy.types.Scene.gridfinity = bpy.props.PointerProperty(type=GridfinityProperties)

def unregister():
    del bpy.types.Scene.gridfinity
    bpy.utils.unregister_class(GridfinityProperties)
