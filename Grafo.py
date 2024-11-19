import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, Canvas, Button, Label, filedialog, Frame
from tkinterdnd2 import TkinterDnD, DND_FILES
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Función para procesar archivos (detecta CSV o Excel)
def procesar_archivo(archivo):
    try:
        if archivo.endswith('.csv'):
            df = pd.read_csv(archivo, delimiter='\t')
        elif archivo.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            raise ValueError("Formato de archivo no compatible. Use CSV o Excel.")
        columnas_csv = ['Nodo 1', 'Nodo 2', 'Distancia (km)', 'Grosor (cm)', 'Costo (USD)']
        columnas_excel = ['Nodo', 'Nodo vecino 1', 'Costo total 1(USD)']
        if all(col in df.columns for col in columnas_csv):
            G = crear_grafo_csv(df)
        elif all(col in df.columns for col in columnas_excel):
            G = crear_grafo_excel(df)
        else:
            raise ValueError("El archivo no contiene las columnas requeridas.")
        g_mst, peso_total = kruskal(G)
        mostrar_resultados(G, g_mst, peso_total)
    except Exception as e:
        lbl_resultados.config(text=f"Error procesando el archivo: {e}")

# Crear un grafo a partir de un archivo CSV
def crear_grafo_csv(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        nodo1 = row['Nodo 1']
        nodo2 = row['Nodo 2']
        costo = row['Costo (USD)']
        if nodo1 != nodo2:
            G.add_edge(nodo1, nodo2, weight=costo)
    return G

# Crear un grafo a partir de un archivo Excel
def crear_grafo_excel(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        nodo = row['Nodo']
        nodo_v1 = row['Nodo vecino 1']
        costo1 = row['Costo total 1(USD)']
        if nodo_v1 != nodo:
            G.add_edge(nodo, nodo_v1, weight=costo1)
    return G

# Clase para manejar Union-Find (algoritmo de Kruskal)
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX != rootY:
            if self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
            elif self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1
            return True
        return False

# Algoritmo de Kruskal para obtener el MST
def kruskal(G):
    node_to_index = {node: idx for idx, node in enumerate(G.nodes())}
    edges = [(data['weight'], node_to_index[u], node_to_index[v], u, v) for u, v, data in G.edges(data=True)]
    edges.sort()
    uf = UnionFind(len(G.nodes()))
    mst = []
    peso_total = 0
    for weight, u_idx, v_idx, u, v in edges:
        if uf.union(u_idx, v_idx):
            mst.append((u, v, weight))
            peso_total += weight
    return mst, peso_total

# Mostrar resultados gráficamente
def mostrar_resultados(G, g_mst, peso_total):
    pos = nx.spring_layout(G)
    mst_edges = [(u, v) for u, v, _ in g_mst]
    imprimir_conexiones("Grafo Completo", G)
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    nx.draw(G, pos, with_labels=True, node_size=500, edge_color='gold', node_color='blue', font_color='white', ax=ax1)
    ax1.set_title("Grafo Completo")
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    nx.draw(G, pos, with_labels=True, node_size=500, edgelist=mst_edges, edge_color='gold', node_color='red', font_color='white', ax=ax2)
    ax2.set_title("Árbol de Expansión Mínima (MST)")
    mostrar_grafica(fig1, canvas_grafo_completo)
    mostrar_grafica(fig2, canvas_mst)
    lbl_resultados.config(text=f"Peso total del MST: {peso_total} USD")

# Imprimir conexiones del grafo en la consola
def imprimir_conexiones(titulo, G):
    conexiones = {}
    print(f"\n{titulo}:")
    for u, v, data in G.edges(data=True):
        peso = data['weight']
        conexiones[(u, v)] = peso
        print(f"Conexión: {u} - {v} con peso {peso}")
    return conexiones

# Mostrar gráfica en un área de Tkinter
def mostrar_grafica(figura, canvas_area):
    for widget in canvas_area.winfo_children():
        widget.destroy()
    canvas_tk = FigureCanvasTkAgg(figura, canvas_area)
    toolbar = NavigationToolbar2Tk(canvas_tk, canvas_area)
    toolbar.update()
    canvas_tk.get_tk_widget().pack()

# Seleccionar archivo mediante un diálogo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV o Excel", "*.csv *.xlsx")])
    if archivo:
        procesar_archivo(archivo)

# Configuración de la interfaz gráfica
app = TkinterDnD.Tk()
app.title("Gestor de Grafos")
app.geometry("1200x800")
canvas = Canvas(app, width=1200, height=50)
canvas.create_text(600, 25, text="Gestor de Grafos con Algoritmo de Kruskal", font=("Arial", 16), fill="gold")
canvas.pack()
frame = Frame(app)
frame.pack(pady=10)
btn_subir = Button(frame, text="Subir Archivo", command=seleccionar_archivo, bg="lightblue", font=("Arial", 12))
btn_subir.pack(pady=5)
lbl_info = Label(app, text="O arrastra un archivo CSV o Excel aquí", font=("Arial", 12), fg="blue")
lbl_info.pack()
lbl_resultados = Label(app, text="", font=("Arial", 12), fg="green")
lbl_resultados.pack(pady=10)
canvas_grafo_completo = Frame(app, width=600, height=600, bg="white")
canvas_grafo_completo.pack(side="left", padx=10, pady=10)
canvas_mst = Frame(app, width=600, height=600, bg="white")
canvas_mst.pack(side="right", padx=10, pady=10)

# Manejar arrastre de archivos
def arrastrar_archivo(event):
    archivo = event.data
    procesar_archivo(archivo)
app.drop_target_register(DND_FILES)
app.dnd_bind('<<Drop>>', arrastrar_archivo)
app.mainloop()
