import os
from graph import GrafoDenso
from visualization import desenhar_grafo
from load_data import load_data
from relatorio import salvar_grafo_png, gerar_relatorio_pdf
from teste_gn import girvan_newman_pure_python
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score


# ===========================================================
# Funções auxiliares
# ===========================================================

def nx_to_dict_graph(G):
    """Converte um grafo NetworkX em um dicionário {nó: {vizinhos}}"""
    return {node: set(G.neighbors(node)) for node in G.nodes()}


def communities_to_labels(communities, all_nodes):
    """
    Converte uma lista de conjuntos de comunidades em um vetor de rótulos.
    Exemplo:
      comunidades = [{1,2}, {3,4}] -> [0,0,1,1]
    """
    node_to_label = {}
    for i, community in enumerate(communities):
        for node in community:
            node_to_label[node] = i
    # Retorna uma lista de rótulos na ordem de all_nodes
    return [node_to_label.get(node, -1) for node in all_nodes]


# ===========================================================
# Configurações iniciais
# ===========================================================

EGO_NODES = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]

script_dir = os.path.dirname(__file__)
facebook_dir = os.path.join(script_dir, "facebook")

resultados = []

# ===========================================================
# Loop principal para cada ego network
# ===========================================================

for ego_node_id in EGO_NODES:
    print(f"\n=================================================")
    print(f"  Analisando a Rede do Ego Node: {ego_node_id}")
    print(f"=================================================")

    # Carregar os dados para o ego_node atual
    try:
        G_nx, node_features, circles = load_data(facebook_dir, ego_node_id)
    except FileNotFoundError:
        print(f"AVISO: Arquivos para o ego_node {ego_node_id} não encontrados. Pulando.")
        continue

    # Criar o grafo denso (estrutura própria)
    vertices = list(G_nx.nodes())
    arestas = list(G_nx.edges())
    grafo = GrafoDenso(vertices, arestas=arestas, features=node_features, circles=circles)

    # Converter grafo para o formato esperado pelo Girvan–Newman
    graph_dict = nx_to_dict_graph(G_nx)

    print("Executando o algoritmo Girvan–Newman (isso pode ser lento)...")
    detected_communities, mod = girvan_newman_pure_python(graph_dict)

    # Converter as comunidades verdadeiras e detectadas em vetores de rótulos
    all_nodes = list(G_nx.nodes())
    true_labels = communities_to_labels(circles, all_nodes)
    pred_labels = communities_to_labels(detected_communities, all_nodes)

    # Calcular métricas de similaridade entre partições
    nmi = normalized_mutual_info_score(true_labels, pred_labels)
    ari = adjusted_rand_score(true_labels, pred_labels)

    # Gerar imagem e métricas adicionais
    img_path = salvar_grafo_png(G_nx, ego_node_id, circles, desenhar_grafo)
    coef_cluster_medio = grafo.coeficiente_de_clusterizacao_medio()

    # Exibir resultados no terminal
    print(f"Coeficiente de Clusterização Médio: {coef_cluster_medio:.4f}")
    print(f"Modularidade Girvan–Newman: {mod:.4f}")
    print(f"NMI (acurácia da comunidade): {nmi:.4f}")
    print(f"ARI (similaridade ajustada): {ari:.4f}")

    # Salvar resultados para o relatório
    resultados.append({
        "ego": ego_node_id,
        "num_vertices": grafo.numero_de_vertices(),
        "num_arestas": grafo.numero_de_arestas(),
        "coef_cluster_medio": coef_cluster_medio,
        "modularidade": mod,
        "nmi": nmi,
        "ari": ari,
        "centralidade": grafo.centralidade_grau(),
        "pagerank": grafo.pagerank(),
        "imagem": img_path
    })


# ===========================================================
# Gerar relatório final
# ===========================================================

gerar_relatorio_pdf("relatorio_facebook.pdf", resultados)
print("\n✅ Relatório gerado: relatorio_facebook.pdf")
