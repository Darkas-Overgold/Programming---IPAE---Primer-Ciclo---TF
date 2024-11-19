const form = document.getElementById('upload-form');
form.onsubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const response = await fetch("/upload", {
        method: "POST",
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
            <!-- Contenedor de los gráficos -->
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
};
