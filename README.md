# Gridfinity Generator for Blender

<div align="center">

A powerful Blender addon for procedurally generating precise, modular, and customizable Gridfinity storage components with advanced geometry merging and boolean operations for exact drawer fitting.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Releases](https://github.com/clemens/gridfinityBlender/releases) • [License](#license)

</div>

## Overview

This addon streamlines the creation of professional-grade Gridfinity storage components directly within Blender. Whether you're designing custom organizers, fitting components into existing drawers, or batch-exporting for 3D printing, this tool provides precise control and automated workflows.

**Key Capabilities:**
- 🎨 Procedural component generation with real-time parameter adjustments
- 📏 Millimeter-precise dimensions for perfect drawer fits
- 🔄 Smart boolean operations for seamless geometry merging
- 📦 Batch STL export with intelligent grouping
- 🔌 Full compatibility with Blender 4.1+ and legacy versions

## Origin and Source

The Gridfinity organizational system was invented by Zack Freedman. Discover more about the system and find additional designs on his [Thangs profile](https://thangs.com/designer/ZackFreedman).

## Features

### 🎯 Configuration & Customization

#### Dimension Settings
- **Grid Size:** Define the exact number of 42mm base units in X and Y directions
- **Height Units:** Choose between official 7mm Gridfinity units or custom millimeter values
- **Bin Parameters:** Customize total bin height and wall thickness (in millimeters)
- **Drawer Constraints:** Specify maximum drawer dimensions for precise fitting
- **Real-time Preview:** Adjust parameters and see changes instantly

### 🏗️ Gridfinity Components

#### Complete Generation Modes
- **Baseplate + Hollow Bin:** Unified object with standard baseplate and hollow storage bin
- **Baseplate + Solid Bin:** Unified object with baseplate and solid block (includes stacking rim)
- **Optional Stacking Profiles:** Add standardized stacking profiles to bins and lids for seamless component stacking
- **Optional Label Tabs:** Angled inner tabs on bin front walls for adhesive label placement
- **Stackable Baseplates:** Generate Gridfinity-profile underside for stacking multiple grids

#### Drawer Fit Mode
The intelligent fitting system automatically:
- Calculates maximum integer grid units fitting within drawer constraints
- Generates perfectly aligned baseplates
- Uses precise boolean intersection to cut edges to exact millimeter limits
- Preserves unit integrity and origin points

#### Lid Generation
- **Fitted Lid Creator:** Generate precision-fit lids with inner alignment plugs for secure seating
- **Lid Stacking Profiles:** Optional profiles on lid tops for stacking bins on top of closed containers
- **Adjustable Tolerance:** Fine-tune fit tolerance for different printer calibrations
- **Customizable Thickness:** Set lid thickness to match your design requirements

#### Standalone Components
- **Baseplate Only:** Single flat array at standard 4.75mm height
- **Stacking Lip Array:** Procedurally generated stacking profiles with optimized topology
- **Hollow Bin Only:** Raw bin walls and inner bottom bevel (baseplate-free)
- **Solid Bin Only:** Solid block with stacking rim (baseplate-free)

### 📤 Export Utilities

#### Intelligent Batch Export
- **One-Click STL Export:** Export all generated objects simultaneously
- **Smart Grouping:** Automatically merges overlapping components based on geometric centers
- **Auto Naming:** Descriptive filenames generated without manual input
- **API Compatibility:** Seamlessly switches between native C++ (Blender 4.1+) and legacy Python exporters

## Installation

### Method 1: From GitHub (Recommended)
1. Download the latest release as a `.zip` file from the [Releases page](https://github.com/clemens/gridfinityBlender/releases)
2. In Blender, navigate to **Edit → Preferences → Add-ons**
3. Click **Install** and select the downloaded ZIP file
4. Search for "Gridfinity" and enable the addon by checking the box
5. The Gridfinity panel will appear in the 3D Viewport sidebar

### Method 2: From Source
1. Clone the repository or download as ZIP
2. Extract to your Blender addons folder:
   - **Windows:** `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons`
   - **macOS:** `~/Library/Application Support/Blender/<version>/scripts/addons`
   - **Linux:** `~/.config/blender/<version>/scripts/addons`
3. Restart Blender and enable the addon in Preferences

## Usage

### Getting Started

1. **Open the Panel**
   - Open the 3D Viewport in Blender
   - Press `N` to toggle the sidebar
   - Navigate to the **Gridfinity** tab

2. **Set Your Dimensions**
   - Enter **Grid Size** (number of 42mm units in X and Y)
   - Customize **Bin Height** and **Wall Thickness** (millimeters)
   - Optionally set **Drawer Constraints** for fitted generation

3. **Generate Components**
   - Select your desired generation mode
   - Click the corresponding button
   - Generated objects appear in the viewport

### Workflow Examples

#### Generating a Stackable Grid System
1. Create your base grid (e.g., 4×3 with official 6 Z-units height)
2. Enable **Stackable Baseplate** for stacking capability
3. Create a second grid layer above the first
4. Both grids will nest perfectly when printed
5. Export all components and stack after printing

#### Creating Bins with Labels
1. Set grid dimensions and customize height
2. Enable **Add Label Tab** option for front wall tabs
3. Generate your bins
4. After printing, apply adhesive labels to the angled tabs
5. Labels won't interfere with insertion/removal

#### Creating Fitted Lids
1. Set dimensions matching your bin grid (e.g., 4×3)
2. Adjust **Lid Thickness** and **Tolerance** as needed
3. Optional: Enable **Add Stacking Profile** to stack bins on closed lids
4. Click **Create Fitted Lid**
5. Test fit and export

#### Creating a Fitted Drawer Organizer
1. Measure your drawer: 300mm × 200mm × 80mm
2. Set **Drawer Constraints** to these dimensions
3. Click **Generate Fitted Grid**
4. Adjust fine details if needed
5. Export to STL with a single click

#### Batch Exporting Multiple Components
1. Generate several different Gridfinity components in your scene
2. Navigate to **Export Utilities**
3. Click **Batch Export STL**
4. Select export directory
5. All components are automatically named and grouped

## Advanced Features

### Stacking System
- **Multi-Level Organization:** Create vertically stacked storage configurations
- **Stacking Profiles:** Both bins and lids support optional Gridfinity-standard stacking profiles
- **Stackable Baseplates:** Underside profiles allow grids to stack on top of each other
- **Perfect Alignment:** Automatic positioning ensures clean, stable stacking

### Labeling System
- **Built-in Label Tabs:** Optional angled inner tabs for adhesive label placement
- **Front Wall Tabs:** Angled geometry prevents label edges from catching

### Magnet Baseplate Support
Full support for magnetic baseplate configurations enables compatible components with magnetic organizing systems.

### Geometry Optimization
- Automatic vertex merging for clean topology
- Internal wall removal for 3D printing efficiency
- Precise beveling on outer corners for manifold meshes
- Corrected normal extrusion for reliable boolean operations

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Addon not appearing after install | Restart Blender completely |
| Export produces invalid STL | Ensure Blender 4.1+ or check Python exporter compatibility |
| Generated geometry looks corrupted | Reset parameters to defaults and regenerate |
| Boolean operations fail | Increase wall thickness or check for overlapping geometry |

## License

This addon is provided under the terms specified in the [LICENSE](LICENSE) file.

## Support & Contributions

- **Report Issues:** Please use the [GitHub Issues](https://github.com/clemens/gridfinityBlender/issues) page
- **Feature Requests:** Share your ideas through GitHub Issues
- **Contributions:** Pull requests are welcome!

---

**Created by:** Clemens, Melrydin
**Last Updated:** May 15, 2026
**Blender Compatibility:** 4.5+ (LTS and Latest)
**Current Development Version:** 0.3.0-dev
