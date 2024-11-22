const dragDropArea = document.getElementById('drag-drop-area');
const fileInput = document.getElementById('file-input');
const fileInputTrigger = document.getElementById('file-input-trigger');
const uploadButton = document.getElementById('upload-button');
let selectedFile = null;

// Mostrar área activa al arrastrar un archivo
dragDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dragDropArea.classList.add('drag-over');
});

dragDropArea.addEventListener('dragleave', () => {
    dragDropArea.classList.remove('drag-over');
});

// Manejar el evento drop
dragDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDropArea.classList.remove('drag-over');
    selectedFile = e.dataTransfer.files[0];

    if (selectedFile) {
        dragDropArea.querySelector('p').textContent = `Archivo seleccionado: ${selectedFile.name}`;
    }
});

// Hacer clic en el texto o el área para seleccionar un archivo
fileInputTrigger.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    selectedFile = fileInput.files[0];
    if (selectedFile) {
        dragDropArea.querySelector('p').textContent = `Archivo seleccionado: ${selectedFile.name}`;
    }
});

// Subir archivo
uploadButton.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Por favor, selecciona un archivo primero.');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();
    const results = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');

    errorMessage.style.display = 'none';

    if (data.error) {
        results.style.display = 'none';
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = `<p style="color: red;">${data.error}</p>`;
    } else {
        results.style.display = 'block';
        document.getElementById('peso_total').textContent = `Peso total del MST: ${data.peso_total} USD`;
        document.getElementById('grafo_completo').src = data.grafo;
        document.getElementById('mst').src = data.mst;
    }
});

// Agregar funcionalidad de zoom a las imágenes
document.querySelectorAll('.zoom-button').forEach(button => {
    button.addEventListener('click', () => {
        const img = button.parentElement.querySelector('img');
        const zoom = button.getAttribute('data-zoom');
        const currentScale = parseFloat(img.style.transform.replace('scale(', '').replace(')', '') || 1);
        img.style.transform = `scale(${zoom === 'in' ? currentScale + 0.1 : Math.max(currentScale - 0.1, 1)})`;
    });
});
