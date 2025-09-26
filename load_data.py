import networkx as nx
import os

def load_data(data_dir, ego_node_id):
    """
    Carrega os dados de uma única rede de ego do dataset do Facebook.

    Args:
        data_dir (str): O caminho para a pasta 'facebook' que contém os arquivos.
        ego_node_id (int): O ID do nó central (ego) da rede a ser carregada.

    Returns:
        tuple: Contendo o grafo (G_nx), as features dos nós (node_features),
               os círculos (circles) e o ID do ego_node.
    """
    
    # --- EXPLICAÇÃO DOS ARQUIVOS ---
    #
    # Cada ego-network é definida por um conjunto de arquivos com o mesmo ID:
    #
    # 1. {ego_node_id}.edges
    #    - O que é: A lista de arestas (conexões de amizade).
    #    - Formato: Cada linha contém "nó1 nó2", indicando que há uma amizade entre eles.
    #    - Propósito: Define a estrutura do grafo, quem está conectado com quem.
    #
    # 2. {ego_node_id}.circles
    #    - O que é: As listas de amigos (círculos) criadas pelo usuário "ego".
    #    - Formato: Cada linha começa com "circle_ID" seguido pelos IDs dos nós nesse círculo.
    #    - Propósito: Define as comunidades (ground truth), que usamos para colorir o grafo.
    #
    # 3. {ego_node_id}.feat
    #    - O que é: As características (features) dos amigos do nó "ego".
    #    - Formato: Cada linha tem um "node_ID" seguido por uma série de 0s e 1s (vetor binário).
    #    - Propósito: Descreve os atributos de cada nó (ex: faculdade, cidade, etc.).
    #
    # 4. {ego_node_id}.featnames
    #    - O que é: O nome de cada característica no arquivo .feat.
    #    - Formato: Cada linha descreve uma feature (ex: "gender;male", "education;school").
    #    - Propósito: Dá significado ao vetor de 0s e 1s do arquivo .feat.
    #
    # 5. {ego_node_id}.egofeat
    #    - O que é: As características do próprio nó "ego".
    #    - Formato: Uma única linha com o vetor de 0s e 1s, no mesmo formato do .feat.
    #    - Propósito: Descreve os atributos do nó central da rede.
    # ------------------------------------

    # Monta os caminhos para os arquivos
    edges_file = os.path.join(data_dir, f"{ego_node_id}.edges")
    circles_file = os.path.join(data_dir, f"{ego_node_id}.circles")
    feat_file = os.path.join(data_dir, f"{ego_node_id}.feat")
    featnames_file = os.path.join(data_dir, f"{ego_node_id}.featnames")
    egofeat_file = os.path.join(data_dir, f"{ego_node_id}.egofeat")

    # 1. Carrega as arestas para construir o grafo
    # O nó "ego" é adicionado primeiro para garantir que ele exista no grafo,
    # mesmo que o arquivo .edges não o inclua explicitamente em uma aresta.
    G_nx = nx.Graph()
    G_nx.add_node(ego_node_id)
    G_nx.add_edges_from(nx.read_edgelist(edges_file, nodetype=int).edges())

    # 2. Carrega os nomes das features para usar como chave do dicionário
    # Ex: 'gender;female', 'locale;pt_BR'
    featnames_raw = [line.strip() for line in open(featnames_file)]

    # 3. Carrega as features dos amigos (alters)
    node_features = {}
    for line in open(feat_file):
        parts = line.strip().split()
        node_id = int(parts[0])
        features_vec = list(map(int, parts[1:]))
        # Cria um dicionário legível para as features de cada nó
        node_features[node_id] = {name: val for name, val in zip(featnames_raw, features_vec)}

    # 4. Carrega as features do nó ego e adiciona ao dicionário
    ego_features_vec = list(map(int, open(egofeat_file).readline().strip().split()))
    node_features[ego_node_id] = {name: val for name, val in zip(featnames_raw, ego_features_vec)}

    # 5. Carrega os círculos (comunidades)
    circles = []
    with open(circles_file) as f:
        for line in f:
            parts = line.strip().split()
            # O primeiro elemento é o nome do círculo, o resto são os membros
            circles.append(set(map(int, parts[1:])))

    return G_nx, node_features, circles