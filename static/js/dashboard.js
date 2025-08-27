// chrysto1/o-cubo-do-saber/O-Cubo-do-Saber-9c8bcb28da0ed73fdd0786b7eaf101a3fb79ce50/static/js/skinRenderer3D.js

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('skinContainer');
    if (!container) return;

    const skinUrl = container.dataset.skinUrl;
    if (!skinUrl) return;

    // --- 1. Configuração da Cena ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    
    // CORREÇÃO: Fundo transparente
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: false });
    renderer.setClearColor(0x000000, 0); // Define a cor de limpeza como preta e totalmente transparente
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // --- 2. Iluminação ---
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);

    // --- 3. Carregamento da Textura ---
    const textureLoader = new THREE.TextureLoader();
    textureLoader.crossOrigin = 'Anonymous';

    textureLoader.load(skinUrl, (texture) => {
        texture.magFilter = THREE.NearestFilter;
        texture.minFilter = THREE.NearestFilter;

        const player = new THREE.Group();
        scene.add(player);

        const playerParts = {};

        const createPart = (size, position, uvMap, isOverlay = false) => {
            const materials = [];
            const skinW = 64; const skinH = 64;
            const faces = ['right', 'left', 'top', 'bottom', 'front', 'back'];

            faces.forEach(faceName => {
                const [u, v, w, h] = uvMap[faceName];
                const material = new THREE.MeshLambertMaterial({ map: texture.clone(), transparent: true });
                material.map.offset.set(u / skinW, 1 - (v + h) / skinH);
                material.map.repeat.set(w / skinW, h / skinH);
                if (isOverlay) {
                    material.depthWrite = false;
                    material.side = THREE.DoubleSide;
                }
                materials.push(material);
            });

            const geometry = new THREE.BoxGeometry(size[0], size[1], size[2]);
            const mesh = new THREE.Mesh(geometry, materials);
            mesh.position.set(position[0], position[1], position[2]);
            return mesh;
        };
        
        // --- 4. CORREÇÃO DA ANIMAÇÃO: Criação de Pivôs para Membros ---
        // As partes do corpo são criadas e depois adicionadas a grupos de pivô
        // para que girem a partir do "ombro" e do "quadril".
        
        // Cabeça e Tronco
        playerParts.head = createPart([8, 8, 8], [0, 4, 0], { right: [0, 8, 8, 8], left: [16, 8, 8, 8], top: [8, 0, 8, 8], bottom: [16, 0, 8, 8], front: [8, 8, 8, 8], back: [24, 8, 8, 8] });
        playerParts.hat = createPart([8.5, 8.5, 8.5], [0, 4, 0], { right: [32, 8, 8, 8], left: [48, 8, 8, 8], top: [40, 0, 8, 8], bottom: [48, 0, 8, 8], front: [40, 8, 8, 8], back: [56, 8, 8, 8] }, true);
        const headGroup = new THREE.Group();
        headGroup.position.set(0, 4.2, 0);
        headGroup.add(playerParts.head, playerParts.hat);
        
        playerParts.body = createPart([8, 12, 4], [0, 0, 0], { right: [16, 20, 4, 12], left: [28, 20, 4, 12], top: [20, 16, 8, 4], bottom: [28, 16, 8, 4], front: [20, 20, 8, 12], back: [32, 20, 8, 12] });
        playerParts.jacket = createPart([8.5, 12.5, 4.5], [0, 0, 0], { right: [16, 36, 4, 12], left: [28, 36, 4, 12], top: [20, 32, 8, 4], bottom: [28, 32, 8, 4], front: [20, 36, 8, 12], back: [32, 36, 8, 12] }, true);
        const bodyGroup = new THREE.Group();
        bodyGroup.position.set(0, -2, 0);
        bodyGroup.add(playerParts.body, playerParts.jacket);

        // Braço Esquerdo com Pivô
        const leftArmMesh = createPart([4, 12, 4], [0, -6, 0], { right: [40, 20, 4, 12], left: [48, 20, 4, 12], top: [44, 16, 4, 4], bottom: [48, 16, 4, 4], front: [44, 20, 4, 12], back: [52, 20, 4, 12] });
        const leftSleeveMesh = createPart([4.5, 12.5, 4.5], [0, -6, 0], { right: [40, 36, 4, 12], left: [48, 36, 4, 12], top: [44, 32, 4, 4], bottom: [48, 32, 4, 4], front: [44, 36, 4, 12], back: [52, 36, 4, 12] }, true);
        playerParts.leftArm = new THREE.Group();
        playerParts.leftArm.position.set(6, 4, 0);
        playerParts.leftArm.add(leftArmMesh, leftSleeveMesh);

        // Braço Direito com Pivô
        const rightArmMesh = createPart([4, 12, 4], [0, -6, 0], { right: [40, 52, 4, 12], left: [48, 52, 4, 12], top: [44, 48, 4, 4], bottom: [48, 48, 4, 4], front: [44, 52, 4, 12], back: [52, 52, 4, 12] });
        const rightSleeveMesh = createPart([4.5, 12.5, 4.5], [0, -6, 0], { right: [56, 52, 4, 12], left: [48, 52, 4, 12], top: [44, 48, 4, 4], bottom: [48, 48, 4, 4], front: [44, 52, 4, 12], back: [52, 52, 4, 12] }, true);
        playerParts.rightArm = new THREE.Group();
        playerParts.rightArm.position.set(-6, 4, 0);
        playerParts.rightArm.add(rightArmMesh, rightSleeveMesh);

        // Perna Esquerda com Pivô
        const leftLegMesh = createPart([4, 12, 4], [0, -6, 0], { right: [0, 20, 4, 12], left: [8, 20, 4, 12], top: [4, 16, 4, 4], bottom: [8, 16, 4, 4], front: [4, 20, 4, 12], back: [12, 20, 4, 12] });
        const leftPantMesh = createPart([4.5, 12.5, 4.5], [0, -6, 0], { right: [0, 36, 4, 12], left: [8, 36, 4, 12], top: [4, 32, 4, 4], bottom: [8, 32, 4, 4], front: [4, 36, 4, 12], back: [12, 36, 4, 12] }, true);
        playerParts.leftLeg = new THREE.Group();
        playerParts.leftLeg.position.set(2, -8, 0);
        playerParts.leftLeg.add(leftLegMesh, leftPantMesh);

        // Perna Direita com Pivô
        const rightLegMesh = createPart([4, 12, 4], [0, -6, 0], { right: [16, 52, 4, 12], left: [24, 52, 4, 12], top: [20, 48, 4, 4], bottom: [24, 48, 4, 4], front: [20, 52, 4, 12], back: [28, 52, 4, 12] });
        const rightPantMesh = createPart([4.5, 12.5, 4.5], [0, -6, 0], { right: [0, 52, 4, 12], left: [8, 52, 4, 12], top: [4, 48, 4, 4], bottom: [8, 48, 4, 4], front: [4, 52, 4, 12], back: [12, 52, 4, 12] }, true);
        playerParts.rightLeg = new THREE.Group();
        playerParts.rightLeg.position.set(-2, -8, 0);
        playerParts.rightLeg.add(rightLegMesh, rightPantMesh);

        player.add(headGroup, bodyGroup, playerParts.leftArm, playerParts.rightArm, playerParts.leftLeg, playerParts.rightLeg);
        player.scale.set(1.5, 1.5, 1.5);
        player.position.y = 5; // Ajusta a posição vertical do modelo inteiro

        camera.position.set(0, 5, 40);
        camera.lookAt(0, 0, 0);

        // --- 5. CORREÇÃO DA ANIMAÇÃO: Lógica de Movimento ---
        const clock = new THREE.Clock();
        const animate = () => {
            requestAnimationFrame(animate);
            const delta = clock.getElapsedTime();
            
            // Velocidade e amplitude do andar mais suaves
            const walkSpeed = 6;
            const walkAmplitude = 0.8;
            const angle = Math.sin(delta * walkSpeed) * walkAmplitude;
            
            // O movimento dos pivôs agora rotaciona os membros de forma natural
            playerParts.leftArm.rotation.x = angle;
            playerParts.rightArm.rotation.x = -angle;
            playerParts.leftLeg.rotation.x = -angle;
            playerParts.rightLeg.rotation.x = angle;

            renderer.render(scene, camera);
        };
        animate();

        // --- 6. Interação com Mouse ---
        let isDragging = false;
        let previousMouseX = 0;
        container.onmousedown = (e) => { isDragging = true; previousMouseX = e.clientX; };
        container.onmouseup = () => { isDragging = false; };
        container.onmouseleave = () => { isDragging = false; };
        container.onmousemove = (e) => {
            if (isDragging) {
                const delta = e.clientX - previousMouseX;
                player.rotation.y += delta * 0.02;
                previousMouseX = e.clientX;
            }
        };

    }, undefined, (error) => {
        console.error('Falha ao carregar a textura da skin:', skinUrl, error);
        container.innerHTML = "<p style='color: #c0392b; padding-top: 50px; text-align: center;'>Erro ao carregar skin</p>";
    });
});