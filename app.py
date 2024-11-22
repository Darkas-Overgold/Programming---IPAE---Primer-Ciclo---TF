from flask import Flask, request, jsonify, send_from_directory
import os
import pandas as pd
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)
STATIC_DIR = os.path.join(app.root_path, "static", "graphs")
os.makedirs(STATIC_DIR, exist_ok=True)
DB_PATH = os.path.join(app.root_path, "file_uploads.db")

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

def validar_columnas(df: pd.DataFrame, required_columns: list) -> dict:
    """Valida si el DataFrame contiene las columnas requeridas."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    return {"error": f"El archivo debe contener las columnas: {', '.join(missing_columns)}."} if missing_columns else {}

def procesar_archivo(file) -> dict:
    """Procesa el archivo subido y genera gráficos a partir de él."""
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return {"error": "Formato no compatible. Por favor sube un archivo .csv o .xlsx."}

        required_columns = ['Nodo 1', 'Nodo 2', 'Costo (usd)', 'Distancia (km)', 'Longitud (km)', 'Grosor (cm)']
        validation_result = validar_columnas(df, required_columns)
        if validation_result:
            return validation_result

        return generar_graficos(df, file.filename)

    except Exception as e:
        return {"error": f"Ocurrió un error al procesar el archivo: {str(e)}"}

def generar_graficos(df: pd.DataFrame, filename: str) -> dict:
    """Genera gráficos a partir del DataFrame y guarda las imágenes."""
    try:
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_edge(row['Nodo 1'], row['Nodo 2'], 
                       distance=row['Distancia (km)'], length=row['Longitud (km)'],
                       thickness=row['Grosor (cm)'], cost=row['Costo (usd)'])

        grafo_path = os.path.join(STATIC_DIR, f"grafo_{os.path.splitext(filename)[0]}.png")
        mst_path = os.path.join(STATIC_DIR, f"mst_{os.path.splitext(filename)[0]}.png")

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
    """Ruta principal que devuelve el index.html."""
    return send_from_directory('.', 'index.html')

@app.route("/styles.css")
def styles():
    """Ruta para devolver el archivo CSS."""
    return send_from_directory('.', 'styles.css')

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

        # Actualizar la base de datos con las rutas de los gráficos
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE uploads SET graph_path = ?, mst_path = ? WHERE id = ?",
                           (result['grafo'], result['mst'], upload_id))
            conn.commit()

        return jsonify({
            "message": "Archivo procesado exitosamente.",
            "grafo": f"/static/graphs/{os.path.basename(result['grafo'])}",
            "mst": f"/static/graphs/{os.path.basename(result['mst'])}"
        })
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error al subir el archivo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)