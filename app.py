from flask import Flask, request, jsonify, send_file, send_from_directory
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Ruta para guardar temporalmente los gráficos generados
STATIC_DIR = os.path.join(app.root_path, "graphs")
os.makedirs(STATIC_DIR, exist_ok=True)

# Ruta para servir archivos estáticos desde la raíz
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.root_path, filename)

# Rutas Flask
@app.route("/")
def index():
    return send_file("index.html")  # Servir el archivo index.html desde la raíz

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No se proporcionó un archivo"}), 400
    
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        return jsonify({"error": "El archivo debe ser CSV o Excel."}), 400
    
    try:
        resultado = procesar_archivo(file)
        if "error" in resultado:
            return jsonify({"error": resultado["error"]}), 400
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
