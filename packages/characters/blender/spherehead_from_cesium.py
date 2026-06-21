import bpy
from pathlib import Path
from mathutils import Vector


BASE_DIR = Path('/home/sohail/Github/vimmy/packages/characters')
SOURCE_GLB = BASE_DIR / 'assets' / 'base' / 'CesiumMan.glb'
OUTPUT_GLB = BASE_DIR / 'assets' / 'spherehead_fullbody.glb'

HEAD_BONE = 'Skeleton_neck_joint_2'
NECK_BONE = 'Skeleton_neck_joint_1'
TORSO_BONES = {'Skeleton_torso_joint_1', 'Skeleton_torso_joint_2', 'torso_joint_3'}
ARM_BONES = {
	'Skeleton_arm_joint_L__4_',
	'Skeleton_arm_joint_L__3_',
	'Skeleton_arm_joint_L__2_',
	'Skeleton_arm_joint_R',
	'Skeleton_arm_joint_R__2_',
	'Skeleton_arm_joint_R__3_',
}


def reset_scene():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)
	for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.textures, bpy.data.images):
		for block in list(collection):
			if block.users == 0:
				collection.remove(block)


def import_base():
	bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))
	armature = next(obj for obj in bpy.data.objects if obj.type == 'ARMATURE')
	mesh = next(obj for obj in bpy.data.objects if obj.type == 'MESH')
	helper = next((obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name == 'Icosphere'), None)
	if helper:
		bpy.data.objects.remove(helper, do_unlink=True)
	return armature, mesh


def make_material(name, color, roughness=0.86):
	mat = bpy.data.materials.new(name=name)
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes['Principled BSDF']
	bsdf.inputs['Base Color'].default_value = color
	bsdf.inputs['Roughness'].default_value = roughness
	bsdf.inputs['Specular IOR Level'].default_value = 0.28
	return mat


def set_body_material(mesh):
	mat = make_material('SphereheadBody', (0.19, 0.2, 0.24, 1.0), roughness=0.9)
	mesh.data.materials.clear()
	mesh.data.materials.append(mat)


def weight_for_group(vertex, group_index):
	for group in vertex.groups:
		if group.group == group_index:
			return group.weight
	return 0.0


def reshape_mesh(mesh):
	group_map = {group.name: group.index for group in mesh.vertex_groups}
	head_idx = group_map.get(HEAD_BONE)
	neck_idx = group_map.get(NECK_BONE)
	torso_indices = [group_map[name] for name in TORSO_BONES if name in group_map]
	arm_indices = [group_map[name] for name in ARM_BONES if name in group_map]

	head_vertices = []
	for vertex in mesh.data.vertices:
		if head_idx is not None and weight_for_group(vertex, head_idx) > 0.2:
			head_vertices.append(vertex.index)

	head_center = Vector((0.0, 0.0, 1.28))
	if head_vertices:
		head_center = sum((mesh.data.vertices[i].co.copy() for i in head_vertices), Vector()) / len(head_vertices)

	for vertex in mesh.data.vertices:
		co = vertex.co.copy()
		head_weight = weight_for_group(vertex, head_idx) if head_idx is not None else 0.0
		neck_weight = weight_for_group(vertex, neck_idx) if neck_idx is not None else 0.0
		torso_weight = max((weight_for_group(vertex, idx) for idx in torso_indices), default=0.0)
		arm_weight = max((weight_for_group(vertex, idx) for idx in arm_indices), default=0.0)

		if head_weight > 0.2:
			# Collapse the original head into the neck area before adding the stylized sphere.
			vertex.co = head_center + (co - head_center) * 0.08
			vertex.co.z -= 0.03
			continue

		if neck_weight > 0.2:
			vertex.co = head_center + (co - head_center) * 0.72
			continue

		if torso_weight > 0.18:
			vertex.co.x *= 1.16
			vertex.co.y *= 1.1

		if arm_weight > 0.15:
			vertex.co.x *= 1.08
			vertex.co.y *= 1.05

		if 0.35 < co.z < 1.05:
			vertex.co.x *= 1.03


def pose_character(armature):
	bpy.context.view_layer.objects.active = armature
	bpy.ops.object.mode_set(mode='POSE')
	rotations = {
		'Skeleton_arm_joint_L__4_': (0.0, 0.0, -1.05),
		'Skeleton_arm_joint_L__3_': (0.0, 0.0, -0.15),
		'Skeleton_arm_joint_R': (0.0, 0.0, 1.05),
		'Skeleton_arm_joint_R__2_': (0.0, 0.0, 0.15),
	}
	for bone_name, rot in rotations.items():
		bone = armature.pose.bones.get(bone_name)
		if bone:
			bone.rotation_mode = 'XYZ'
			bone.rotation_euler = rot
	bpy.ops.object.mode_set(mode='OBJECT')


def create_sphere_head(armature):
	bone = armature.pose.bones[HEAD_BONE]
	head = armature.matrix_world @ bone.head
	tail = armature.matrix_world @ bone.tail
	body_height = 1.5
	radius = body_height * 0.22
	center = head.lerp(tail, 0.55) + Vector((0.0, 0.0, radius * 0.45))

	bpy.ops.mesh.primitive_uv_sphere_add(segments=56, ring_count=28, radius=radius, location=center)
	sphere = bpy.context.active_object
	sphere.name = 'SphereheadOrb'
	sphere.scale[1] = 1.02
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	bpy.ops.object.shade_smooth()

	dark = make_material('SphereheadDark', (0.34, 0.35, 0.42, 1.0), roughness=0.96)
	light = make_material('SphereheadLight', (0.93, 0.93, 0.91, 1.0), roughness=0.99)
	sphere.data.materials.clear()
	sphere.data.materials.append(dark)
	sphere.data.materials.append(light)

	for poly in sphere.data.polygons:
		z_avg = sum(sphere.data.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
		poly.material_index = 1 if z_avg > center.z + radius * 0.34 else 0

	mod = sphere.modifiers.new(name='Armature', type='ARMATURE')
	mod.object = armature
	group = sphere.vertex_groups.new(name=HEAD_BONE)
	group.add([vertex.index for vertex in sphere.data.vertices], 1.0, 'ADD')
	sphere.parent = armature
	return sphere


def place_on_ground(objects):
	min_z = None
	for obj in objects:
		if obj.type != 'MESH':
			continue
		for vertex in obj.data.vertices:
			world = obj.matrix_world @ vertex.co
			min_z = world.z if min_z is None else min(min_z, world.z)
	if min_z is None:
		return
	for obj in objects:
		obj.location.z -= min_z


def export_glb(objects):
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select_set(True)
	bpy.context.view_layer.objects.active = objects[0]
	bpy.ops.export_scene.gltf(
		filepath=str(OUTPUT_GLB),
		use_selection=True,
		export_format='GLB',
		export_apply=False,
		export_animations=False,
		export_yup=True,
	)


def main():
	reset_scene()
	armature, mesh = import_base()
	set_body_material(mesh)
	reshape_mesh(mesh)
	pose_character(armature)
	sphere = create_sphere_head(armature)
	place_on_ground([armature, mesh, sphere])
	export_glb([armature, mesh, sphere])


if __name__ == '__main__':
	main()
