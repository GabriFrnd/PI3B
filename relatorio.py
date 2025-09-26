import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt

def salvar_grafo_png(G, ego_node, comunidades, desenhar_grafo_func, pasta="docs/imagens"):
    """Gera e salva o grafo como imagem PNG sem abrir janela."""
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    path_img = os.path.join(pasta, f"ego_{ego_node}.png")
    fig = desenhar_grafo_func(G, comunidades=comunidades, ego_node=ego_node, show=False)
    fig.savefig(path_img, format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    return path_img

def gerar_relatorio_pdf(relatorio_nome, resultados):
    """
    resultados = [
        {
            "ego": 0,
            "num_vertices": 100,
            "num_arestas": 500,
            "centralidade": {...},
            "pagerank": {...},
            "imagem": "imagens/ego_0.png"
        },
        ...
    ]
    """
    doc = SimpleDocTemplate(relatorio_nome, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    for r in resultados:
        elementos.append(Paragraph(f"<b>Ego Node {r['ego']}</b>", styles["Heading1"]))
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph(f"Número de vértices: {r['num_vertices']}", styles["Normal"]))
        elementos.append(Paragraph(f"Número de arestas: {r['num_arestas']}", styles["Normal"]))
        elementos.append(Spacer(1, 12))

        # adiciona imagem
        elementos.append(Image(r["imagem"], width=400, height=400))
        elementos.append(Spacer(1, 24))

    doc.build(elementos)
    print(f"Relatório salvo em {relatorio_nome}")
