// Aguarda o conteúdo da página carregar antes de executar o script
document.addEventListener('DOMContentLoaded', function() {
    
    // Encontra o canvas na página
    const skinCanvas = document.getElementById("skin_container");

    // Se o canvas não existir, interrompe o script para evitar erros
    if (!skinCanvas) {
        return;
    }

    // Pega os caminhos das skins a partir dos 'data-attributes' do HTML
    const skinUrl = skinCanvas.dataset.skinUrl;
    const defaultSkinUrl = skinCanvas.dataset.defaultSkinUrl;

    let skinViewer = new skinview3d.SkinViewer({
        canvas: skinCanvas,
        width: 250,
        height: 300,
        // Usa a skin do usuário se existir, senão usa a padrão
        skin: skinUrl ? skinUrl : defaultSkinUrl
    });

    // Controle de câmera (zoom, rotação)
    let control = skinview3d.createOrbitControls(skinViewer);
    control.enableRotate = true;
    control.enableZoom = true;
    control.enablePan = false;

    // Animação de caminhada
    let walk = skinViewer.animations.add(skinview3d.WalkingAnimation);
});