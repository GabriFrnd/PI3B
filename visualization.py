import networkx as nx
import matplotlib.pyplot as plt

def desenhar_grafo(grafo, centralidade=None, comunidades=None):
    G = nx.Graph()
    for i in range(grafo.n):
        for j in range(i+1, grafo.n):
            if grafo.matriz[i][j] == 1:
                G.add_edge(grafo.vertices[i], grafo.vertices[j])

    pos = nx.spring_layout(G, k=2, seed=42)

    sizes = [300 + 2000*(v/sum(centralidade.values())) for v in centralidade.values()] if centralidade else 500

    if comunidades:
        cor_map = {}
        for idx, com in enumerate(comunidades):
            for v in com:
                cor_map[v] = idx
        colors = [cor_map[v] for v in G.nodes()]
    else:
        colors = "skyblue"

    plt.figure(figsize=(12, 12))
    nx.draw(G, pos, with_labels=True, node_size=sizes, node_color=colors, cmap=plt.cm.Set3, edge_color="gray")
    plt.show()
