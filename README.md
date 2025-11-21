# 🔍 Análise de Redes Sociais com Grafos

📊 Um projeto de análise de redes sociais que utiliza teoria dos grafos para identificar usuários influentes e detectar comunidades em redes sociais. Este projeto combina métricas de centralidade e algoritmos avançados para analisar a estrutura e dinâmica de interações sociais.

## ✨ Funcionalidades

- **Identificação de Influenciadores**: Calcula métricas de centralidade (Grau, Proximidade, Intermediação, PageRank) para detectar usuários mais influentes
- **Detecção de Comunidades**: Aplica algoritmos como Girvan-Newman, Louvain, Infomap, K-Click, Label Propagation, SLPA e DEMON para identificar grupos sociais
- **Visualização Intuitiva**: Gera representações gráficas das redes, coloridas por comunidade, para facilitar a interpretação
- **Análise Comparativa**: Avalia o desempenho dos algoritmos através de métricas como NMI, ARI e Modularidade
- **Relatórios Automatizados**: Gera relatórios em PDF com resultados estruturais e visualizações

## 🧱 Tecnologias Utilizadas

- **Python** - Linguagem principal para análise de dados
- **NetworkX** - Biblioteca para análise e manipulação de grafos
- **Matplotlib** - Geração de visualizações e gráficos
- **Pandas** - Manipulação e análise estruturada de dados
- **Scikit-learn** - Métricas de avaliação (NMI, ARI)

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

🛠️ Como Fazer o Deploy (Instalação e Execução)
Para configurar e rodar o projeto PI3B em seu ambiente local, siga os passos abaixo:

Pré-requisitos
Certifique-se de ter o Python 3.x e o pip (gerenciador de pacotes) instalados em seu sistema.

Passo 1: Clonar o Repositório
Abra seu terminal ou prompt de comando e clone o projeto usando o Git:

Bash
git clone https://github.com/GabriFrnd/PI3B.git
cd PI3B
Passo 2: Instalar as Dependências
O projeto depende de bibliotecas listadas no arquivo requirements.txt. Instale todas as dependências usando o pip install -r:

Bash
pip install -r requirements.txt
Este comando garante que todas as bibliotecas necessárias, como NetworkX, sejam instaladas nas versões compatíveis.   

Passo 3: Executar a Análise
Execute o arquivo principal do projeto (assumindo main.py como ponto de entrada) para iniciar o cálculo das métricas de centralidade, detecção de comunidades e a geração dos relatórios analíticos em PDF:

Bash
python main.py
A execução produzirá os resultados das métricas e as visualizações gráficas das redes analisadas.   
