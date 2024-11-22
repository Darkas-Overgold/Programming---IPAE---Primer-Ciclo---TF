from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import sqlite3

app = Flask(__name__)

# Configuración de directorios
STATIC_DIR = os.path.join(app.root_path, "static", "graphs")
os.makedirs(STATIC_DIR, exist_ok=True)

DB_PATH = os.path.join(app.root_path, "file_uploads.sql")

# Inicializar base de datos
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

def procesar_archivo(file):
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            raise ValueError("Formato no compatible")

        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_edge(row['nodo 1'], row['nodo 2'], weight=row['costo (usd)'])

        pos = nx.spring_layout(G)
        grafo_path = os.path.join(STATIC_DIR, "grafo_completo.png")
        mst_path = os.path.join(STATIC_DIR, "mst.png")

        nx.draw(G, pos, with_labels=True)
        plt.savefig(grafo_path)
        plt.close()

        mst_edges = list(nx.minimum_spanning_edges(G, data=False))
        nx.draw(G, pos, with_labels=True, edgelist=mst_edges, edge_color='r')
        plt.savefig(mst_path)
        plt.close()

        return {"grafo": grafo_path, "mst": mst_path}
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/styles.css")
def styles():
    return send_from_directory('.', 'styles.css')

@app.route("/grafo.png")
def favicon():
    return send_from_directory('.', 'grafo.png')

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO uploads (filename) VALUES (?)", (file.filename,))
        conn.commit()

    result = procesar_archivo(file)
    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        "grafo": f"/static/graphs/{os.path.basename(result['grafo'])}",
        "mst": f"/static/graphs/{os.path.basename(result['mst'])}"
    })

if __name__ == "__main__":
    app.run(debug=True)
