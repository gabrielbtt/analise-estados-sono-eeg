import pandas as pd
import os

# Diretório onde o script está
diretorio_script = os.path.dirname(os.path.abspath(__file__))

# Caminho do arquivo de entrada
arquivo_entrada = os.path.join(
    diretorio_script, '..', 'analise-estados-sono-eeg', 'dados', 'brutos',
    'dados_epocas.csv'
)

# Caminho de saída: apenas CSV
arquivo_saida_csv = os.path.join(diretorio_script, 'SC4001E0_PROCESSADO.csv')

# --- Execução ---
try:
    # Leitura do CSV
    df = pd.read_csv(arquivo_entrada)
    print("Arquivo lido com sucesso!")
    print(f"Shape: {df.shape}")

    # Análise exploratória
    print("\nAnálise exploratória:")
    print("Shape:", df.shape)
    print("\nColunas:")
    print(df.columns.tolist())
    print("\nHead (primeiras 5 linhas):")
    print(df.head())
    print("\nInfo:")
    print(df.info())
    print("\nMissing values:")
    print(df.isnull().sum())

    # Salvar o arquivo processado em CSV
    df.to_csv(arquivo_saida_csv, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nArquivo CSV salvo em: {arquivo_saida_csv}")

except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado em {os.path.abspath(arquivo_entrada)}")
except Exception as e:
    print(f"Erro inesperado: {e}")
