def analisar_sobreposicao_de_circulos(circles):
    """
    Analisa o quanto os círculos verdadeiros se sobrepõem.
    Isso explica por que algoritmos de partição têm dificuldade.
    """
    total_nodes = set()
    for circle in circles:
        total_nodes.update(circle)
    
    # Conta quantos círculos cada nó pertence
    node_membership = {node: 0 for node in total_nodes}
    for circle in circles:
        for node in circle:
            node_membership[node] += 1
    
    # Estatísticas
    memberships = list(node_membership.values())
    nodes_em_multiplos = sum(1 for m in memberships if m > 1)
    max_membership = max(memberships) if memberships else 0
    avg_membership = sum(memberships) / len(memberships) if memberships else 0
    
    return {
        "total_nodes": len(total_nodes),
        "nodes_em_multiplos_circulos": nodes_em_multiplos,
        "porcentagem_sobreposicao": 100 * nodes_em_multiplos / len(total_nodes) if total_nodes else 0,
        "max_circulos_por_no": max_membership,
        "media_circulos_por_no": avg_membership
    }


def analisar_tamanho_das_comunidades(communities):
    """Analisa a distribuição de tamanhos das comunidades."""
    tamanhos = sorted([len(c) for c in communities], reverse=True)
    
    return {
        "num_comunidades": len(communities),
        "tamanhos": tamanhos,
        "maior_comunidade": tamanhos[0] if tamanhos else 0,
        "menor_comunidade": tamanhos[-1] if tamanhos else 0,
        "tamanho_medio": sum(tamanhos) / len(tamanhos) if tamanhos else 0
    }


def calcular_jaccard_entre_particoes(true_communities, detected_communities):
    """
    Calcula a similaridade de Jaccard média entre as melhores correspondências
    de comunidades verdadeiras e detectadas.
    """
    def jaccard(set1, set2):
        if not set1 and not set2:
            return 1.0
        intersecao = len(set1 & set2)
        uniao = len(set1 | set2)
        return intersecao / uniao if uniao > 0 else 0.0
    
    # Para cada comunidade verdadeira, encontra a detectada mais similar
    jaccards = []
    for true_com in true_communities:
        melhor_jaccard = 0.0
        for det_com in detected_communities:
            j = jaccard(true_com, det_com)
            melhor_jaccard = max(melhor_jaccard, j)
        jaccards.append(melhor_jaccard)
    
    return {
        "jaccard_medio": sum(jaccards) / len(jaccards) if jaccards else 0.0,
        "jaccards_individuais": jaccards,
        "num_circulos_bem_detectados": sum(1 for j in jaccards if j > 0.5)
    }


def gerar_relatorio_detalhado(ego_node_id, circles, detected_communities, 
                               nmi, ari, modularidade):
    """
    Gera um relatório textual detalhado sobre a qualidade da detecção.
    """
    print(f"\n{'='*60}")
    print(f"  ANÁLISE DETALHADA - Ego Node {ego_node_id}")
    print(f"{'='*60}")
    
    # Análise de sobreposição
    sobreposicao_info = analisar_sobreposicao_de_circulos(circles)
    print(f"\n📊 Sobreposição dos Círculos Verdadeiros:")
    print(f"  • Total de nós: {sobreposicao_info['total_nodes']}")
    print(f"  • Nós em múltiplos círculos: {sobreposicao_info['nodes_em_multiplos_circulos']} "
          f"({sobreposicao_info['porcentagem_sobreposicao']:.1f}%)")
    print(f"  • Máx. círculos por nó: {sobreposicao_info['max_circulos_por_no']}")
    print(f"  • Média círculos por nó: {sobreposicao_info['media_circulos_por_no']:.2f}")
    
    if sobreposicao_info['porcentagem_sobreposicao'] > 30:
        print(f"  ⚠️  Alta sobreposição! Algoritmos de partição terão dificuldade.")
    
    # Análise de tamanhos
    print(f"\n📏 Tamanho dos Círculos Verdadeiros:")
    true_info = analisar_tamanho_das_comunidades(circles)
    print(f"  • Número de círculos: {true_info['num_comunidades']}")
    print(f"  • Maior: {true_info['maior_comunidade']} nós")
    print(f"  • Menor: {true_info['menor_comunidade']} nós")
    print(f"  • Média: {true_info['tamanho_medio']:.1f} nós")
    
    print(f"\n📏 Tamanho das Comunidades Detectadas:")
    det_info = analisar_tamanho_das_comunidades(detected_communities)
    print(f"  • Número de comunidades: {det_info['num_comunidades']}")
    print(f"  • Maior: {det_info['maior_comunidade']} nós")
    print(f"  • Menor: {det_info['menor_comunidade']} nós")
    print(f"  • Média: {det_info['tamanho_medio']:.1f} nós")
    
    # Similaridade Jaccard
    jaccard_info = calcular_jaccard_entre_particoes(circles, detected_communities)
    print(f"\n🎯 Similaridade das Comunidades:")
    print(f"  • Jaccard médio: {jaccard_info['jaccard_medio']:.4f}")
    print(f"  • Círculos bem detectados (J>0.5): {jaccard_info['num_circulos_bem_detectados']}/{len(circles)}")
    
    # Métricas finais
    print(f"\n📈 Métricas de Avaliação:")
    print(f"  • NMI (Normalized Mutual Information): {nmi:.4f}")
    print(f"  • ARI (Adjusted Rand Index): {ari:.4f}")
    print(f"  • Modularidade: {modularidade:.4f}")
    
    # Interpretação
    print(f"\n💡 Interpretação:")
    if nmi > 0.5:
        print(f"  ✅ NMI > 0.5: Excelente detecção de comunidades!")
    elif nmi > 0.4:
        print(f"  ✓ NMI > 0.4: Boa detecção de comunidades")
    elif nmi > 0.3:
        print(f"  ~ NMI > 0.3: Detecção razoável")
    else:
        print(f"  ⚠️  NMI < 0.3: Detecção precisa melhorar")
    
    if modularidade > 0.4:
        print(f"  ✅ Modularidade > 0.4: Estrutura de comunidades forte")
    elif modularidade > 0.3:
        print(f"  ✓ Modularidade > 0.3: Estrutura de comunidades clara")
    else:
        print(f"  ~ Modularidade < 0.3: Estrutura de comunidades fraca")
    
    print(f"\n{'='*60}\n")


def analisar_comunidades_sobrepostas(comunidades_detectadas):
    """
    Analisa comunidades sobrepostas detectadas por algoritmos como SLPA ou DEMON.
    """
    # Conta quantos nós estão em múltiplas comunidades
    node_membership = {}
    for com in comunidades_detectadas:
        for node in com:
            node_membership[node] = node_membership.get(node, 0) + 1
    
    if not node_membership:
        return {
            "total_nodes": 0,
            "nodes_em_multiplas": 0,
            "porcentagem_sobreposicao": 0.0,
            "max_membership": 0,
            "avg_membership": 0.0
        }
    
    memberships = list(node_membership.values())
    nodes_em_multiplas = sum(1 for m in memberships if m > 1)
    
    return {
        "total_nodes": len(node_membership),
        "nodes_em_multiplas": nodes_em_multiplas,
        "porcentagem_sobreposicao": 100 * nodes_em_multiplas / len(node_membership),
        "max_membership": max(memberships),
        "avg_membership": sum(memberships) / len(memberships)
    }


def comparar_sobreposicao_verdadeiro_vs_detectado(circles, comunidades_detectadas):
    """
    Compara a sobreposição dos círculos verdadeiros vs comunidades detectadas.
    """
    sobreposicao_verdadeiro = analisar_sobreposicao_de_circulos(circles)
    sobreposicao_detectado = analisar_comunidades_sobrepostas(comunidades_detectadas)
    
    print(f"\n🔍 Comparação de Sobreposição:")
    print(f"  Círculos verdadeiros:")
    print(f"    • {sobreposicao_verdadeiro['porcentagem_sobreposicao']:.1f}% dos nós em múltiplos círculos")
    print(f"    • Média de {sobreposicao_verdadeiro['media_circulos_por_no']:.2f} círculos por nó")
    
    print(f"  Comunidades detectadas:")
    print(f"    • {sobreposicao_detectado['porcentagem_sobreposicao']:.1f}% dos nós em múltiplas comunidades")
    print(f"    • Média de {sobreposicao_detectado['avg_membership']:.2f} comunidades por nó")
    
    # Avalia quão bem o algoritmo capturou a sobreposição
    diff_percentage = abs(sobreposicao_verdadeiro['porcentagem_sobreposicao'] - sobreposicao_detectado['porcentagem_sobreposicao'])
    
    if diff_percentage < 10:
        print(f"  ✅ Excelente captura da sobreposição (diferença de {diff_percentage:.1f}%)")
    elif diff_percentage < 20:
        print(f"  ✓ Boa captura da sobreposição (diferença de {diff_percentage:.1f}%)")
    else:
        print(f"  ⚠️  Sobreposição capturada difere significativamente (diferença de {diff_percentage:.1f}%)")
    
    return sobreposicao_verdadeiro, sobreposicao_detectado