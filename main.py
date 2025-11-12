import os
from graph import GrafoDenso
from visualization import desenhar_grafo
from load_data import load_data
from relatorio import salvar_grafo_png, gerar_relatorio_pdf
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score
from analysis import (
    analisar_sobreposicao_de_circulos,
    comparar_sobreposicao_verdadeiro_vs_detectado
)
# NOVA IMPORTAÇÃO
from export_csv import exportar_todos_csvs


def communities_to_labels(communities, all_nodes):
    """Converte uma lista de conjuntos de comunidades em um vetor de rótulos."""
    node_to_label = {}
    for i, community in enumerate(communities):
        for node in community:
            node_to_label[node] = i
    return [node_to_label.get(node, -1) for node in all_nodes]


EGO_NODES = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]

script_dir = os.path.dirname(__file__)
facebook_dir = os.path.join(script_dir, "facebook")

resultados = []

for ego_node_id in EGO_NODES:
    print(f"  Analisando a Rede do Ego Node: {ego_node_id}")
    print(f"{'='*60}")

    # Carregar os dados
    try:
        G_nx, node_features, circles = load_data(facebook_dir, ego_node_id)
    except FileNotFoundError:
        print(f"AVISO: Arquivos para o ego_node {ego_node_id} não encontrados. Pulando.")
        continue

    # Criar o grafo denso
    vertices = list(G_nx.nodes())
    arestas = list(G_nx.edges())
    grafo = GrafoDenso(vertices, arestas=arestas, features=node_features, circles=circles)

    all_nodes = list(G_nx.nodes())
    true_labels = communities_to_labels(circles, all_nodes)
    
    nome_sobreposicao, comunidades_sobreposicao, mod_sobreposicao = grafo.detectar_comunidades_sobrepostas(ego_node=ego_node_id)
    
    pred_labels_sobreposicao = communities_to_labels(
        grafo._converter_comunidades_para_particao(comunidades_sobreposicao), 
        all_nodes
    )
    nmi_sobreposicao = normalized_mutual_info_score(true_labels, pred_labels_sobreposicao)
    ari_sobreposicao = adjusted_rand_score(true_labels, pred_labels_sobreposicao)

    # Calcula sobreposição real das comunidades detectadas
    total_memberships = sum(len(com) for com in comunidades_sobreposicao)
    unique_nodes = len(set().union(*comunidades_sobreposicao)) if comunidades_sobreposicao else 0
    sobreposicao_detectado = (total_memberships - unique_nodes) / unique_nodes * 100 if unique_nodes > 0 else 0

    
    nome_particao, comunidades_particao, mod_particao = grafo.detectar_comunidades_hibrido(ego_node=ego_node_id)
    
    pred_labels_particao = communities_to_labels(comunidades_particao, all_nodes)
    nmi_particao = normalized_mutual_info_score(true_labels, pred_labels_particao)
    ari_particao = adjusted_rand_score(true_labels, pred_labels_particao)
    
    # Escolhe baseado no NMI
    if nmi_sobreposicao > nmi_particao:
        nome_melhor = nome_sobreposicao
        comunidades_melhor = comunidades_sobreposicao
        mod_melhor = mod_sobreposicao
        nmi_melhor = nmi_sobreposicao
        ari_melhor = ari_sobreposicao
        tipo_algoritmo = "sobreposicao"
    else:
        nome_melhor = nome_particao
        comunidades_melhor = comunidades_particao
        mod_melhor = mod_particao
        nmi_melhor = nmi_particao
        ari_melhor = ari_particao
        tipo_algoritmo = "partição"
    
    if tipo_algoritmo == "sobreposicao":
        comunidades_para_analise = grafo._converter_comunidades_para_particao(comunidades_melhor)
    else:
        comunidades_para_analise = comunidades_melhor

    
    if tipo_algoritmo == "sobreposicao":
        comparar_sobreposicao_verdadeiro_vs_detectado(circles, comunidades_melhor)
    
    sobreposicao_info = analisar_sobreposicao_de_circulos(circles)

    if tipo_algoritmo == "sobreposicao":
        comunidades_para_vis = grafo._converter_comunidades_para_particao(comunidades_melhor)
    else:
        comunidades_para_vis = comunidades_melhor
    
    img_path = salvar_grafo_png(G_nx, ego_node_id, comunidades_para_vis, desenhar_grafo)
    coef_cluster_medio = grafo.coeficiente_de_clusterizacao_medio()

    # Salva resultados
    resultados.append({
        "ego": ego_node_id,
        "num_vertices": grafo.numero_de_vertices(),
        "num_arestas": grafo.numero_de_arestas(),
        "coef_cluster_medio": coef_cluster_medio,
        "algoritmo_usado": nome_melhor,
        "tipo_algoritmo": tipo_algoritmo,
        "num_comunidades_real": len(circles),
        "num_comunidades_detectadas": len(comunidades_melhor),
        "modularidade": mod_melhor,
        "nmi": nmi_melhor,
        "ari": ari_melhor,
        "sobreposicao_percentage": sobreposicao_info['porcentagem_sobreposicao'],
        "sobreposicao_detectado": sobreposicao_detectado if tipo_algoritmo == "sobreposicao" else 0.0,
        "centralidade": grafo.centralidade_grau(),
        "pagerank": grafo.pagerank(),
        "imagem": img_path
    })

exportar_todos_csvs(resultados, output_dir="resultados_csv")

gerar_relatorio_pdf("relatorio_facebook.pdf", resultados)

for r in resultados:
    tipo = r.get('tipo_algoritmo', 'partição')[:9]
    print(f"{r['ego']:<6} {r['num_vertices']:<5} {r['num_arestas']:<6} "
          f"{r['algoritmo_usado']:<20} {tipo:<10} {r['nmi']:<7.4f} {r['ari']:<7.4f} "
          f"{r['modularidade']:<7.4f}")

# Calcula médias
if resultados:
    nmi_medio = sum(r['nmi'] for r in resultados) / len(resultados)
    ari_medio = sum(r['ari'] for r in resultados) / len(resultados)
    mod_medio = sum(r['modularidade'] for r in resultados) / len(resultados)