import csv
import networkx as nx
import matplotlib.pyplot as plt
# Crear un grafo vacío como un diccionario
grafo = {}
try:
    # Leer el archivo CSV con tabulaciones
    with open("Datos.csv", mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        # Saltar la cabecera
        next(reader)
        # Añadir las aristas al grafo
        for row in reader:
            # Extraer los valores de cada columna
            origen = row[0].strip()  # Nodo 1
            destino = row[1].strip()  # Nodo 2
            distancia = int(row[2].strip())  # Distancia (km)
            grosor = int(row[3].strip())  # Grosor (cm)
            costo = int(row[4].strip())  # Costo (USD)
            print(f"Arista añadida: {origen} -> {destino} | Distancia: {distancia} km, Grosor: {grosor} cm, Costo: ${costo}")
            # Añadir el nodo de origen y destino al grafo
            if origen not in grafo:
                grafo[origen] = set()
            if destino not in grafo:
                grafo[destino] = set()
            # Añadir el destino a la lista de adyacencias del origen y viceversa, evitando auto-bordes
            if origen != destino:
                grafo[origen].add(destino)
                grafo[destino].add(origen)
    # Crear un grafo usando NetworkX
    G = nx.Graph()
    for origen, destinos in grafo.items():
        for destino in destinos:
            G.add_edge(origen, destino)
    # Imprimir en consola el número total de nodos y aristas
    print(f"\nTotal de nodos: {G.number_of_nodes()}")
    print(f"Total de aristas: {G.number_of_edges()}")
    # Dibujar el grafo
    plt.figure(figsize=(10, 8))  # Ajustar el tamaño de la figura
    plt.gcf().canvas.manager.set_window_title("Grafo")
    pos = nx.spring_layout(G)  # Usar el layout de resorte para distribuir los nodos
    nx.draw(
        G, pos, with_labels=True, node_size=500, node_color='blue', 
        font_size=10, font_weight='bold', font_color='white', edge_color='gold'
    )
    # Mostrar la gráfica
    plt.title("Representación Gráfica del Grafo")
    plt.show()
except FileNotFoundError:
    print("El archivo Datos.csv no fue encontrado. Verifica la ruta o nombre del archivo.")
except Exception as e:
    print(f"Ocurrió un error: {e}")