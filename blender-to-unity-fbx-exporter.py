bl_info = {
	"name": "Unity FBX format",
	"author": "Angel ""Edy"" Garcia (@VehiclePhysics)",
	"version": (1, 2),
	"blender": (2, 80, 0),
	"location": "File > Export > Unity FBX",
	"description": "FBX exporter compatible with Unity's coordinate and scaling system.",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export",
}


import bpy
import mathutils
import math


# Multi-user mesh data is preserved here. Unique copies are made for applying the rotation.
# Eventually multi-user meshes become single-user and gets processed.
# Therefore restoring the multi-user data assigns a shared but already processed mesh.
mesh_data = dict()

# All objects and collections in this view layer must be visible while being processed.
# apply_rotation and matrix changes don't have effect otherwise.
# Visibility will be restored right before saving the FBX.
hidden_collections = []
hidden_objects = []
disabled_collections = []
disabled_objects = []


def unhide_collections(col):
	global hidden_collections
	global disabled_collections

	# No need to unhide excluded collections. Their objects aren't included in current view layer.
	if col.exclude:
		return

	# Find hidden child collections and unhide them
	hidden = [item for item in col.children if not item.exclude and item.hide_viewport]
	for item in hidden:
		item.hide_viewport = False

	# Add them to the list so they could be restored later
	hidden_collections.extend(hidden)

	# Same with the disabled collections
	disabled = [item for item in col.children if not item.exclude and item.collection.hide_viewport]
	for item in disabled:
		item.collection.hide_viewport = False

	disabled_collections.extend(disabled)

	# Recursively unhide child collections
	for item in col.children:
		unhide_collections(item)


def unhide_objects():
	global hidden_objects
	global disabled_objects

	view_layer_objects = [ob for ob in bpy.data.objects if ob.name in bpy.context.view_layer.objects]

	for ob in view_layer_objects:
		if ob.hide_get():
			hidden_objects.append(ob)
			ob.hide_set(False)
		if ob.hide_viewport:
			disabled_objects.append(ob)
			ob.hide_viewport = False


def reset_parent_inverse(ob):
	if (ob.parent):
		mat_world = ob.matrix_world.copy()
		ob.matrix_parent_inverse.identity()
		ob.matrix_basis = ob.parent.matrix_world.inverted() @ mat_world


def apply_rotation(ob):
	global mesh_data

	# Create a single copy in multi-user meshes. Will be restored later.
	if (ob.type == "MESH" and ob.data.users > 1):
		mesh_data[ob.name] = ob.data
		ob.data = ob.data.copy()

	# Apply rotation
	bpy.ops.object.select_all(action='DESELECT')
	ob.select_set(True)
	bpy.ops.object.transform_apply(rotation = True)


def fix_object(ob):
	# Only fix objects in current view layer
	if ob.name in bpy.context.view_layer.objects:

		# Reset parent's inverse so we can work with local transform directly
		reset_parent_inverse(ob)

		# Create a copy of the local matrix and set a pure X-90 matrix
		mat_original = ob.matrix_local.copy()
		ob.matrix_local = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

		# Apply the rotation to the object
		apply_rotation(ob)

		# Reapply the previous local transform with an X+90 rotation
		ob.matrix_local = mat_original @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

	# Recursively fix child objects in current view layer.
	# Children may be in the current view layer even if their parent isn't.
	for child in ob.children:
		fix_object(child)


def export_unity_fbx(context, filepath, active_collection, selected_objects):
	global mesh_data
	global hidden_collections
	global hidden_objects
	global disabled_collections
	global disabled_objects

	print("Preparing 3D model for Unity...")

	# Root objects: Empty or Mesh without parent
	root_objects = [item for item in bpy.data.objects if (item.type == "EMPTY" or item.type == "MESH") and not item.parent]

	# Preserve current scene
	bpy.ops.ed.undo_push()
	mesh_data = dict()
	hidden_collections = []
	hidden_objects = []
	disabled_collections = []
	disabled_objects = []
	
	selection = bpy.context.selected_objects

	# Ensure all the collections and objects in this view layer are visible
	unhide_collections(bpy.context.view_layer.layer_collection)
	unhide_objects()

	try:
		# Fix rotations
		for ob in root_objects:
			print(ob.name)
			fix_object(ob)

		# Restore multi-user meshes
		for item in mesh_data:
			bpy.data.objects[item].data = mesh_data[item]

		# Recompute the transforms out of the changed matrices
		bpy.context.view_layer.update()

		# Restore hidden and disabled objects
		for ob in hidden_objects:
			ob.hide_set(True)
		for ob in disabled_objects:
			ob.hide_viewport = True

		# Restore hidden and disabled collections
		for col in hidden_collections:
			col.hide_viewport = True
		for col in disabled_collections:
			col.collection.hide_viewport = True

		# Restore selection
		bpy.ops.object.select_all(action='DESELECT')
		for ob in selection:
			ob.select_set(True)
		
		# Export FBX file
		bpy.ops.export_scene.fbx(filepath=filepath, apply_scale_options='FBX_SCALE_UNITS', object_types={'EMPTY', 'MESH', 'ARMATURE'}, use_active_collection=active_collection, use_selection=selected_objects)

	except Exception as e:
		bpy.ops.ed.undo()
		print(e)
		print("File not saved.")
		return {'CANCELLED'}

	# Restore scene and finish
	bpy.ops.ed.undo()
	print("FBX file for Unity saved.")
	return {'FINISHED'}


#---------------------------------------------------------------------------------------------------
# Exporter stuff (from the Operator File Export template)

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportUnityFbx(Operator, ExportHelper):
	"""FBX exporter compatible with Unity's coordinate and scaling system"""
	bl_idname = "export_scene.unity_fbx"
	bl_label = "Export Unity FBX"

	# ExportHelper mixin class uses this
	filename_ext = ".fbx"

	filter_glob: StringProperty(
		default="*.fbx",
		options={'HIDDEN'},
		maxlen=255,  # Max internal buffer length, longer would be clamped.
	)

	# List of operator properties, the attributes will be assigned
	# to the class instance from the operator settings before calling.

	active_collection: BoolProperty(
		name="Active Collection Only",
		description="Export only objects from the active collection (and its children)",
		default=False,
	)
	
	selected_objects: BoolProperty(
		name="Selected Objects Only",
		description="Export only selected objects. Only from current collection if the other option is also checked.",
		default=False,
	)	

	def execute(self, context):
		return export_unity_fbx(context, self.filepath, self.active_collection, self.selected_objects)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
	self.layout.operator(ExportUnityFbx.bl_idname, text="Unity FBX (.fbx)")


def register():
	bpy.utils.register_class(ExportUnityFbx)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ExportUnityFbx)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()

	# test call
	bpy.ops.export_scene.unity_fbx('INVOKE_DEFAULT')
