from flask import Flask, request, jsonify, send_file
import pandas as pd
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import os
import sqlite3
import json

app = Flask(__name__)

# Configuración de directorios
STATIC_DIR = os.path.join(app.root_path, "graphs")
os.makedirs(STATIC_DIR, exist_ok=True)

# Configuración de la base de datos
DB_PATH = os.path.join(app.root_path, "file_uploads.sql")

def init_db() -> None:
    """Inicializa la base de datos y crea la tabla de uploads si no existe."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    graph_path TEXT,
                    mst_path TEXT
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")

init_db()

# Procesar archivo y crear grafo
def procesar_archivo(file):
    try:
        # Leer archivo
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return {"error": "Formato no compatible. Por favor sube un archivo .csv o .xlsx."}

        # Crear grafo
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_edge(row['Nodo 1'], row['Nodo 2'], 
                       distance=row['Distancia (km)'], length=row['Longitud (km)'],
                       thickness=row['Grosor (cm)'], cost=row['Costo (usd)'])

        # Generar gráficos
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        plt.savefig(grafo_path)
        plt.close()

        mst_edges = list(nx.minimum_spanning_edges(G, data=False))
        nx.draw(G, pos, with_labels=True, edgelist=mst_edges, edge_color='r')
        plt.savefig(mst_path)
        plt.close()

        return {"grafo": grafo_path, "mst": mst_path}
    except Exception as e:
        return {"error": f"Ocurrió un error al generar los gráficos: {str(e)}"}

@app.route('/static/grafo.png')
def favicon():
    """Ruta para el favicon."""
    return send_from_directory(os.path.join(app.root_path,'static'), 'grafo.png')

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    """Ruta para subir un archivo y procesarlo."""
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No se ha subido ningún archivo."}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO uploads (filename) VALUES (?)", (file.filename,))
            conn.commit()
            upload_id = cursor.lastrowid
            
        result = procesar_archivo(file)
        if "error" in result:
            return jsonify(result), 400

    return jsonify({
        "grafo": f"/graphs/{os.path.basename(result['grafo'])}",
        "mst": f"/graphs/{os.path.basename(result['mst'])}"
    })

if __name__ == "__main__":
    app.run(debug=True)