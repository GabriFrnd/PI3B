import csv
import os
from datetime import datetime

def exportar_metricas_detalhadas_csv(resultados, filename="metricas_detalhadas.csv"):
    """
    Exporta métricas mais detalhadas incluindo centralidade e PageRank dos top nós.
    
    Args:
        resultados: Lista de dicionários com os resultados
        filename: Nome do arquivo CSV de saída
    """
    if not resultados:
        print("Nenhum resultado para exportar.")
        return
    
    rows = []
    
    for resultado in resultados:
        ego = resultado['ego']
        
        row = {
            'ego': ego,
            'algoritmo': resultado.get('algoritmo_usado', ''),
            'tipo': resultado.get('tipo_algoritmo', ''),
            'nmi': resultado.get('nmi', 0),
            'ari': resultado.get('ari', 0),
            'modularidade': resultado.get('modularidade', 0),
        }
        
        rows.append(row)
    
    # Escreve o CSV
    campos = list(rows[0].keys()) if rows else []
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Métricas detalhadas exportadas para: {filename}")