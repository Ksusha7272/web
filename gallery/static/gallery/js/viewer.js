// 1. Импортируем Three.js по имени из Import Map
import * as THREE from 'three';
// Подключаем "грузчика" для формата GLB
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// НОВЫЙ ИМПОРТ: Контроллер орбиты
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js'
// И нам понадобится PMREMGenerator (преобразует окружение в карту света)
// Он уже встроен в THREE, импортировать отдельно не надо.

// 2. Экспортируем главную функцию
// Она принимает ID HTML-элемента, в который нужно вставить 3D
export function loadModel(containerId, modelUrl) {
    const container = document.getElementById(containerId);
    if (!container) return;
    // 1. Стандартная настройка сцены (как в прошлый раз)
    const scene = new THREE.Scene();
    scene.background = null 
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    

    // --- ВАЖНЫЕ НАСТРОЙКИ ЦВЕТА --
    // 1. Говорим, что текстуры и свет должны быть конвертированы под монитор
    renderer.outputColorSpace = THREE.SRGBColorSpace; 
    // 2. Включаем Tone Mapping (как в кино)
    // ACESFilmic - это стандарт индустрии (Unreal Engine использует его же)
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    // 3. Настраиваем экспозицию (яркость)
    renderer.toneMappingExposure = 1.0; 

    // Очищаем контейнер от текста "Wait..." и вставляем Canvas
    container.innerHTML = ''; 
    container.appendChild(renderer.domElement);
    

    // --- ДОБАВЛЯЕМ УПРАВЛЕНИЕ --
    const controls = new OrbitControls(camera, renderer.domElement);
    // Включаем инерцию (damping), чтобы вращение было плавным, как в Sketchfab
    controls.enableDamping = true; 
    controls.dampingFactor = 0.05;
    // Ограничиваем зум (чтобы не улететь сквозь модель)
    controls.minDistance = 0.1;
    controls.maxDistance = 50;
    // ... (код света и загрузчика) ...
    

    // 2. Свет (ВАЖНО! Без него модель будет черной)
    // PMREMGenerator генерирует карту окружения из сцены
    const environment = new RoomEnvironment();
    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    pmremGenerator.compileEquirectangularShader();

    // Генерируем текстуру окружения и устанавливаем её
    scene.environment = pmremGenerator.fromScene(environment).texture;

    const loaderDiv = document.createElement('div');
    loaderDiv.className = 'loader-overlay';
    loaderDiv.innerHTML = `
        <div style="color: #666; font-size: 0.9rem;">Loading...</div>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
    `;
    container.appendChild(loaderDiv);
    console.log('🎨 WebGLRenderer создан и добавлен в контейнер');
    // Находим полоску, чтобы менять её ширину
    const progressFill = loaderDiv.querySelector('.progress-fill');

    
    // --- 2. Обновляем вызов загрузчика --
    const loader = new GLTFLoader();
    loader.load(modelUrl,(gltf) => {
            const model = gltf.scene;
            fitCameraToObject(camera, model, controls);
            scene.add(model);
            
            // Скрываем лоадер
            loaderDiv.style.opacity = '0';
            setTimeout(() => {
                loaderDiv.remove(); // Удаляем из DOM через 0.3 сек
            }, 300);
        },
        
        // B. ON PROGRESS (Прогресс)
        (xhr) => {
            // xhr.total - общий вес файла в байтах
            // xhr.loaded - сколько скачалось
            if (xhr.total > 0) {
                const percent = (xhr.loaded / xhr.total) * 100;
                progressFill.style.width = percent + '%';
            }
        },
        
        // C. ON ERROR (Ошибка)
        (error) => {
            console.error('Ошибка загрузки:', error);
            loaderDiv.innerHTML = `<div class="error-msg">❌Ошибка загрузки<br><small>Проверьте файл</small></div>`;
        }
    );

    

   
    function animate() {
        requestAnimationFrame(animate);
        // ОБЯЗАТЕЛЬНО: Обновляем контроллер в каждом кадре
        controls.update(); 
        // Авто-вращение можно убрать или оставить по желанию.
        // Если оставить, оно будет конфликтовать с мышкой. 
        // Давайте пока закомментируем авто-вращение:
        // if (loadedModel) loadedModel.rotation.y += 0.005;
        renderer.render(scene, camera);
    }

    animate();
        // Resize handler (как в прошлый раз)
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
        
    });
}

function fitCameraToObject(camera, object, controls) {
    const box = new THREE.Box3().setFromObject(object);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    // Сдвигаем модель в центр
    object.position.x = -center.x;
    object.position.y = -center.y;
    object.position.z = -center.z;
    // Ставим камеру
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.5;
    camera.position.set(cameraZ, cameraZ * 0.5, cameraZ);
    camera.lookAt(0, 0, 0);

    // ВАЖНО: Обновляем цель контроллера, чтобы вращение было вокруг центра модели
    controls.target.set(0, 0, 0);
    controls.update();
}