// Obtener elementos del DOM
const dragDropArea = document.getElementById('drag-drop-area');
const fileInput = document.getElementById('file-input');
const fileInputTrigger = document.getElementById('file-input-trigger');
const uploadButton = document.getElementById('upload-button');
const errorMessage = document.getElementById('error-message');
const results = document.getElementById('results');
const grafoCompletoImg = document.getElementById('grafo_completo');
const grafoMstImg = document.getElementById('grafo_mst');
let selectedFile = null;

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
    e.preventDefault(); // Prevenir el comportamiento predeterminado
    dragDropArea.classList.remove('drag-over'); // Eliminar resaltado
    const file = e.dataTransfer.files[0]; // Obtener el primer archivo
    validarArchivo(file); // Validar el archivo
});

// Activar el input de archivo al hacer clic
fileInputTrigger.addEventListener('click', () => {
    fileInput.click(); // Simular clic en el input de archivo
});

// Validar y mostrar el archivo seleccionado
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0]; // Obtener el archivo seleccionado
    validarArchivo(file); // Validar el archivo
});

// Función para validar el archivo
function validarArchivo(file) {
    // Verificar que el archivo sea CSV
    if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
        selectedFile = file; // Almacenar el archivo seleccionado
        dragDropArea.querySelector('p').textContent = `Archivo seleccionado: ${file.name}`;
        dragDropArea.classList.add('file-selected'); // Añadir clase al área
        errorMessage.style.display = 'none'; // Ocultar mensajes de error
    } else {
        // Mensaje de error si el archivo no es válido
        alert('Por favor selecciona un archivo CSV.');
        selectedFile = null; // Limpiar archivo seleccionado
    }
}

// Subir archivo
uploadButton.addEventListener('click', async () => {
    if (!selectedFile) {
        errorMessage.style.display = 'block'; // Mostrar error si no hay archivo
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile); // Añadir archivo a FormData

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json(); // Obtener respuesta del servidor
        mostrarResultados(data); // Mostrar resultados
    } catch (error) {
        errorMessage.style.display = 'block'; // Mostrar error de carga
        errorMessage.innerHTML = '<p style="color: red;">Hubo un error al subir el archivo. Intenta nuevamente.</p>';
    }
});

// Mostrar resultados o errores
function mostrarResultados(data) {
    errorMessage.style.display = 'none'; // Ocultar mensaje de error al mostrar resultados

    if (data.error) {
        results.style.display = 'none'; // Ocultar resultados si hay error
        errorMessage.style.display = 'block'; // Mostrar mensaje de error
        errorMessage.innerHTML = `<p style="color: red;">${data.error}</p>`;
    } else {
        results.style.display = 'block'; // Mostrar resultados
        document.getElementById('peso_total').textContent = `Peso total del MST: ${data.peso_total}`;
        grafoCompletoImg.src = data.grafo_completo || 'static/graphs/grafo_completo.png'; // Cargar la imagen del grafo completo
        grafoMstImg.src = data.grafo_mst || 'static/graphs/grafo_mst.png'; // Cargar la imagen del MST
    }
}