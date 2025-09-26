import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon

def community_layout(g, communities):
    """
    Cria posições pros nós, organizando em "bolhas" (uma pra cada comunidade).
    """
    meta_graph = nx.Graph()
    community_list = list(communities)
    
    for i in range(len(community_list)):
        meta_graph.add_node(i)

    for i in range(len(community_list)):
        for j in range(i + 1, len(community_list)):
            if nx.edge_boundary(g, community_list[i], community_list[j]):
                meta_graph.add_edge(i, j)
    
    pos_communities = nx.spring_layout(meta_graph, seed=42, scale=3.0)

    pos = {}
    for i, community in enumerate(community_list):
        subgraph = g.subgraph(community)
        pos_subgraph = nx.spring_layout(subgraph, seed=42, scale=0.8)
        
        center = pos_communities.get(i, (np.random.rand(), np.random.rand()))
        for node, (x, y) in pos_subgraph.items():
            pos[node] = (center[0] + x, center[1] + y)

    unassigned_nodes = set(g.nodes()) - set().union(*community_list)
    if unassigned_nodes:
        subgraph_unassigned = g.subgraph(unassigned_nodes)
        pos_unassigned = nx.spring_layout(subgraph_unassigned, seed=42, center=(0,0), scale=2.0)
        pos.update(pos_unassigned)
        
    return pos

def desenhar_grafo(G, comunidades=None, ego_node=None, show=False, ax=None):
    """
    Desenha o grafo.
    - Se show=True → exibe na tela.
    - Se show=False → retorna a figura para ser salva externamente.
    """
    if comunidades and len(comunidades) > 0:
        pos = community_layout(G, comunidades)
    else:
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    default_color = -1 
    cor_map = {node: default_color for node in G.nodes()}
    
    if comunidades:
        for idx, com in enumerate(comunidades):
            for no in com:
                if no in G.nodes():
                    cor_map[no] = idx
    
    colors = [cor_map[no] for no in G.nodes()]
    sizes = [300] * G.number_of_nodes()
    
    if ego_node in G.nodes():
        ego_idx = list(G.nodes()).index(ego_node)
        colors[ego_idx] = -2 
        sizes[ego_idx] = 600
    
    fig, ax = plt.subplots(figsize=(18, 18)) if ax is None else (ax.figure, ax)

    if comunidades:
        cmap = plt.cm.jet
        norm = plt.Normalize(vmin=min(cor_map.values()), vmax=max(cor_map.values()))

        for i, community in enumerate(comunidades):
            points = np.array([pos[node] for node in community if node in pos])
            if len(points) < 3:
                continue
            hull = ConvexHull(points)
            polygon = Polygon(points[hull.vertices, :], facecolor=cmap(norm(i)), alpha=0.15, edgecolor="none")
            ax.add_patch(polygon)
    
    nx.draw(
        G, pos, ax=ax, with_labels=True, node_size=sizes, node_color=colors,
        cmap=plt.cm.jet, edge_color="lightgray", font_size=8, width=0.5
    )
    
    ax.set_title(f"Visualização da Rede Social - Ego Node {ego_node}", fontsize=20)

    if show:
        plt.show()
    return fig