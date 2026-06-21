import * as THREE from 'three';
import { Document, NodeIO, Accessor } from '@gltf-transform/core';
import { writeFileSync, mkdirSync } from 'node:fs';

const BODY_COLOR = 0xccaaee;
const HEAD_COLOR = 0x8822aa;

function cap(radius, length, segs) {
	return new THREE.CapsuleGeometry(radius, length, segs || 12, 16);
}
function sphere(radius, segs) {
	return new THREE.SphereGeometry(radius, segs || 28, 28);
}
function box(w, h, d) {
	return new THREE.BoxGeometry(w, h, d);
}
function mat(color) {
	return new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.0 });
}

function add(parent, geo, pos, rot) {
	const m = new THREE.Mesh(geo, mat(BODY_COLOR));
	m.position.set(pos[0], pos[1], pos[2]);
	if (rot) m.rotation.set(rot[0], rot[1], rot[2]);
	m.castShadow = true;
	m.receiveShadow = true;
	parent.add(m);
	return m;
}

function addHead(parent, geo, pos) {
	const m = new THREE.Mesh(geo, mat(HEAD_COLOR));
	m.position.set(pos[0], pos[1], pos[2]);
	m.castShadow = true;
	m.receiveShadow = true;
	parent.add(m);
	return m;
}

const group = new THREE.Group();

// === TORSO ===
add(group, cap(0.55, 0.5), [0, 1.55, 0]);
add(group, cap(0.48, 0.45), [0, 1.15, 0]);
add(group, cap(0.40, 0.3), [0, 0.75, 0]);
add(group, cap(0.42, 0.3), [0, 0.4, 0]);
add(group, cap(0.44, 0.25), [0, 0.12, -0.1]);

// === SHOULDERS ===
add(group, sphere(0.3), [-0.62, 1.7, 0]);
add(group, sphere(0.3), [0.62, 1.7, 0]);
add(group, sphere(0.22), [-0.68, 1.75, 0.05]);
add(group, sphere(0.22), [0.68, 1.75, 0.05]);

// === NECK ===
add(group, cap(0.15, 0.18), [0, 2.15, 0]);

// === HEAD ===
addHead(group, sphere(0.8), [0, 2.7, 0]);

// === LEFT ARM ===
add(group, cap(0.19, 0.5), [-0.82, 1.4, 0], [0, 0, -0.25]);
add(group, cap(0.15, 0.45), [-0.98, 1.0, 0], [0, 0, -0.3]);
add(group, sphere(0.1), [-1.08, 0.72, 0]);

// === RIGHT ARM ===
add(group, cap(0.19, 0.5), [0.82, 1.4, 0], [0, 0, 0.25]);
add(group, cap(0.15, 0.45), [0.98, 1.0, 0], [0, 0, 0.3]);
add(group, sphere(0.1), [1.08, 0.72, 0]);

// === LEFT LEG ===
add(group, cap(0.24, 0.5), [-0.24, 0.0, 0]);
add(group, cap(0.17, 0.45), [-0.24, -0.44, 0]);
add(group, box(0.22, 0.1, 0.4), [-0.24, -0.72, 0.1]);

// === RIGHT LEG ===
add(group, cap(0.24, 0.5), [0.24, 0.0, 0]);
add(group, cap(0.17, 0.45), [0.24, -0.44, 0]);
add(group, box(0.22, 0.1, 0.4), [0.24, -0.72, 0.1]);

// === PECS ===
add(group, sphere(0.18), [-0.23, 1.55, 0.38]);
add(group, sphere(0.18), [0.23, 1.55, 0.38]);

// === 6-PACK ===
for (const p of [
	[-0.15, 1.2, 0.32], [0.15, 1.2, 0.32],
	[-0.14, 1.05, 0.30], [0.14, 1.05, 0.30],
	[-0.13, 0.9, 0.28], [0.13, 0.9, 0.28],
]) {
	add(group, sphere(0.06), p);
}

// === GROIN ===
const groinMat = new THREE.MeshStandardMaterial({ color: 0x9966bb, roughness: 0.6, metalness: 0.0 });
const groin = new THREE.Mesh(box(0.26, 0.12, 0.2), groinMat);
groin.position.set(0, 0.3, 0.12);
groin.castShadow = true;
groin.receiveShadow = true;
group.add(groin);

// ============================================================
// GLB export using @gltf-transform/core
// ============================================================

function hexToRGB(hex) {
	return [
		((hex >> 16) & 0xff) / 255,
		((hex >> 8) & 0xff) / 255,
		(hex & 0xff) / 255,
	];
}

function xformPoint(p, m) {
	const e = m.elements;
	return [
		p[0]*e[0] + p[1]*e[4] + p[2]*e[8]  + e[12],
		p[0]*e[1] + p[1]*e[5] + p[2]*e[9]  + e[13],
		p[0]*e[2] + p[1]*e[6] + p[2]*e[10] + e[14],
	];
}

function xformNormal(n, m) {
	const e = m.elements;
	const x = n[0]*e[0] + n[1]*e[4] + n[2]*e[8];
	const y = n[0]*e[1] + n[1]*e[5] + n[2]*e[9];
	const z = n[0]*e[2] + n[1]*e[6] + n[2]*e[10];
	const len = Math.sqrt(x*x + y*y + z*z);
	return len > 0 ? [x/len, y/len, z/len] : [0, 0, 0];
}

const doc = new Document();
doc.createBuffer('buffer');

group.updateMatrixWorld(true);

const primsByColor = new Map();
const colorToName = { [BODY_COLOR]: 'Body', [HEAD_COLOR]: 'Head', [0x9966bb]: 'Groin' };

group.traverse((child) => {
	if (!child.isMesh || !child.geometry) return;
	const geo = child.geometry;
	const pos = geo.getAttribute('position');
	const norm = geo.getAttribute('normal');
	const idx = geo.getIndex();
	if (!pos || !norm) return;

	const wm = child.matrixWorld;
	const hex = child.material.color.getHex();

	if (!primsByColor.has(hex)) {
		primsByColor.set(hex, { pos: [], norm: [], idx: [], off: 0 });
	}
	const entry = primsByColor.get(hex);

	for (let i = 0; i < pos.count; i++) {
		const p = xformPoint([pos.getX(i), pos.getY(i), pos.getZ(i)], wm);
		const n = xformNormal([norm.getX(i), norm.getY(i), norm.getZ(i)], wm);
		entry.pos.push(p[0], p[1], p[2]);
		entry.norm.push(n[0], n[1], n[2]);
	}

	if (idx) {
		for (let i = 0; i < idx.count; i++) entry.idx.push(idx.getX(i) + entry.off);
	} else {
		for (let i = 0; i < pos.count; i++) entry.idx.push(entry.off + i);
	}
	entry.off += pos.count;
});

const scene = doc.createScene('Scene');
const node = doc.createNode('BallHeadBoss');
scene.addChild(node);
const mesh = doc.createMesh('BallHeadBoss');
node.setMesh(mesh);

for (const [hex, data] of primsByColor) {
	const prim = doc.createPrimitive();

	const posAcc = doc.createAccessor()
		.setType('VEC3')
		.setArray(new Float32Array(data.pos));
	const normAcc = doc.createAccessor()
		.setType('VEC3')
		.setArray(new Float32Array(data.norm));
	const idxAcc = doc.createAccessor()
		.setType('SCALAR')
		.setArray(new Uint16Array(data.idx));

	prim.setAttribute('POSITION', posAcc);
	prim.setAttribute('NORMAL', normAcc);
	prim.setIndices(idxAcc);

	const matName = colorToName[hex] || `Mat${hex.toString(16)}`;
	const mat = doc.createMaterial(matName);
	const [r, g, b] = hexToRGB(hex);
	mat.setBaseColorFactor([r, g, b, 1]);
	mat.setMetallicFactor(0);
	mat.setRoughnessFactor(0.4);
	prim.setMaterial(mat);

	mesh.addPrimitive(prim);
}

const io = new NodeIO();
const glbBuf = await io.writeBinary(doc);
const outPath = '/home/sohail/Github/vimmy/packages/characters/assets/bosses/ball-head-boss.glb';
mkdirSync('/home/sohail/Github/vimmy/packages/characters/assets/bosses', { recursive: true });
writeFileSync(outPath, Buffer.from(glbBuf));
console.log(`Wrote ${glbBuf.byteLength} bytes to ${outPath}`);
