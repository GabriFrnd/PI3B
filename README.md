📊 Análise de Redes Sociais com Grafos
Este projeto realiza a análise de redes sociais por meio de Teoria dos Grafos, com foco na identificação de usuários influentes e detecção de comunidades usando o dataset Facebook Ego Networks. Foram aplicadas métricas de centralidade e diversos algoritmos de detecção de comunidades, com resultados consolidados em relatórios automatizados.

🧠 Objetivos

1. Identificar os usuários mais influentes em redes sociais usando métricas de centralidade (Grau, Proximidade, Intermediação, PageRank).
2. Detectar comunidades com algoritmos como Girvan–Newman, Louvain, Infomap, K-Click, Label Propagation, SLPA e DEMON.
3. Comparar o desempenho dos algoritmos usando métricas como NMI, ARI e Modularidade.
4. Visualizar a estrutura das redes e comunidades geradas.

🛠 Tecnologias Utilizadas

1. Python
2. NetworkX
3. Matplotlib
4. Pandas
5. Algoritmos de detecção de comunidades (Louvain, Infomap, SLPA, etc.)
6. Facebook Ego Networks (dataset público)

📈 Métricas de Centralidade Aplicadas

1. Grau
2. Proximidade
3. Intermediação (Betweenness)
4. PageRank

🧩 Algoritmos de Detecção de Comunidades

1. Girvan–Newman
2. Louvain
3. Infomap
4. K-Click
5. Label Propagation (LP)
6. SLPA
7. DEMON

🚀 Como Executar o Projeto

1. Clone o repositório
   
bash
git clone https://github.com/GabriFrnd/PI3B.git
cd PI3B

3. Instale as dependências

bash
pip install -r requirements.txt

Caso não haja um arquivo requirements.txt, instale manualmente:

bash
pip install networkx matplotlib pandas numpy scikit-learn

3. Execute o script principal

bash
python main.py

4. Visualize os resultados

Os relatórios em PDF serão gerados na pasta results/.
As imagens dos grafos coloridos por comunidade serão salvas em images/.

📌 Resultados Destacados

O algoritmo SLPA obteve a maior modularidade (0,66), indicando comunidades internamente coesas.
Infomap e Label Propagation apresentaram bom equilíbrio entre NMI e modularidade.
Redes mais densas tendem a ter maior modularidade e estrutura comunitária mais complexa.

📄 Estrutura do Projeto

PI3B/
├── data/                 # Datasets (Facebook Ego Networks)
├── src/                  # Código-fonte
│   ├── grafo.py          # Classe GrafoDenso (matriz de adjacência)
│   ├── metricas.py       # Cálculo de centralidade
│   ├── comunidades.py    # Algoritmos de detecção
│   └── visualizacao.py   # Geração de gráficos
├── results/              # Relatórios em PDF
├── images/               # Imagens dos grafos
├── main.py               # Script principal
└── README.md

👥 Autores

1. Davi Serra Bezerra
2. Gabriel Fernandes Feitosa
3. Guilherme Tempesta Francisco
4. David Lopes Bezerra de Oliveira
5. Gabrielle Arruda Rodrigues
6. Vinicius von Glehn Severo

📚 Referências

NetworkX Documentation
SNAP: Social Circles - Facebook
Leskovec, J.; McAuley, J. (2012). Learning to Discover Social Circles in Ego Networks.
