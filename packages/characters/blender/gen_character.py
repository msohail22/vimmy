import bpy
import math
import os
import re

OUTPUT_DIR = os.path.expanduser('/home/sohail/Github/vimmy/packages/characters/preview')
RENDER_PATH = os.path.join(OUTPUT_DIR, 'character_render.png')
GLB_PATH = os.path.expanduser('/home/sohail/Github/vimmy/packages/characters/assets/spherehead_back.glb')

TORSO_HEIGHT = 2.8


def clear_scene():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)


def force_srgb_name():
	for mat in bpy.data.materials:
		if mat.node_tree:
			for node in mat.node_tree.nodes:
				if hasattr(node, 'name'):
					m = re.match(r'^SN:\s*(.+)$', node.name)
					if m:
						mat.name = m.group(1)


def torso_rx(z):
	if z < 0.3:   return 0.40 + 0.10 * (z / 0.3)
	if z < 0.8:   return 0.50 + 0.15 * ((z - 0.3) / 0.5)
	if z < 1.5:   return 0.65 + 0.10 * ((z - 0.8) / 0.7)
	if z < 2.1:   return 0.75 + 0.20 * ((z - 1.5) / 0.6)
	if z < 2.5:   return 0.95 - 0.25 * ((z - 2.1) / 0.4)
	return 0.35 - 0.10 * ((z - 2.5) / 0.3)


def torso_ry_back(z):
	if z < 0.3:   return 0.18 + 0.04 * (z / 0.3)
	if z < 1.0:   return 0.22 + 0.08 * ((z - 0.3) / 0.7)
	if z < 1.8:   return 0.30 + 0.06 * ((z - 1.0) / 0.8)
	if z < 2.3:   return 0.36 - 0.06 * ((z - 1.8) / 0.5)
	return 0.18 - 0.05 * ((z - 2.3) / 0.5)


def torso_ry_front(z):
	if z < 0.3:   return 0.18 + 0.04 * (z / 0.3)
	if z < 1.0:   return 0.22 + 0.08 * ((z - 0.3) / 0.7)
	if z < 1.8:   return 0.30 + 0.04 * ((z - 1.0) / 0.8)
	if z < 2.3:   return 0.32 - 0.10 * ((z - 1.8) / 0.5)
	return 0.18 - 0.05 * ((z - 2.3) / 0.5)


def back_muscle_delta(x, y, z):
	dx = dy = 0.0

	# Trapezius — diamond at upper back
	if 1.6 < z < 2.4 and abs(x) < 0.38:
		zf = 1 - ((z - 2.0) / 0.4) ** 2
		xf = 1 - (x / 0.38) ** 2
		if zf > 0 and xf > 0:
			dy += 0.09 * zf * xf

	# Trapezius lateral wings
	for xc in (-0.25, 0.25):
		if 1.55 < z < 2.15 and abs(x - xc) < 0.25:
			zf = 1 - ((z - 1.85) / 0.3) ** 2
			xf = 1 - ((x - xc) / 0.25) ** 2
			if zf > 0 and xf > 0:
				dy += 0.05 * zf * xf
				dx += 0.02 * math.copysign(1, x) * zf * xf

	# Latissimus dorsi — sides of mid back
	for xc in (-0.48, 0.48):
		if 0.6 < z < 1.6 and abs(x - xc) < 0.28:
			zf = 1 - ((z - 1.1) / 0.5) ** 2
			xf = 1 - ((x - xc) / 0.28) ** 2
			if zf > 0 and xf > 0:
				dy += 0.07 * zf * xf
				dx += 0.04 * math.copysign(1, x) * zf * xf

	# Spinal erectors
	for xc in (-0.10, 0.10):
		if 0.4 < z < 1.9 and abs(x - xc) < 0.08:
			zf = 1 - ((z - 1.15) / 0.75) ** 2
			xf = 1 - ((x - xc) / 0.08) ** 2
			if zf > 0 and xf > 0:
				dy += 0.04 * zf * xf

	# Spine groove
	if 0.4 < z < 1.9 and abs(x) < 0.06:
		zf = 1 - ((z - 1.15) / 0.75) ** 2
		xf = 1 - (x / 0.06) ** 2
		if zf > 0 and xf > 0:
			dy -= 0.035 * zf * xf

	# Deltoids
	for xc in (-0.72, 0.72):
		if 1.8 < z < 2.3 and abs(x - xc) < 0.2:
			zf = 1 - ((z - 2.05) / 0.25) ** 2
			xf = 1 - ((x - xc) / 0.2) ** 2
			if zf > 0 and xf > 0:
				dy += 0.04 * zf * xf * 0.5
				dx += 0.03 * math.copysign(1, x) * zf * xf

	return dx, dy


def close_polygon_loop(verts, z, rx, ry_back, ry_front, n):
	row = []
	for j in range(n):
		theta = 2 * math.pi * j / n
		ct = math.cos(theta)
		st = math.sin(theta)
		xb = rx * ct
		yb = ry_back * st if st >= 0 else ry_front * st
		if st > 0:
			dx, dy = back_muscle_delta(xb, yb, z)
		else:
			dx = dy = 0.0
		row.append((xb + dx, yb + dy, z))
	return row


def build_torso():
	n_rings = 48
	n_per = 64
	verts = []
	faces = []

	for i in range(n_rings):
		z = (TORSO_HEIGHT * i) / (n_rings - 1)
		rx = torso_rx(z)
		ryb = torso_ry_back(z)
		ryf = torso_ry_front(z)
		row = close_polygon_loop(verts, z, rx, ryb, ryf, n_per)
		verts.extend(row)

	for i in range(n_rings - 1):
		for j in range(n_per):
			a = i * n_per + j
			b = i * n_per + (j + 1) % n_per
			c = (i + 1) * n_per + (j + 1) % n_per
			d = (i + 1) * n_per + j
			faces.append((a, b, c, d))

	mesh = bpy.data.meshes.new('TorsoMesh')
	mesh.from_pydata(verts, [], faces)
	mesh.update()
	obj = bpy.data.objects.new('Torso', mesh)
	bpy.context.collection.objects.link(obj)
	return obj


def build_arm(side):
	"""side: -1 (left) or +1 (right). Arm hangs down, only upper half visible."""
	n_per = 24
	n_len = 12
	verts = []
	faces = []
	arm_len = 0.9

	for i in range(n_len):
		t = i / (n_len - 1)
		z = 1.45 - t * arm_len
		r = 0.13 - t * 0.04
		x0 = side * 0.78
		for j in range(n_per):
			theta = 2 * math.pi * j / n_per
			x = x0 + r * math.cos(theta)
			y = r * math.sin(theta) * 0.85
			verts.append((x, y, z))

	for i in range(n_len - 1):
		for j in range(n_per):
			a = i * n_per + j
			b = i * n_per + (j + 1) % n_per
			c = (i + 1) * n_per + (j + 1) % n_per
			d = (i + 1) * n_per + j
			faces.append((a, b, c, d))

	mesh = bpy.data.meshes.new(f'Arm{"L" if side < 0 else "R"}Mesh')
	mesh.from_pydata(verts, [], faces)
	mesh.update()
	obj = bpy.data.objects.new(f'Arm{"L" if side < 0 else "R"}', mesh)
	bpy.context.collection.objects.link(obj)
	return obj


def build_neck():
	bpy.ops.mesh.primitive_cylinder_add(
		vertices=24, radius=0.16, depth=0.45, location=(0, 0, TORSO_HEIGHT + 0.225)
	)
	obj = bpy.context.active_object
	obj.name = 'Neck'
	return obj


def build_sphere_head():
	bpy.ops.mesh.primitive_uv_sphere_add(
		segments=64, ring_count=64, radius=0.72, location=(0, 0, TORSO_HEIGHT + 0.65)
	)
	obj = bpy.context.active_object
	obj.name = 'SphereHead'
	bpy.ops.object.shade_smooth()
	return obj


def join_meshes(objects, name):
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select_set(True)
	bpy.context.view_layer.objects.active = objects[0]
	bpy.ops.object.join()
	joined = bpy.context.active_object
	joined.name = name
	return joined


def add_subdiv(obj, levels=2):
	mod = obj.modifiers.new(name='Subdiv', type='SUBSURF')
	mod.levels = levels
	mod.render_levels = levels
	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.modifier_apply(modifier=mod.name)


def make_skin_material():
	mat = bpy.data.materials.new(name='SkinMat')
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	nodes.clear()

	output = nodes.new('ShaderNodeOutputMaterial')
	diffuse = nodes.new('ShaderNodeBsdfDiffuse')
	diffuse.inputs['Color'].default_value = (0.92, 0.90, 0.85, 1.0)
	diffuse.inputs['Roughness'].default_value = 0.85
	links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

	# Freestyle color is controlled by line style, not material
	return mat


def make_sphere_material():
	mat = bpy.data.materials.new(name='SphereMat')
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	nodes.clear()

	output = nodes.new('ShaderNodeOutputMaterial')
	diffuse = nodes.new('ShaderNodeBsdfDiffuse')
	diffuse.inputs['Color'].default_value = (0.88, 0.86, 0.82, 1.0)
	diffuse.inputs['Roughness'].default_value = 0.75
	links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

	# Radial scratch texture as bump — uses angle from center to create bands
	tex_coord = nodes.new('ShaderNodeTexCoord')
	separate = nodes.new('ShaderNodeSeparateXYZ')
	math_u = nodes.new('ShaderNodeMath')
	math_u.operation = 'SUBTRACT'
	math_u.inputs[1].default_value = 0.5
	math_v = nodes.new('ShaderNodeMath')
	math_v.operation = 'SUBTRACT'
	math_v.inputs[1].default_value = 0.5
	arctan2 = nodes.new('ShaderNodeMath')
	arctan2.operation = 'ARCTAN2'
	mul_angle = nodes.new('ShaderNodeMath')
	mul_angle.operation = 'MULTIPLY'
	mul_angle.inputs[1].default_value = 60.0

	noise = nodes.new('ShaderNodeTexNoise')
	noise.inputs['Scale'].default_value = 4.0
	noise.inputs['Detail'].default_value = 1.5
	noise.inputs['Roughness'].default_value = 0.5

	add_jitter = nodes.new('ShaderNodeMath')
	add_jitter.operation = 'ADD'

	fract = nodes.new('ShaderNodeMath')
	fract.operation = 'FRACT'

	color_ramp = nodes.new('ShaderNodeValToRGB')
	color_ramp.color_ramp.elements[0].position = 0.30
	color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
	color_ramp.color_ramp.elements[1].position = 0.38
	color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

	bump = nodes.new('ShaderNodeBump')
	bump.inputs['Strength'].default_value = 0.12
	bump.inputs['Distance'].default_value = 0.08

	# Link chain
	links.new(tex_coord.outputs['UV'], separate.inputs['Vector'])
	links.new(separate.outputs['X'], math_u.inputs[0])
	links.new(separate.outputs['Y'], math_v.inputs[0])
	links.new(math_u.outputs[0], arctan2.inputs[0])
	links.new(math_v.outputs[0], arctan2.inputs[1])
	links.new(arctan2.outputs[0], mul_angle.inputs[0])
	links.new(mul_angle.outputs[0], add_jitter.inputs[0])
	links.new(noise.outputs['Fac'], add_jitter.inputs[1])
	links.new(add_jitter.outputs[0], fract.inputs[0])
	links.new(fract.outputs[0], color_ramp.inputs['Fac'])
	links.new(color_ramp.outputs['Color'], bump.inputs['Height'])
	links.new(bump.outputs['Normal'], diffuse.inputs['Normal'])

	return mat


def assign_material(obj, mat):
	if obj.data.materials:
		obj.data.materials[0] = mat
	else:
		obj.data.materials.append(mat)


def setup_scene():
	scene = bpy.context.scene
	scene.render.engine = 'BLENDER_EEVEE'
	scene.render.resolution_x = 1920
	scene.render.resolution_y = 1920
	scene.render.resolution_percentage = 100
	scene.render.film_transparent = False
	scene.render.image_settings.file_format = 'PNG'
	scene.render.filepath = RENDER_PATH

	# Background
	scene.world.use_nodes = False
	scene.world.color = (1.0, 1.0, 1.0)

	# EEVEE settings
	scene.eevee.use_gtao = True
	scene.eevee.gtao_distance = 2.0
	scene.eevee.use_ssr = False
	scene.eevee.use_bloom = False


def setup_camera():
	bpy.ops.object.camera_add(location=(0, 5.5, 2.0), rotation=(math.pi / 2, 0, 0))
	cam = bpy.context.active_object
	cam.name = 'MainCamera'
	# Rotate to look at character from back
	cam.rotation_euler = (math.pi / 2, 0, 0)
	bpy.context.scene.camera = cam

	# Orthographic
	cam.data.type = 'ORTHO'
	cam.data.ortho_scale = 3.8

	bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1.6))
	target = bpy.context.active_object
	target.name = 'CameraTarget'

	# TrackTo constraint
	track = cam.constraints.new(type='TRACK_TO')
	track.target = target
	track.track_axis = 'TRACK_NEGATIVE_Z'
	track.up_axis = 'UP_Y'

	return cam


def setup_lights():
	bpy.ops.object.light_add(type='AREA', location=(0, 4.5, 4.0))
	key = bpy.context.active_object
	key.name = 'KeyLight'
	key.data.energy = 800
	key.data.color = (1.0, 0.98, 0.95)
	key.scale = (3, 3, 1)

	bpy.ops.object.light_add(type='AREA', location=(0, -1.5, 0.5))
	fill = bpy.context.active_object
	fill.name = 'FillLight'
	fill.data.energy = 200
	fill.data.color = (0.95, 0.97, 1.0)
	fill.scale = (2, 2, 1)

	bpy.ops.object.light_add(type='AREA', location=(0, 6.5, 0.3))
	rim = bpy.context.active_object
	rim.name = 'RimLight'
	rim.data.energy = 100
	rim.data.color = (1, 1, 1)
	rim.scale = (3, 3, 1)


def setup_freestyle():
	scene = bpy.context.scene
	scene.render.use_freestyle = True
	view_layer = scene.view_layers[0]
	view_layer.use_freestyle = True

	fs = view_layer.freestyle_settings
	fs.mode = 'SCRIPT'
	# Remove default line set
	for ls in list(fs.linesets):
		fs.linesets.remove(ls)

	# Create a new line set
	line_set = fs.linesets.new(name='InkLines')
	line_set.select_silhouette = True
	line_set.select_border = True
	line_set.select_crease = True
	line_set.select_edge_mark = True
	line_set.select_contour = True
	line_set.select_suggestive_contour = True
	line_set.select_material_boundary = True
	line_set.select_external_contour = True
	line_set.edge_type_combination = 'OR'

	# Configure line style (auto-created with the line set)
	ls = line_set.linestyle
	ls.color = (0.0, 0.0, 0.0)
	ls.thickness = 1.2


def add_mod_subdiv(obj, levels=1):
	mod = obj.modifiers.new(name='Subdiv', type='SUBSURF')
	mod.levels = levels
	mod.render_levels = levels
	return mod


def main():
	clear_scene()

	skin_mat = make_skin_material()
	sphere_mat = make_sphere_material()

	# Build body parts (torso + arms + neck)
	torso = build_torso()
	torso.modifiers.new(name='Subdiv_body', type='SUBSURF')

	arm_l = build_arm(-1)
	arm_r = build_arm(1)
	neck = build_neck()

	# Join body parts into one mesh
	body = join_meshes([torso, arm_l, arm_r, neck], 'Body')
	body.modifiers.new(name='Subdiv', type='SUBSURF')
	body.modifiers['Subdiv'].levels = 2
	body.modifiers['Subdiv'].render_levels = 2
	bpy.context.view_layer.objects.active = body

	# Build sphere head separately (so it gets its own material)
	sphere = build_sphere_head()
	sphere.modifiers.new(name='Subdiv_sphere', type='SUBSURF')
	sphere.modifiers['Subdiv_sphere'].levels = 2
	sphere.modifiers['Subdiv_sphere'].render_levels = 2

	# Assign materials
	assign_material(body, skin_mat)
	assign_material(sphere, sphere_mat)

	# Smooth shading
	for obj in (body, sphere):
		bpy.context.view_layer.objects.active = obj
		bpy.ops.object.shade_smooth()

	# Setup scene, camera, lights
	setup_scene()
	setup_camera()
	setup_lights()
	setup_freestyle()

	# Render
	bpy.ops.render.render(write_still=True)
	print(f'Render saved to: {RENDER_PATH}')

	# Also export as GLB for viewer
	bpy.ops.object.select_all(action='DESELECT')
	for obj in bpy.data.objects:
		if obj.type in ('MESH',):
			obj.select_set(True)
	bpy.ops.export_scene.gltf(
		filepath=GLB_PATH,
		use_selection=True,
		export_format='GLB',
		export_apply=True,
		export_texcoords=True,
		export_normals=True,
		export_colors=True,
		export_yup=True,
	)
	print(f'GLB exported to: {GLB_PATH}')


if __name__ == '__main__':
	main()
