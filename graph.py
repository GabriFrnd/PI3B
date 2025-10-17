from abc import ABC, abstractmethod
from collections import deque
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

    # @abstractmethod
    # def imprimir(self):
    #     pass

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

    def girvan_newman(self):
        g = copy.deepcopy(self)
        comunidades = [set(self.vertices)]
        while len(comunidades)==1:
            betweenness = g.centralidade_intermediacao()
            max_bet, aresta_max = 0, None
            for i in range(g.n):
                for j in range(i+1,g.n):
                    if g.matriz[i][j]==1:
                        valor = betweenness[g.vertices[i]] + betweenness[g.vertices[j]]
                        if valor>max_bet: max_bet=valor; aresta_max=(g.vertices[i], g.vertices[j])
            if aresta_max: g.remover_aresta(*aresta_max)
            comunidades = g._componentes_conexos()
        return comunidades

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
        """
        Calcula o coeficiente de clusterização local para um vértice específico.
        Mede a proporção de arestas existentes entre os vizinhos de um nó
        em relação ao número máximo de arestas possíveis entre eles.
        """
        # 1. Obter o índice do vértice na matriz
        idx = self._indice(vertice)
        
        # 2. Encontrar todos os vizinhos do vértice
        vizinhos_indices = []
        for j in range(self.n):
            if self.matriz[idx][j] == 1:
                vizinhos_indices.append(j)
        
        grau = len(vizinhos_indices)
        
        # 3. Se o grau for menor que 2, o coeficiente é 0 (não há pares de vizinhos)
        if grau < 2:
            return 0.0
            
        # 4. Contar as arestas que existem ENTRE os vizinhos
        arestas_entre_vizinhos = 0
        for i in range(len(vizinhos_indices)):
            for j in range(i + 1, len(vizinhos_indices)):
                # Pega dois vizinhos distintos
                vizinho1_idx = vizinhos_indices[i]
                vizinho2_idx = vizinhos_indices[j]
                
                # Verifica se há uma aresta entre eles
                if self.matriz[vizinho1_idx][vizinho2_idx] == 1:
                    arestas_entre_vizinhos += 1
        
        # 5. Aplicar a fórmula
        # O número máximo de arestas possíveis entre os vizinhos é k * (k - 1) / 2
        max_arestas_possiveis = grau * (grau - 1) / 2
        
        return arestas_entre_vizinhos / max_arestas_possiveis
    
    def coeficiente_de_clusterizacao_medio(self):
        """Calcula o coeficiente de clusterização médio do grafo."""
        soma_coeficientes = sum(self.coeficiente_de_clusterizacao_local(v) for v in self.vertices)
        return soma_coeficientes / self.n if self.n > 0 else 0.0