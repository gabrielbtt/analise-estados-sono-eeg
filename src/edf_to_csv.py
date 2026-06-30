import mne
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Configurações de diretórios
BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_EDF = BASE_DIR / 'sleep_cassette'
PASTA_SAIDA = BASE_DIR / 'dados' / 'brutos'
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

arquivos_psg = sorted(PASTA_EDF.glob("*-PSG.edf"))
print(f"Encontrados {len(arquivos_psg)} arquivos PSG.\n")

# Função para encontrar o arquivo Hypnogram correspondente ao arquivo PSG
def encontrar_hypnogram(arq_psg: Path) -> Path | None:
    pasta = arq_psg.parent
    base = arq_psg.name.split('-')[0][:7]

    candidatos = [
        f"{base}C-Hypnogram.edf",
        f"{base}EC-Hypnogram.edf",
        f"{base}EH-Hypnogram.edf",
        arq_psg.name.replace("-PSG.edf", "-Hypnogram.edf"),
        arq_psg.name.replace("E0-PSG.edf", "EC-Hypnogram.edf"),
        arq_psg.name.replace("E0-PSG.edf", "EH-Hypnogram.edf"),
    ]

    for cand in candidatos:
        if (pasta / cand).exists():
            return pasta / cand
    return None


def processar_noite(arq_psg: Path):
    arq_hyp = encontrar_hypnogram(arq_psg)
    if not arq_hyp:
        print(f"Hypnogram não encontrado para {arq_psg.name}")
        return None

    print(f"Processando: {arq_psg.name} + {arq_hyp.name}")

    raw = mne.io.read_raw_edf(arq_psg, preload=True, verbose=False)

    # Seleção do canal EEG (Fpz-Cz ou Fpz-Cz)
    print(f"   Canais disponíveis: {raw.ch_names}")

    canal_alvo = None
    for cand in ['EEG Fpz-Cz', 'Fpz-Cz']:
        if cand in raw.ch_names:
            canal_alvo = cand
            break

    if canal_alvo is None:
        raise ValueError(f"Canal EEG não encontrado em {arq_psg.name}. Canais: {raw.ch_names}")

    raw.pick_channels([canal_alvo])
    print(f"   Canal selecionado: {canal_alvo}")

    anotacoes = mne.read_annotations(arq_hyp)
    hora_inicio = raw.info['meas_date']

    df = raw.to_data_frame()
    df.rename(columns={
        'time': 'Segundos_Relativos',
        canal_alvo: 'Voltagem_uV'
    }, inplace=True)

    df['Horario'] = hora_inicio + pd.to_timedelta(df['Segundos_Relativos'], unit='s')
    df['Horario'] = df['Horario'].dt.strftime('%H:%M:%S.%f').str[:-3]

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
            df.loc[
                (df['Segundos_Relativos'] >= inicio) &
                (df['Segundos_Relativos'] < fim),
                'Estado'
            ] = mapa_nomes[desc]

    # Filtra região do sono com margem
    indices_sono = df.index[~df['Estado'].isin(['Acordado', 'Nao_Marcado'])].tolist()
    if indices_sono:
        margem = 180000
        ini = max(0, indices_sono[0] - margem)
        fim = min(len(df) - 1, indices_sono[-1] + margem)
        df = df.iloc[ini:fim + 1]

    df.drop(columns=['Segundos_Relativos'], inplace=True, errors='ignore')

    nome_saida = arq_psg.name.split('-')[0] + "_BRUTO_NOITE.csv"
    caminho_saida = PASTA_SAIDA / nome_saida
    df.to_csv(caminho_saida, index=False)
    print(f"   Salvo: {caminho_saida.name} ({len(df):,} amostras)")

    return df

dfs = []
for arq_psg in arquivos_psg:
    df_i = processar_noite(arq_psg)
    if df_i is not None:
        df_i["arquivo_origem"] = arq_psg.name
        dfs.append(df_i)

if not dfs:
    raise RuntimeError("Nenhum arquivo processado.")

df_total = pd.concat(dfs, ignore_index=True)
arquivo_final = PASTA_SAIDA / "TODOS_PACIENTES_BRUTO.csv"
df_total.to_csv(arquivo_final, index=False)

print(f"\n Concluído! Arquivo final salvo em: {arquivo_final}")
print(f"Total de amostras: {len(df_total):,}")
