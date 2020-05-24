
# Blender To Unity FBX Exporter

FBX exporter add-on for Blender compatible with Unity's coordinate system and scaling.

## How to install

1. Clone the repository or download the add-on file [`blender-to-unity-fbx-exporter.py`](/blender-to-unity-fbx-exporter.py) to your device.
2. In Blender go to Edit > Preferences > Add-ons, then use the Install… button and use the File Browser to select the add-on file.
3. Enable the add-on by checking the enable checkbox.

## How to use

File > Export > Unity FBX (.fbx)

Exports all Empty, Mesh and Armature objects in the current scene except those in disabled collections. The full hierarchy is properly preserved and exported, including local positions and rotations.

The File Browser exposes an option to export the active collection only.

## Notes

- Not yet tested with armatures nor animations.
- No option to export selected objects only. This is intentional. The nature of the fix might cause unexpected results if a child is selected without its parent.

## How it works

Every object to be exported receives a rotation of +90 degrees in the X axis _without_ actually modifying the geometry nor the visual transform of the children. This is done in the root objects first, then recursively propagated to their children (as they inhering a -90 rotation after transforming their parent). The scene is then exported to FBX using Blender's built-in FBX exported with the proper options applied. Finally everything is restored to the point prior to the modifications.

When Unity imports the FBX file the different coordinate system results in the objects including a rotation of -90 degrees applied in the X axis. As the objects in the FBX already have a rotation of X+90, then the unwanted rotation is canceled and everything gets imported correctly.

## About the author

Angel "Edy" Garcia<br>
[@VehiclePhysics](https://twitter.com/VehiclePhysics)<br>
https://vehiclephysics.com
