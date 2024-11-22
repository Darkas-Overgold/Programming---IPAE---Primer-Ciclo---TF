// Obtener elementos del DOM
const dragDropArea = document.getElementById('drag-drop-area');
const fileInput = document.getElementById('file-input');
const fileInputTrigger = document.getElementById('file-input-trigger');
const uploadButton = document.getElementById('upload-button');
let selectedFile = null; // Variable para almacenar el archivo seleccionado

// Mostrar área activa al arrastrar un archivo
dragDropArea.addEventListener('dragover', (e) => {
    e.preventDefault(); // Prevenir el comportamiento predeterminado
    dragDropArea.classList.add('drag-over'); // Añadir clase para resaltar el área
});

// Eliminar resaltado cuando se sale del área de arrastre
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

// Hacer clic para seleccionar un archivo
dragDropArea.addEventListener('click', () => {
    fileInput.click();
});

// Validar y mostrar el archivo seleccionado
fileInput.addEventListener('change', () => {
    selectedFile = fileInput.files[0];
    if (selectedFile) {
        dragDropArea.querySelector('p').textContent = `Archivo seleccionado: ${selectedFile.name}`;
    }
});

// Manejar el clic en el botón "Subir Archivo"
uploadButton.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Por favor, selecciona un archivo primero.');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    const results = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');

    // Ocultar mensaje de error si todo sale bien
    errorMessage.style.display = 'none';

    if (data.error) {
        // Mostrar error si el procesamiento falla
        results.style.display = 'none';
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = `<p style="color: red;">${data.error}</p>`;
    } else {
        // Mostrar los resultados si todo está bien
        results.style.display = 'block';
        results.innerHTML = `
            <h2>Resultados del Grafo</h2>
            <p id="peso_total">Peso total del MST: ${data.peso_total} USD</p>
            <div class="grafico-container">
                <div class="grafico-box">
                    <h3>Grafo Completo</h3>
                    <img id="grafo_completo" src="${data.grafo}" alt="Grafo Completo">
                </div>
                <div class="grafico-box">
                    <h3>Árbol de Expansión Mínima (MST)</h3>
                    <img id="mst" src="${data.mst}" alt="Árbol de Expansión Mínima">
                </div>
            </div>
            <a href="/">Volver a la página principal</a>
        `;
    }
});
