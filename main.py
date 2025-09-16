from graph import GrafoDenso
from visualization import desenhar_grafo
from load_data import load_data

# Carregar dados
facebook_dir = "C:/Users/user/Downloads/facebook/facebook"
G_nx, node_features, circles = load_data(facebook_dir)

# Criar grafo
vertices = list(G_nx.nodes())
arestas = list(G_nx.edges())
grafo = GrafoDenso(vertices, arestas=arestas, features=node_features, circles=circles)

# Métricas
print("Centralidade grau:", grafo.centralidade_grau())
print("Centralidade proximidade:", grafo.centralidade_proximidade())
print("Centralidade intermediação:", grafo.centralidade_intermediacao())
print("PageRank:", grafo.pagerank())
comunidades = grafo.girvan_newman()
print("Comunidades:", comunidades)

# Visualização
desenhar_grafo(grafo, centralidade=grafo.centralidade_grau(), comunidades=comunidades)
