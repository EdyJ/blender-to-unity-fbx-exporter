
# Blender To Unity FBX Exporter

FBX exporter add-on for Blender 2.80+ compatible with Unity's coordinate and scaling system.

## How to install

1. Clone the repository or download the add-on file [`blender-to-unity-fbx-exporter.py`](/blender-to-unity-fbx-exporter.py) to your device.
2. In Blender go to Edit > Preferences > Add-ons, then use the Install… button and use the File Browser to select the add-on file.
3. Enable the add-on by checking the enable checkbox.

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-addon.png" alt="Blender To Unity FBX Exporter Add-On">
</p>

## How to use

**File > Export > Unity FBX (.fbx)**

Exports all Empty, Mesh and Armature objects in the current scene except those in disabled collections. The full hierarchy is properly preserved and exported, including local positions and rotations.

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-menu.png" alt="Blender To Unity FBX Exporter Menu">
</p>

The File Browser exposes an option to export the active collection only.

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-options.png" alt="Blender To Unity FBX Exporter Options">
</p>

## Notes

- Not tested with armatures nor animations.
- No option to export selected objects only. This is intentional. The nature of the fix for Unity might cause unexpected results if a child object is selected without its parent. Use Collections for defining the objects to be exported.

## How it works

In Blender every object to be exported receives a rotation of +90 degrees around the X axis in their transform _without_ actually modifying the visual pose of its geometry and children. This is done in the root objects first, then recursively propagated to their children (as they inhering a -90 rotation after transforming their parent). The scene is then exported to FBX using Blender's built-in FBX exported with the proper options applied. Finally the scene is restored to the point prior to applying the modifications.

When Unity imports the FBX file the different coordinate system results in the objects including a rotation of -90 degrees applied in the X axis. As the objects in the FBX already have a rotation of X+90, then the unwanted rotation is canceled and everything gets imported correctly.

## About the author

Angel "Edy" Garcia<br>
[@VehiclePhysics](https://twitter.com/VehiclePhysics)<br>
https://vehiclephysics.com
