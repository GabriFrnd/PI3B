import collections
import copy
from itertools import combinations

# ==============================================================================
# FUNÇÕES DO ALGORITMO GIRVAN-NEWMAN (AS MESMAS DA RESPOSTA ANTERIOR)
# ==============================================================================

def calculate_modularity(original_graph, communities):
    num_nodes = len(original_graph)
    if num_nodes == 0: return 0.0
    num_edges = 0
    degrees = collections.defaultdict(int)
    for node, neighbors in original_graph.items():
        degrees[node] = len(neighbors)
        num_edges += len(neighbors)
    num_edges /= 2
    if num_edges == 0: return 0.0
    modularity = 0.0
    for community in communities:
        sum_degrees_in_community = sum(degrees[node] for node in community)
        edges_in_community = 0
        for node in community:
            for neighbor in original_graph.get(node, set()):
                if neighbor in community:
                    edges_in_community += 1
        edges_in_community /= 2
        term1 = edges_in_community / num_edges
        term2 = (sum_degrees_in_community / (2 * num_edges)) ** 2
        modularity += (term1 - term2)
    return modularity

def get_connected_components(graph):
    visited = set()
    components = []
    for node in graph:
        if node not in visited:
            component = set()
            queue = collections.deque([node])
            visited.add(node)
            while queue:
                current = queue.popleft()
                component.add(current)
                for neighbor in graph.get(current, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
    return components

def edge_betweenness_centrality(graph):
    if not graph: return {}
    betweenness = collections.defaultdict(float)
    nodes = list(graph.keys())
    for s in nodes:
        predecessors = collections.defaultdict(list)
        num_shortest_paths = collections.defaultdict(int)
        num_shortest_paths[s] = 1
        distance = {node: -1 for node in nodes}
        distance[s] = 0
        queue = collections.deque([s])
        stack = []
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in graph.get(v, set()):
                if distance[w] < 0:
                    distance[w] = distance[v] + 1
                    queue.append(w)
                if distance[w] == distance[v] + 1:
                    num_shortest_paths[w] += num_shortest_paths[v]
                    predecessors[w].append(v)
        dependency = collections.defaultdict(float)
        while stack:
            w = stack.pop()
            for v in predecessors[w]:
                credit = (num_shortest_paths[v] / num_shortest_paths[w]) * (1 + dependency[w])
                edge = tuple(sorted((v, w)))
                betweenness[edge] += credit
                dependency[v] += credit
    for edge in betweenness:
        betweenness[edge] /= 2.0
    return betweenness

def girvan_newman_pure_python(graph):
    if not graph: return [], 0.0
    g_copy = copy.deepcopy(graph)
    initial_components = get_connected_components(g_copy)
    best_partition = initial_components
    best_modularity = calculate_modularity(graph, initial_components)
    while len(g_copy) > 0:
        betweenness = edge_betweenness_centrality(g_copy)
        if not betweenness: break
        edge_to_remove = max(betweenness, key=betweenness.get)
        u, v = edge_to_remove
        if u in g_copy and v in g_copy[u]: g_copy[u].remove(v)
        if v in g_copy and u in g_copy[v]: g_copy[v].remove(u)
        if u in g_copy and not g_copy[u]: del g_copy[u]
        if v in g_copy and not g_copy[v]: del g_copy[v]
        current_partition = get_connected_components(g_copy)
        current_modularity = calculate_modularity(graph, current_partition)
        if current_modularity > best_modularity:
            best_modularity = current_modularity
            best_partition = current_partition
    return best_partition, best_modularity

# ==============================================================================
# NOVA PARTE: CONSTRUÇÃO DO GRAFO A PARTIR DO SEU DATASET
# ==============================================================================

def build_graph_from_circles(data_string):
    """
    Constrói um grafo a partir de uma string de dados de círculos.
    Assume que todos os nós em um círculo formam um clique.
    """
    graph = collections.defaultdict(set)
    lines = data_string.strip().split('\n')

    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            continue
        
        # Converte os nós de string para inteiro
        nodes_in_circle = [int(p) for p in parts[1:]]

        # Adiciona arestas entre todos os pares de nós no círculo
        for u, v in combinations(nodes_in_circle, 2):
            graph[u].add(v)
            graph[v].add(u)
            
    # Garante que todos os nós mencionados (mesmo os de círculos unitários) existam no grafo
    all_nodes = set()
    for line in lines:
        parts = line.split()
        all_nodes.update(int(p) for p in parts[1:])
    for node in all_nodes:
        if node not in graph:
            graph[node] = set()

    return dict(graph)

# --- Exemplo de Uso com o seu Dataset ---
if __name__ == '__main__':
    # Cole o seu dataset aqui
    dataset_string = """
    circle0	71	215	54	61	298	229	81	253	193	97	264	29	132	110	163	259	183	334	245	222
    circle1	173
    circle2	155	99	327	140	116	147	144	150	270
    circle3	51	83	237
    circle4	125	344	295	257	55	122	223	59	268	280	84	156	258	236	250	239	69
    circle5	23
    circle6	337	289	93	17	111	52	137	343	192	35	326	310	214	32	115	321	209	312	41	20
    circle7	225	46
    circle8	282
    circle9	336	204	74	206	292	146	154	164	279	73
    circle10	42	14	216	2
    circle11	324	265	54	161	298	76	165	199	203	13	66	113	97	252	313	238	158	240	331	332	134	218	118	235	311	151	308	212	70	211
    circle12	278
    circle13	138	131	68	143	86
    circle14	175	227
    circle15	108	208	251	125	325	176	133	276	198	271	288	316	96	246	347	121	7	3	170	323	56	338	23	109	141	67	345	55	114	122	50	304	318	65	15	45	317	322	26	31	168	124	285	255	129	40	172	274	95	207	128	339	233	1	294	280	224	269	256	60	328	189	146	77	196	64	286	89	22	39	190	281	117	38	213	135	197	291	21	315	261	47	36	186	169	342	49	9	16	185	219	123	72	309	103	157	277	105	139	148	248	341	62	98	63	297	242	10	152	236	308	82	87	136	200	183	247	290	303	319	6	314	104	127	25	69	171	119	79	340	301	188	142
    circle16	251	94	330	5	34	299	254	24	180	194	281	101	266	135	197	173	36	9	85	57	37	258	309	80	139	202	187	249	58	127	48	92
    circle17	90	52	172	126	294	179	145	105	210
    circle18	177
    circle19	93	33	333	17	137	44	343	326	214	115	312	41	20
    circle20	244	282	262	293	220	174
    circle21	12
    circle22	267
    circle23	28	149	162
    """
    
    print("Construindo o grafo a partir do dataset...")
    social_graph = build_graph_from_circles(dataset_string)
    
    num_nodes = len(social_graph)
    num_edges = sum(len(neighbors) for neighbors in social_graph.values()) // 2
    print(f"Grafo construído com {num_nodes} nós e {num_edges} arestas.")
    print("\nAVISO: A execução a seguir pode ser EXTREMAMENTE LENTA devido ao tamanho do grafo.\n")

    print("Executando o algoritmo Girvan-Newman...")
    communities, mod = girvan_newman_pure_python(social_graph)

    print(f"\nMelhor modularidade encontrada: {mod:.4f}")
    print(f"Número de comunidades detectadas: {len(communities)}")
    print("\nComunidades:")
    sorted_communities = sorted([sorted(list(c)) for c in communities])
    for i, community in enumerate(sorted_communities):
        print(f"  Comunidade {i+1}: {community}")