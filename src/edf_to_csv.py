import mne
import pandas as pd
import numpy as np
from datetime import timedelta
import warnings

warnings.filterwarnings('ignore')

# 1. Arquivos originais
arq_psg = 'sleep_cassette/SC4001E0-PSG.edf'
arq_hyp = 'sleep_cassette/SC4001EC-Hypnogram.edf'
nome_saida = arq_psg.split('-')[0] + "_BRUTO_NOITE.csv"

print(f"Lendo {arq_psg}...")
raw = mne.io.read_raw_edf(arq_psg, preload=True, verbose=False)
anotacoes = mne.read_annotations(arq_hyp)

# 2. SELEÇÃO DE SENSOR: Manter apenas o EEG principal para não pesar o arquivo
print("Filtrando apenas o sensor EEG Fpz-Cz...")
raw.pick_channels(['EEG Fpz-Cz'])

# 3. EXTRAÇÃO DO HORÁRIO DE INÍCIO
hora_inicio = raw.info['meas_date']

# 4. CONVERSÃO PARA DATAFRAME
print("Convertendo sinal para formato tabular...")
df = raw.to_data_frame()

# Ajustar nomes das colunas
# O MNE gera a coluna 'time' em segundos desde o início
df.rename(columns={'time': 'Segundos_Relativos', 'EEG Fpz-Cz': 'Voltagem_uV'}, inplace=True)

# 5. CRIAR COLUNA DE HORÁRIO REAL (Relógio)
# Usamos vetorização do Pandas para ser rápido (são milhões de linhas)
print("Calculando horários reais (relógio)...")
df['Horario'] = hora_inicio + pd.to_timedelta(df['Segundos_Relativos'], unit='s')
# Formatar para ficar fácil de ler no CSV
df['Horario'] = df['Horario'].dt.strftime('%H:%M:%S.%f').str[:-3] 

# 6. SINCRONIZAR ESTADOS DO SONO
print("Sincronizando estados do sono...")
df['Estado'] = 'Nao_Marcado'

mapa_nomes = {
    'Sleep stage W': 'Acordado',
    'Sleep stage 1': 'N1',
    'Sleep stage 2': 'N2',
    'Sleep stage 3': 'N3',
    'Sleep stage 4': 'N3',
    'Sleep stage R': 'REM'
}

for anot in anotacoes:
    inicio = anot['onset']
    fim = inicio + anot['duration']
    desc = anot['description']
    if desc in mapa_nomes:
        # Preenche o bloco de tempo com o nome simplificado
        df.loc[(df['Segundos_Relativos'] >= inicio) & (df['Segundos_Relativos'] < fim), 'Estado'] = mapa_nomes[desc]

# 7. RECORTE DA NOITE (Focar no sono + margem de 30 min)
print("Recortando período da noite...")
indices_sono = df.index[~df['Estado'].isin(['Acordado', 'Nao_Marcado', 'Outro'])].tolist()

if indices_sono:
    # Margem de 30 min (100Hz * 60s * 30min = 180.000 amostras)
    margem = 180000
    inicio_corte = max(0, indices_sono[0] - margem)
    fim_corte = min(len(df) - 1, indices_sono[-1] + margem)
    df_final = df.iloc[inicio_corte : fim_corte + 1].copy()
else:
    df_final = df

# Remover a coluna de segundos relativos para o arquivo ficar mais limpo
df_final.drop(columns=['Segundos_Relativos'], inplace=True)

# 8. SALVAR
print(f"Salvando CSV final ({len(df_final)} linhas)...")
df_final.to_csv(nome_saida, index=False)

print(f"✅ CONCLUÍDO! Arquivo: {nome_saida}")