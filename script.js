const dragDropArea = document.getElementById('drag-drop-area');
const fileInput = document.getElementById('file-input');
const fileInputTrigger = document.getElementById('file-input-trigger');
const uploadButton = document.getElementById('upload-button');
const errorMessage = document.getElementById('error-message');
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
    const file = e.dataTransfer.files[0];
    validarArchivo(file);
});

// Activar el input de archivo al hacer clic
fileInputTrigger.addEventListener('click', () => {
    fileInput.click();
});

// Validar y mostrar el archivo seleccionado
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    validarArchivo(file);
});

// Función para validar el archivo
function validarArchivo(file) {
    if (file && file.type === 'text/csv') {
        selectedFile = file;
        dragDropArea.querySelector('p').textContent = Archivo seleccionado: ${file.name};
        dragDropArea.classList.add('file-selected');
        errorMessage.style.display = 'none';
    } else {
        alert('Por favor selecciona un archivo CSV.');
        selectedFile = null;
    }
}

// Subir archivo
uploadButton.addEventListener('click', async () => {
    if (!selectedFile) {
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = <p style="color: red;">Por favor selecciona un archivo antes de subirlo.</p>;
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Error al subir el archivo.');
        }

        const data = await response.json();
        mostrarResultados(data);
    } catch (error) {
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = <p style="color: red;">Hubo un error al subir el archivo. Intenta nuevamente.</p>;
    }
});

// Mostrar resultados o errores
function mostrarResultados(data) {
    const results = document.getElementById('results');

    errorMessage.style.display = 'none';

    if (data.error) {
        results.style.display = 'none';
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = <p style="color: red;">${data.error}</p>;
    } else {
        results.style.display = 'block';
        document.getElementById('peso_total').textContent = Peso total del MST: ${data.peso_total} USD;
        document.getElementById('grafo_completo').src = data.grafo;
        document.getElementById('mst').src = data.mst;
    }
}

// Agregar funcionalidad de zoom a las imágenes
document.querySelectorAll('.zoom-button').forEach(button => {
    button.addEventListener('click', () => {
        const img = button.parentElement.querySelector('img');
        const zoom = button.getAttribute('data-zoom');
        const currentScale = parseFloat(img.style.transform.replace('scale(', '').replace(')', '') || 1);
        img.style.transform = scale(${zoom === 'in' ? currentScale + 0.1 : Math.max(currentScale - 0.1, 1)});
    });
});
