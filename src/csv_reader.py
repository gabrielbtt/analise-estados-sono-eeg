import pandas as pd
import os

# Diretório onde o script está
diretorio_script = os.path.dirname(os.path.abspath(__file__))

# Caminho do arquivo de entrada
arquivo_entrada = os.path.join(
    diretorio_script, '..', 'dados', 'brutos',
    'dados_epocas.csv'
)

# Caminho do diretório de saída (dados/tratados)
diretorio_saida = os.path.join(
    diretorio_script, '..', 'dados', 'tratados'
)

# Garante que o diretório existe
os.makedirs(diretorio_saida, exist_ok=True)

# Caminho completo do arquivo de saída
arquivo_saida_csv = os.path.join(
    diretorio_saida,
    'TODOS_PACIENTES_PROCESSADO.csv'
)

try:
    df = pd.read_csv(arquivo_entrada)
    print("Arquivo lido com sucesso!")
    print(f"Shape: {df.shape}")

    # Análise exploratória
    print("\nColunas:")
    print(df.columns.tolist())

    # Salvar o arquivo processado
    df.to_csv(
        arquivo_saida_csv,
        index=False,
        sep=';',
        encoding='utf-8-sig'
    )

    print(f"\nArquivo CSV salvo em:\n{os.path.abspath(arquivo_saida_csv)}")

except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado em {os.path.abspath(arquivo_entrada)}")
except Exception as e:
    print(f"Erro inesperado: {e}")
