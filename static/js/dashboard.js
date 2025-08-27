// chrysto1/o-cubo-do-saber/O-Cubo-do-Saber-c0080c4f624e438c722d4cfe2b703ecc560dcf51/static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('skinCanvas');
    if (!canvas) {
        console.error('Elemento canvas não encontrado!');
        return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Não foi possível obter o contexto 2D do canvas.');
        return;
    }

    // Pega a URL da skin do atributo data-skin-url no elemento canvas
    const skinUrl = canvas.dataset.skinUrl;

    if (!skinUrl) {
        console.error('URL da skin não encontrada no atributo data-skin-url.');
        return;
    }

    const skinImage = new Image();
    skinImage.src = skinUrl;

    // Evento que é disparado quando a imagem termina de carregar
    skinImage.onload = () => {
        // Limpa o canvas antes de desenhar
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Aumenta a nitidez da imagem para evitar que fique borrada
        ctx.imageSmoothingEnabled = false;

        // Desenha a parte da frente da skin (cabeça e corpo)
        // Essas coordenadas são padrões para skins 64x64 do Minecraft
        
        // Cabeça (camada 1)
        ctx.drawImage(skinImage, 8, 8, 8, 8, 60, 50, 80, 80); 
        // Corpo (camada 1)
        ctx.drawImage(skinImage, 20, 20, 8, 12, 60, 130, 80, 120);
        // Braço Direito (camada 1)
        ctx.drawImage(skinImage, 44, 20, 4, 12, 20, 130, 40, 120);
        // Braço Esquerdo (camada 1)
        ctx.drawImage(skinImage, 36, 52, 4, 12, 140, 130, 40, 120);
        // Perna Direita (camada 1)
        ctx.drawImage(skinImage, 4, 20, 4, 12, 60, 250, 40, 120);
        // Perna Esquerda (camada 1)
        ctx.drawImage(skinImage, 20, 52, 4, 12, 100, 250, 40, 120);
    };

    // Evento para caso a imagem não possa ser carregada
    skinImage.onerror = () => {
        console.error('Erro ao carregar a imagem da skin:', skinUrl);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'red';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Erro ao carregar skin', canvas.width / 2, canvas.height / 2);
    };
});