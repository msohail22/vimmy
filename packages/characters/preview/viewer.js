import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const app = document.querySelector('#app');
const errorBox = document.querySelector('#error');
const browser = document.querySelector('#browser');

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111318);

const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.01, 100);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minDistance = 0.5;
controls.maxDistance = 15;
controls.target.set(0, 0.2, 0);
controls.update();

const hemiLight = new THREE.HemisphereLight(0x404060, 0x101020, 1.5);
scene.add(hemiLight);

const keyLight = new THREE.DirectionalLight(0xff8866, 3.0);
keyLight.position.set(3, 5, 4);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0x4466ff, 1.2);
fillLight.position.set(-4, 2, -3);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xff8844, 0.8);
rimLight.position.set(-2, 3, -5);
scene.add(rimLight);

const loader = new GLTFLoader();

let currentModel = null;

function loadModel(path) {
	if (currentModel) {
		scene.remove(currentModel);
		currentModel = null;
	}

	errorBox.style.display = 'none';
	loader.load(
		path,
		(gltf) => {
			const model = gltf.scene;
			model.traverse((child) => {
				if (child.isMesh) {
					child.castShadow = true;
					child.receiveShadow = true;
				}
			});

			scene.add(model);
			currentModel = model;

			const box = new THREE.Box3().setFromObject(model);
			const size = box.getSize(new THREE.Vector3());
			const center = box.getCenter(new THREE.Vector3());
			const radius = size.length() * 0.5;
			const distance = radius / Math.sin(THREE.MathUtils.degToRad(camera.fov * 0.5));

			controls.target.copy(center);
			camera.position.set(0, center.y, distance);
			camera.near = Math.max(distance / 500, 0.01);
			camera.far = distance * 10;
			camera.updateProjectionMatrix();
			controls.update();
		},
		undefined,
		(err) => {
			errorBox.style.display = 'block';
			errorBox.textContent = `Failed to load model. ${err?.message ?? ''}`;
		}
	);
}

async function initBrowser() {
	const res = await fetch('../assets/manifest.json');
	const manifest = await res.json();

	let activeButton = null;

	function buildCategory(name, models) {
		const section = document.createElement('div');
		section.className = 'category';

		const header = document.createElement('div');
		header.className = 'category-header';
		header.textContent = name;
		section.appendChild(header);

		for (const m of models) {
			const btn = document.createElement('button');
			btn.className = 'model-btn';
			btn.textContent = m.name;
			btn.title = m.description;
			btn.dataset.path = `../assets/${m.file}`;
			btn.addEventListener('click', () => {
				if (activeButton) activeButton.classList.remove('active');
				btn.classList.add('active');
				activeButton = btn;
				loadModel(btn.dataset.path);
			});
			section.appendChild(btn);
		}

		return section;
	}

	if (manifest.bosses) browser.appendChild(buildCategory('Bosses', manifest.bosses));
	if (manifest.beasts) browser.appendChild(buildCategory('Beasts', manifest.beasts));
	if (manifest.minions) browser.appendChild(buildCategory('Minions', manifest.minions));
	if (manifest.characters) browser.appendChild(buildCategory('Characters', manifest.characters));

	const firstBtn = browser.querySelector('.model-btn');
	if (firstBtn) {
		firstBtn.classList.add('active');
		activeButton = firstBtn;
		loadModel(firstBtn.dataset.path);
	}
}

initBrowser();

window.addEventListener('resize', () => {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
	requestAnimationFrame(animate);
	controls.update();
	renderer.render(scene, camera);
}

animate();
