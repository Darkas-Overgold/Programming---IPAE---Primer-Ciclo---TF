from flask import Flask, request, jsonify, send_file, send_from_directory
import pandas as pd
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import os
import json

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de directorios para gráficos y archivos JSON
STATIC_DIR = os.path.join(app.root_path, "graphs")
os.makedirs(STATIC_DIR, exist_ok=True)

JSON_DIR = os.path.join(app.root_path, "jsons")
os.makedirs(JSON_DIR, exist_ok=True)

# Ruta de la base de datos
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
                    mst_path TEXT,
                    json_path TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")

# Inicializar la base de datos al iniciar la aplicación
init_db()

def procesar_archivo(file, upload_id):
    """Procesa el archivo subido y genera gráficos y un archivo JSON."""
    try:
        # Leer el archivo subido
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return {"error": "Formato no compatible. Por favor sube un archivo .csv o .xlsx."}

        # Validar si las columnas necesarias existen
        required_columns = ['Nodo 1', 'Nodo 2', 'Distancia (km)', 'Longitud (km)', 'Grosor (cm)', 'Costo (usd)']
        if not all(col in df.columns for col in required_columns):
            return {"error": f"El archivo debe contener las siguientes columnas: {', '.join(required_columns)}"}

        # Crear el grafo utilizando NetworkX
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_edge(row['Nodo 1'], row['Nodo 2'], 
                       distance=row['Distancia (km)'], length=row['Longitud (km)'],
                       thickness=row['Grosor (cm)'], cost=row['Costo (usd)'])
        
        # Generar rutas para guardar los gráficos y el JSON
        grafo_path = os.path.join(STATIC_DIR, f'grafo_{upload_id}.png')
        mst_path = os.path.join(STATIC_DIR, f'mst_{upload_id}.png')
        json_path = os.path.join(JSON_DIR, f'data_{upload_id}.json')

        # Generar y guardar el gráfico del grafo
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        plt.savefig(grafo_path)
        plt.close()

        # Generar y guardar el gráfico del árbol de expansión mínima
        mst_edges = list(nx.minimum_spanning_edges(G, data=False))
        nx.draw(G, pos, with_labels=True, edgelist=mst_edges, edge_color='r')
        plt.savefig(mst_path)
        plt.close()

        # Guardar información del grafo en un archivo JSON
        data = {
            "nodes": list(G.nodes(data=True)),
            "edges": list(G.edges(data=True)),
            "graph_info": {
                "filename": file.filename,
                "upload_id": upload_id,
                "num_nodes": G.number_of_nodes(),
                "num_edges": G.number_of_edges()
            }
        }
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file)

        # Actualizar la base de datos con las rutas de los gráficos y el JSON
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE uploads SET graph_path = ?, mst_path = ?, json_path = ? WHERE id = ?",
                           (grafo_path, mst_path, json_path, upload_id))
            conn.commit()

        return {"grafo": grafo_path, "mst": mst_path, "json": json_path}
    except Exception as e:
        return {"error": f"Ocurrió un error al generar los gráficos: {str(e)}"}

@app.route('/static/<path:filename>')
def serve_graph(filename):
    """Ruta para servir los gráficos generados."""
    return send_from_directory(STATIC_DIR, filename)

@app.route('/jsons/<path:filename>')
def serve_json(filename):
    """Ruta para servir los archivos JSON generados."""
    return send_from_directory(JSON_DIR, filename)

@app.route("/")
def index():
    """Ruta principal que devuelve el archivo index.html."""
    return send_file("index.html")
@app.route("/")
def styles():
    """Ruta principal que devuelve el archivo styles.css."""
    return send_file("styles.css")

@app.route("/upload", methods=["POST"])
def upload_file():
    """Ruta para subir un archivo y procesarlo."""
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No se ha subido ningún archivo."}), 400

    try:
        # Insertar el registro en la base de datos
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO uploads (filename) VALUES (?)", (file.filename,))
            conn.commit()
            upload_id = cursor.lastrowid
            
        # Procesar el archivo
        result = procesar_archivo(file, upload_id)
        if "error" in result:
            return jsonify(result), 400

        # Devolver las rutas de los archivos generados
        return jsonify({
            "grafo": f"/static/grafo_{upload_id}.png",
            "mst": f"/static/mst_{upload_id}.png",
            "json": f"/jsons/data_{upload_id}.json"
        })
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error al procesar el archivo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
