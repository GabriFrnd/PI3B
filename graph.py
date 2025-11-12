from abc import ABC, abstractmethod
from collections import deque, defaultdict
import copy
import itertools

class Grafo(ABC):
    @abstractmethod
    def numero_de_vertices(self):
        pass

    @abstractmethod
    def numero_de_arestas(self):
        pass

    @abstractmethod
    def sequencia_de_graus(self):
        pass

    @abstractmethod
    def adicionar_aresta(self, u, v):
        pass

    @abstractmethod
    def remover_aresta(self, u, v):
        pass

class GrafoDenso(Grafo):
    def __init__(self, vertices, arestas=None, features=None, circles=None):
        self.vertices = vertices
        self.n = len(vertices)
        self.vertices.sort()
        self.mapa_indices = {vertice: i for i, vertice in enumerate(self.vertices)}
        self.matriz = [[0]*self.n for _ in range(self.n)]
        self.features = features or {}
        self.circles = circles or []
        if arestas:
            for u, v in arestas:
                self.adicionar_aresta(u, v)

    def _indice(self, vertice):
        return self.mapa_indices[vertice]

    def numero_de_vertices(self):
        return self.n

    def numero_de_arestas(self):
        count = 0
        for i in range(self.n):
            for j in range(i+1, self.n):
                count += self.matriz[i][j]
        return count

    def sequencia_de_graus(self):
        return [sum(self.matriz[i]) for i in range(self.n)]

    def adicionar_aresta(self, u, v):
        i, j = self._indice(u), self._indice(v)
        self.matriz[i][j] = 1
        self.matriz[j][i] = 1

    def remover_aresta(self, u, v):
        i, j = self._indice(u), self._indice(v)
        if i is not None and j is not None:
            self.matriz[i][j] = 0
            self.matriz[j][i] = 0

    def centralidade_grau(self):
        graus = self.sequencia_de_graus()
        return {self.vertices[i]: graus[i] for i in range(self.n)}

    def _bfs_distancias(self, start_idx):
        dist = {self.vertices[start_idx]: 0}
        fila = deque([start_idx])
        while fila:
            u = fila.popleft()
            for j in range(self.n):
                if self.matriz[u][j] == 1 and self.vertices[j] not in dist:
                    dist[self.vertices[j]] = dist[self.vertices[u]] + 1
                    fila.append(j)
        return dist

    def centralidade_proximidade(self):
        proximidade = {}
        for i, v in enumerate(self.vertices):
            distancias = self._bfs_distancias(i)
            soma = sum(distancias.values())
            proximidade[v] = (len(distancias)-1)/soma if soma > 0 else 0
        return proximidade

    def centralidade_intermediacao(self):
        betweenness = {v:0 for v in self.vertices}
        for s in range(self.n):
            stack = []; pred = {v:[] for v in self.vertices}
            sigma = dict.fromkeys(self.vertices, 0); sigma[self.vertices[s]] = 1
            dist = dict.fromkeys(self.vertices, -1); dist[self.vertices[s]] = 0
            Q = deque([self.vertices[s]])
            while Q:
                v = Q.popleft(); stack.append(v)
                v_idx = self._indice(v)
                for w_idx in range(self.n):
                    if self.matriz[v_idx][w_idx] == 1:
                        w = self.vertices[w_idx]
                        if dist[w] < 0: Q.append(w); dist[w] = dist[v]+1
                        if dist[w] == dist[v]+1: sigma[w] += sigma[v]; pred[w].append(v)
            delta = dict.fromkeys(self.vertices, 0)
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta_v = (sigma[v]/sigma[w])*(1 + delta[w])
                    delta[v] += delta_v
                if w != self.vertices[s]: betweenness[w] += delta[w]
        return betweenness

    def pagerank(self, d=0.85, max_iter=100, tol=1e-6):
        N = self.n; pr = {v: 1/N for v in self.vertices}
        for _ in range(max_iter):
            novo_pr = {}
            for v in self.vertices:
                rank = (1-d)/N
                for u in self.vertices:
                    i,j = self._indice(u), self._indice(v)
                    if self.matriz[i][j]==1:
                        grau = sum(self.matriz[i])
                        rank += d*(pr[u]/grau if grau>0 else 0)
                novo_pr[v]=rank
            if all(abs(novo_pr[v]-pr[v])<tol for v in self.vertices): break
            pr = novo_pr
        return pr

    def modularidade(self, comunidades):
        """Calcula a modularidade de uma partição de comunidades."""
        m = self.numero_de_arestas()
        if m == 0:
            return 0.0
        
        Q = 0.0
        graus = self.sequencia_de_graus()
        
        for comunidade in comunidades:
            for v in comunidade:
                i = self._indice(v)
                for w in comunidade:
                    j = self._indice(w)
                    if i != j:
                        A_ij = self.matriz[i][j]
                        k_i = graus[i]
                        k_j = graus[j]
                        Q += A_ij - (k_i * k_j) / (2 * m)
        
        Q = Q / (2 * m)
        return Q

    def louvain(self):
        """
        Algoritmo de Louvain para detecção de comunidades.
        Retorna uma lista de conjuntos (comunidades) e a modularidade.
        """
        # Inicialização: cada nó em sua própria comunidade
        comunidade = {v: i for i, v in enumerate(self.vertices)}
        m = self.numero_de_arestas()
        graus = {v: g for v, g in zip(self.vertices, self.sequencia_de_graus())}
        
        melhorou = True
        iteracao = 0
        max_iter = 100
        
        while melhorou and iteracao < max_iter:
            melhorou = False
            iteracao += 1
            
            # Fase 1: Otimização local
            for v in self.vertices:
                melhor_comunidade = comunidade[v]
                melhor_ganho = 0.0
                
                # Comunidades vizinhas
                comunidades_vizinhas = set()
                idx_v = self._indice(v)
                for j in range(self.n):
                    if self.matriz[idx_v][j] == 1:
                        comunidades_vizinhas.add(comunidade[self.vertices[j]])
                
                # Remove v de sua comunidade atual temporariamente
                com_atual = comunidade[v]
                
                # Tenta cada comunidade vizinha
                for com in comunidades_vizinhas:
                    if com == com_atual:
                        continue
                    
                    # Calcula o ganho de modularidade
                    ganho = self._calcular_ganho_modularidade(
                        v, com_atual, com, comunidade, graus, m
                    )
                    
                    if ganho > melhor_ganho:
                        melhor_ganho = ganho
                        melhor_comunidade = com
                
                # Se encontrou uma comunidade melhor, move o nó
                if melhor_comunidade != com_atual and melhor_ganho > 0:
                    comunidade[v] = melhor_comunidade
                    melhorou = True
        
        # Converte o dicionário de comunidades em lista de conjuntos
        comunidades_dict = defaultdict(set)
        for node, com_id in comunidade.items():
            comunidades_dict[com_id].add(node)
        
        comunidades_lista = list(comunidades_dict.values())
        mod = self.modularidade(comunidades_lista)
        
        return comunidades_lista, mod

    def _calcular_ganho_modularidade(self, node, com_from, com_to, comunidade, graus, m):
        """Calcula o ganho de modularidade ao mover um nó entre comunidades."""
        if m == 0:
            return 0.0
        
        idx_node = self._indice(node)
        k_i = graus[node]
        
        # Soma dos graus na comunidade de destino
        sigma_to = sum(graus[v] for v in self.vertices if comunidade[v] == com_to)
        
        # Número de arestas de node para com_to
        k_i_in_to = 0
        for v in self.vertices:
            if comunidade[v] == com_to:
                idx_v = self._indice(v)
                k_i_in_to += self.matriz[idx_node][idx_v]
        
        # Ganho
        ganho = (k_i_in_to / m) - (sigma_to * k_i / (2 * m * m))
        
        return ganho

    def label_propagation(self, max_iter=100):
        """
        Algoritmo de Label Propagation para detecção de comunidades.
        Cada nó adota o label mais comum entre seus vizinhos.
        """
        # Inicialização: cada nó com seu próprio label
        labels = {v: v for v in self.vertices}
        
        for _ in range(max_iter):
            mudou = False
            
            # Processa os nós em ordem aleatória para evitar viés
            import random
            nodes_shuffled = self.vertices.copy()
            random.shuffle(nodes_shuffled)
            
            for v in nodes_shuffled:
                idx_v = self._indice(v)
                
                # Conta os labels dos vizinhos
                label_count = defaultdict(int)
                for j in range(self.n):
                    if self.matriz[idx_v][j] == 1:
                        neighbor = self.vertices[j]
                        label_count[labels[neighbor]] += 1
                
                if not label_count:
                    continue
                
                # Escolhe o label mais frequente
                max_count = max(label_count.values())
                labels_max = [l for l, c in label_count.items() if c == max_count]
                
                # Em caso de empate, escolhe o menor label
                novo_label = min(labels_max)
                
                if novo_label != labels[v]:
                    labels[v] = novo_label
                    mudou = True
            
            if not mudou:
                break
        
        # Converte labels em comunidades
        comunidades_dict = defaultdict(set)
        for node, label in labels.items():
            comunidades_dict[label].add(node)
        
        comunidades_lista = list(comunidades_dict.values())
        mod = self.modularidade(comunidades_lista)
        
        return comunidades_lista, mod

    def girvan_newman(self, num_comunidades=None):
        """
        Versão melhorada do Girvan-Newman que para quando:
        1. Atinge o número desejado de comunidades, OU
        2. A modularidade começa a diminuir
        """
        g = copy.deepcopy(self)
        melhor_particao = None
        melhor_modularidade = -1
        
        historico = []
        
        while True:
            # Calcula comunidades atuais
            comunidades = g._componentes_conexos()
            mod = g.modularidade(comunidades)
            
            historico.append((len(comunidades), mod, [c.copy() for c in comunidades]))
            
            # Atualiza melhor partição
            if mod > melhor_modularidade:
                melhor_modularidade = mod
                melhor_particao = [c.copy() for c in comunidades]
            
            # Critério de parada
            if num_comunidades and len(comunidades) >= num_comunidades:
                break
            
            # Se modularidade está diminuindo, para
            if len(historico) > 3:
                mods_recentes = [h[1] for h in historico[-3:]]
                if all(mods_recentes[i] >= mods_recentes[i+1] for i in range(len(mods_recentes)-1)):
                    break
            
            # Calcula betweenness das arestas
            betweenness = g.centralidade_intermediacao()
            max_bet, aresta_max = 0, None
            
            for i in range(g.n):
                for j in range(i+1, g.n):
                    if g.matriz[i][j] == 1:
                        # Betweenness da aresta = soma dos betweenness dos nós
                        valor = betweenness[g.vertices[i]] + betweenness[g.vertices[j]]
                        if valor > max_bet:
                            max_bet = valor
                            aresta_max = (g.vertices[i], g.vertices[j])
            
            if not aresta_max:
                break
            
            g.remover_aresta(*aresta_max)
        
        return melhor_particao, melhor_modularidade

    def _componentes_conexos(self):
        visitados = set()
        componentes = []
        for v in self.vertices:
            if v not in visitados:
                comp = []
                fila = deque([v])
                while fila:
                    u = fila.popleft()
                    if u not in visitados:
                        visitados.add(u)
                        comp.append(u)
                        idx = self._indice(u)
                        for j in range(self.n):
                            if self.matriz[idx][j]==1:
                                fila.append(self.vertices[j])
                componentes.append(set(comp))
        return componentes
    
    def coeficiente_de_clusterizacao_local(self, vertice):
        """Calcula o coeficiente de clusterização local para um vértice específico."""
        idx = self._indice(vertice)
        vizinhos_indices = []
        for j in range(self.n):
            if self.matriz[idx][j] == 1:
                vizinhos_indices.append(j)
        
        grau = len(vizinhos_indices)
        if grau < 2:
            return 0.0
            
        arestas_entre_vizinhos = 0
        for i in range(len(vizinhos_indices)):
            for j in range(i + 1, len(vizinhos_indices)):
                vizinho1_idx = vizinhos_indices[i]
                vizinho2_idx = vizinhos_indices[j]
                if self.matriz[vizinho1_idx][vizinho2_idx] == 1:
                    arestas_entre_vizinhos += 1
        
        max_arestas_possiveis = grau * (grau - 1) / 2
        return arestas_entre_vizinhos / max_arestas_possiveis
    
    def coeficiente_de_clusterizacao_medio(self):
        """Calcula o coeficiente de clusterização médio do grafo."""
        soma_coeficientes = sum(self.coeficiente_de_clusterizacao_local(v) for v in self.vertices)
        return soma_coeficientes / self.n if self.n > 0 else 0.0

    def k_clique_communities(self, k=3):
        """
        Detecção de comunidades baseada em k-cliques.
        Dois k-cliques estão na mesma comunidade se compartilham k-1 vértices.
        Melhor para detectar comunidades sobrepostas e funciona bem em redes sociais.
        """
        # Encontra todos os k-cliques
        cliques = []
        vertices_set = set(self.vertices)
        
        def encontrar_cliques_de_tamanho_k(vertices_candidatos, clique_atual, inicio):
            if len(clique_atual) == k:
                cliques.append(tuple(sorted(clique_atual)))
                return
            
            for i in range(inicio, len(vertices_candidatos)):
                v = vertices_candidatos[i]
                # Verifica se v é adjacente a todos em clique_atual
                idx_v = self._indice(v)
                eh_adjacente_a_todos = all(
                    self.matriz[idx_v][self._indice(u)] == 1 
                    for u in clique_atual
                )
                
                if eh_adjacente_a_todos:
                    encontrar_cliques_de_tamanho_k(
                        vertices_candidatos, 
                        clique_atual + [v], 
                        i + 1
                    )
        
        # Busca cliques a partir de cada vértice
        for idx_inicio, v_inicio in enumerate(self.vertices):
            vizinhos = [self.vertices[j] for j in range(self.n) 
                       if self.matriz[self._indice(v_inicio)][j] == 1]
            encontrar_cliques_de_tamanho_k(
                [v_inicio] + vizinhos, 
                [], 
                0
            )
        
        # Remove duplicatas
        cliques = list(set(cliques))
        
        if not cliques:
            # Se não encontrou k-cliques, retorna cada componente conexa
            return self._componentes_conexos(), 0.0
        
        # Constrói grafo de cliques (dois cliques são adjacentes se compartilham k-1 vértices)
        n_cliques = len(cliques)
        adj_cliques = [[0] * n_cliques for _ in range(n_cliques)]
        
        for i in range(n_cliques):
            for j in range(i + 1, n_cliques):
                intersecao = set(cliques[i]) & set(cliques[j])
                if len(intersecao) >= k - 1:
                    adj_cliques[i][j] = 1
                    adj_cliques[j][i] = 1
        
        # Encontra componentes conexas no grafo de cliques
        visitados = set()
        comunidades = []
        
        for i in range(n_cliques):
            if i not in visitados:
                comunidade = set()
                fila = deque([i])
                
                while fila:
                    idx = fila.popleft()
                    if idx not in visitados:
                        visitados.add(idx)
                        # Adiciona todos os vértices deste clique à comunidade
                        comunidade.update(cliques[idx])
                        
                        # Adiciona cliques adjacentes à fila
                        for j in range(n_cliques):
                            if adj_cliques[idx][j] == 1 and j not in visitados:
                                fila.append(j)
                
                if comunidade:
                    comunidades.append(comunidade)
        
        # Se algumas comunidades têm muita sobreposição, mescla elas
        comunidades = self._mesclar_comunidades_sobrepostas(comunidades, threshold=0.5)
        
        mod = self.modularidade(comunidades)
        return comunidades, mod

    def _mesclar_comunidades_sobrepostas(self, comunidades, threshold=0.5):
        """Mescla comunidades que têm muita sobreposição."""
        if len(comunidades) <= 1:
            return comunidades
        
        mesclou = True
        while mesclou:
            mesclou = False
            nova_lista = []
            usadas = set()
            
            for i, com1 in enumerate(comunidades):
                if i in usadas:
                    continue
                    
                mesclada = False
                for j in range(i + 1, len(comunidades)):
                    if j in usadas:
                        continue
                    
                    com2 = comunidades[j]
                    intersecao = len(com1 & com2)
                    menor = min(len(com1), len(com2))
                    
                    if menor > 0 and intersecao / menor > threshold:
                        # Mescla as comunidades
                        nova_lista.append(com1 | com2)
                        usadas.add(i)
                        usadas.add(j)
                        mesclada = True
                        mesclou = True
                        break
                
                if not mesclada:
                    nova_lista.append(com1)
                    usadas.add(i)
            
            comunidades = nova_lista
        
        return comunidades

    def infomap(self, num_iter=10):
        """
        Algoritmo Infomap simplificado para detecção de comunidades.
        Baseado na teoria da informação: minimiza o comprimento da descrição
        de um random walk no grafo usando códigos de Huffman.
        """
        # Inicialização: cada nó em sua própria comunidade
        comunidade = {v: i for i, v in enumerate(self.vertices)}
        m = self.numero_de_arestas()
        
        if m == 0:
            return [set(self.vertices)], 0.0
        
        # Calcula probabilidades de transição
        graus = self.sequencia_de_graus()
        
        for _ in range(num_iter):
            melhorou = False
            
            for v in self.vertices:
                idx_v = self._indice(v)
                com_atual = comunidade[v]
                
                # Conta quantos vizinhos estão em cada comunidade
                com_vizinhos = defaultdict(int)
                for j in range(self.n):
                    if self.matriz[idx_v][j] == 1:
                        vizinho = self.vertices[j]
                        com_vizinhos[comunidade[vizinho]] += 1
                
                # Encontra a comunidade com mais conexões
                if com_vizinhos:
                    melhor_com = max(com_vizinhos.items(), key=lambda x: x[1])[0]
                    
                    if melhor_com != com_atual:
                        comunidade[v] = melhor_com
                        melhorou = True
            
            if not melhorou:
                break
        
        # Converte para lista de conjuntos
        comunidades_dict = defaultdict(set)
        for node, com_id in comunidade.items():
            comunidades_dict[com_id].add(node)
        
        comunidades_lista = list(comunidades_dict.values())
        mod = self.modularidade(comunidades_lista)
        
        return comunidades_lista, mod

    def detectar_comunidades_hibrido(self, ego_node=None):
        """
        Abordagem híbrida que combina múltiplos algoritmos e escolhe o melhor resultado.
        Especialmente útil para redes ego do Facebook.
        """
        resultados = []
        
        # 1. Louvain (geralmente o melhor)
        try:
            com_louvain, mod_louvain = self.louvain()
            resultados.append(("Louvain", com_louvain, mod_louvain))
        except:
            pass
        
        # 2. K-Clique (bom para detectar grupos densos)
        try:
            com_kclique, mod_kclique = self.k_clique_communities(k=3)
            resultados.append(("K-Clique (k=3)", com_kclique, mod_kclique))
        except:
            pass
        
        # 3. K-Clique com k=4 (mais restritivo)
        if self.n < 150:  # Só para grafos menores
            try:
                com_kclique4, mod_kclique4 = self.k_clique_communities(k=4)
                resultados.append(("K-Clique (k=4)", com_kclique4, mod_kclique4))
            except:
                pass
        
        # 4. Infomap
        try:
            com_infomap, mod_infomap = self.infomap()
            resultados.append(("Infomap", com_infomap, mod_infomap))
        except:
            pass
        
        # 5. Label Propagation
        try:
            com_lp, mod_lp = self.label_propagation()
            resultados.append(("Label Propagation", com_lp, mod_lp))
        except:
            pass
        
        # Escolhe o resultado com melhor modularidade
        if resultados:
            melhor = max(resultados, key=lambda x: x[2])
            return melhor
        
        # Fallback: retorna componentes conexas
        componentes = self._componentes_conexos()
        return ("Componentes Conexas", componentes, 0.0)

    def slpa(self, T=10, r=0.1):
        """
        SLPA - Speaker-Listener Label Propagation Algorithm
        Algoritmo para detecção de comunidades sobrepostas.
        
        Args:
            T: Número de iterações (padrão: 20)
            r: Threshold para remover labels raros (padrão: 0.1)
        
        Returns:
            Lista de comunidades (pode haver sobreposição) e modularidade
        """
        import random
        from collections import defaultdict, Counter
        
        # Inicialização: cada nó tem uma "memória" com seu próprio label
        memoria = {v: [v] for v in self.vertices}
        
        # Fase 1: Propagação de labels (T iterações)
        for iteracao in range(T):
            # Processa nós em ordem aleatória
            vertices_shuffled = self.vertices.copy()
            random.shuffle(vertices_shuffled)
            
            for listener in vertices_shuffled:
                idx_listener = self._indice(listener)
                
                # Coleta labels dos vizinhos (speakers)
                labels_vizinhos = []
                for j in range(self.n):
                    if self.matriz[idx_listener][j] == 1:
                        speaker = self.vertices[j]
                        # Escolhe um label aleatório da memória do vizinho
                        if memoria[speaker]:
                            label = random.choice(memoria[speaker])
                            labels_vizinhos.append(label)
                
                if not labels_vizinhos:
                    continue
                
                # Escolhe o label mais popular (ou aleatório em caso de empate)
                counter = Counter(labels_vizinhos)
                max_freq = max(counter.values())
                labels_mais_populares = [l for l, c in counter.items() if c == max_freq]
                label_escolhido = random.choice(labels_mais_populares)
                
                # Adiciona o label à memória do listener
                memoria[listener].append(label_escolhido)
        
        # Fase 2: Post-processamento - remove labels raros
        threshold = int(T * r)
        for v in self.vertices:
            counter = Counter(memoria[v])
            # Mantém apenas labels que aparecem mais que o threshold
            memoria[v] = [label for label, count in counter.items() if count > threshold]
            
            # Se ficou vazio, mantém o label original
            if not memoria[v]:
                memoria[v] = [v]
        
        # Fase 3: Converte memórias em comunidades
        comunidades_dict = defaultdict(set)
        for node, labels in memoria.items():
            for label in labels:
                comunidades_dict[label].add(node)
        
        comunidades_lista = [com for com in comunidades_dict.values() if len(com) > 0]
        
        # Para calcular modularidade com sobreposição, converte para partição
        # (cada nó fica na comunidade onde mais aparece)
        particao = self._converter_sobreposicao_para_particao(memoria)
        mod = self.modularidade(particao)
        
        return comunidades_lista, mod

    def demon(self, epsilon=0.15):
        """
        Algoritmo para detecção de comunidades sobrepostas baseado em ego networks.
        
        Args:
            epsilon: Threshold para merge de comunidades (padrão: 0.25)
        
        Returns:
            Lista de comunidades sobrepostas e modularidade
        """
        # Fase 1: Para cada nó, encontra sua ego network
        ego_networks = {}
        for v in self.vertices:
            idx_v = self._indice(v)
            
            # Ego = nó + seus vizinhos
            ego = {v}
            vizinhos = []
            for j in range(self.n):
                if self.matriz[idx_v][j] == 1:
                    ego.add(self.vertices[j])
                    vizinhos.append(self.vertices[j])
            
            # Detecta comunidades na ego network usando Label Propagation
            if len(ego) > 2:
                comunidades_ego = self._label_propagation_local(ego, vizinhos)
                ego_networks[v] = comunidades_ego
            else:
                ego_networks[v] = [ego]
        
        # Fase 2: Merge de comunidades similares
        todas_comunidades = []
        for comunidades in ego_networks.values():
            todas_comunidades.extend(comunidades)
        
        # Remove duplicatas e mescla comunidades com alta sobreposição
        comunidades_unicas = self._merge_comunidades_demon(todas_comunidades, epsilon)
        
        # Calcula modularidade
        particao = self._converter_comunidades_para_particao(comunidades_unicas)
        mod = self.modularidade(particao)
        
        return comunidades_unicas, mod

    def _label_propagation_local(self, nodes, vizinhos, max_iter=10):
        """Label propagation em um subconjunto de nós."""
        import random
        from collections import defaultdict, Counter
        
        nodes_list = list(nodes)
        labels = {v: v for v in nodes_list}
        
        for _ in range(max_iter):
            mudou = False
            random.shuffle(nodes_list)
            
            for v in nodes_list:
                idx_v = self._indice(v)
                
                # Conta labels dos vizinhos que estão no subgrafo
                label_count = defaultdict(int)
                for j in range(self.n):
                    if self.matriz[idx_v][j] == 1:
                        neighbor = self.vertices[j]
                        if neighbor in nodes:
                            label_count[labels[neighbor]] += 1
                
                if label_count:
                    max_count = max(label_count.values())
                    labels_max = [l for l, c in label_count.items() if c == max_count]
                    novo_label = min(labels_max)
                    
                    if novo_label != labels[v]:
                        labels[v] = novo_label
                        mudou = True
            
            if not mudou:
                break
        
        # Agrupa por label
        comunidades_dict = defaultdict(set)
        for node, label in labels.items():
            comunidades_dict[label].add(node)
        
        return list(comunidades_dict.values())

    def _merge_comunidades_demon(self, comunidades, epsilon):
        """Mescla comunidades com sobreposição significativa."""
        def jaccard(c1, c2):
            intersecao = len(c1 & c2)
            uniao = len(c1 | c2)
            return intersecao / uniao if uniao > 0 else 0.0
        
        # Remove comunidades muito pequenas
        comunidades = [c for c in comunidades if len(c) >= 2]
        
        # Remove duplicatas exatas
        comunidades_unicas = []
        vistos = set()
        for com in comunidades:
            com_frozen = frozenset(com)
            if com_frozen not in vistos:
                vistos.add(com_frozen)
                comunidades_unicas.append(com)
        
        # Merge iterativo
        mesclou = True
        while mesclou:
            mesclou = False
            nova_lista = []
            usadas = set()
            
            for i in range(len(comunidades_unicas)):
                if i in usadas:
                    continue
                
                com1 = comunidades_unicas[i]
                mesclada = False
                
                for j in range(i + 1, len(comunidades_unicas)):
                    if j in usadas:
                        continue
                    
                    com2 = comunidades_unicas[j]
                    
                    # Se Jaccard > epsilon, mescla
                    if jaccard(com1, com2) > epsilon:
                        nova_lista.append(com1 | com2)
                        usadas.add(i)
                        usadas.add(j)
                        mesclada = True
                        mesclou = True
                        break
                
                if not mesclada:
                    nova_lista.append(com1)
                    usadas.add(i)
            
            comunidades_unicas = nova_lista
        
        return comunidades_unicas

    def _converter_sobreposicao_para_particao(self, memoria):
        """Converte comunidades sobrepostas em partição para calcular modularidade."""
        from collections import Counter
        
        particao_dict = {}
        for node, labels in memoria.items():
            # Cada nó fica na comunidade mais frequente em sua memória
            if labels:
                counter = Counter(labels)
                particao_dict[node] = counter.most_common(1)[0][0]
            else:
                particao_dict[node] = node
        
        # Converte em lista de conjuntos
        comunidades_dict = defaultdict(set)
        for node, label in particao_dict.items():
            comunidades_dict[label].add(node)
        
        return list(comunidades_dict.values())

    def _converter_comunidades_para_particao(self, comunidades):
        """Converte comunidades sobrepostas em partição."""
        particao_dict = {}
        
        for idx, com in enumerate(comunidades):
            for node in com:
                # Se nó já está em uma comunidade, mantém a primeira
                if node not in particao_dict:
                    particao_dict[node] = idx
        
        # Converte em lista de conjuntos
        comunidades_dict = defaultdict(set)
        for node, label in particao_dict.items():
            comunidades_dict[label].add(node)
        
        return list(comunidades_dict.values())

    def detectar_comunidades_sobrepostas(self, ego_node=None):
        """
        Testa todos os algoritmos para comunidades sobrepostas e retorna o melhor.
        """
        resultados_sobreposicao = []
        
        try:
            com_slpa, mod_slpa = self.slpa(T=20, r=0.1)
            resultados_sobreposicao.append(("SLPA", com_slpa, mod_slpa))
            print(f"        ✓ SLPA: {len(com_slpa)} comunidades, Mod={mod_slpa:.4f}")
        except Exception as e:
            print(f"        ✗ SLPA falhou: {e}")
        
        try:
            com_demon, mod_demon = self.demon(epsilon=0.25)
            resultados_sobreposicao.append(("DEMON", com_demon, mod_demon))
            print(f"        ✓ DEMON: {len(com_demon)} comunidades, Mod={mod_demon:.4f}")
        except Exception as e:
            print(f"        ✗ DEMON falhou: {e}")
        
        # Escolhe o melhor
        if resultados_sobreposicao:
            melhor = max(resultados_sobreposicao, key=lambda x: x[2])
            return melhor
        
        # Fallback
        return ("Nenhum algoritmo sobreposicao funcionou", [set(self.vertices)], 0.0)