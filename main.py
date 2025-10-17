import os
from graph import GrafoDenso
from visualization import desenhar_grafo
from load_data import load_data
from relatorio import salvar_grafo_png, gerar_relatorio_pdf

EGO_NODES = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]

script_dir = os.path.dirname(__file__)
facebook_dir = os.path.join(script_dir, "facebook")

resultados = []

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

    vertices = list(G_nx.nodes())
    arestas = list(G_nx.edges())
    grafo = GrafoDenso(vertices, arestas=arestas, features=node_features, circles=circles)

    img_path = salvar_grafo_png(G_nx, ego_node_id, circles, desenhar_grafo)

    # Calcular o coeficiente médio para toda a rede
    coef_cluster_medio = grafo.coeficiente_de_clusterizacao_medio()

    print(f"Coeficiente de Clusterização Médio: {coef_cluster_medio:.4f}")

    resultados.append({
        "ego": ego_node_id,
        "num_vertices": grafo.numero_de_vertices(),
        "num_arestas": grafo.numero_de_arestas(),
        "centralidade": grafo.centralidade_grau(),
        "pagerank": grafo.pagerank(),
        "imagem": img_path,
        "coef_cluster_medio": coef_cluster_medio
    })

gerar_relatorio_pdf("relatorio_facebook.pdf", resultados)