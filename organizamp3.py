import os
import requests
import eyed3
from datetime import datetime
import logging
import json
from tqdm import tqdm

def organizar_arquivos(diretorio_origem="/media/epessoa/D/origem", 
                       diretorio_destino="/media/epessoa/D/destino", 
                       diretorio_json="/media/epessoa/D/json",
                       release_group="the original release"):
    """Organiza arquivos MP3 em um novo diretório com base nos metadados da MusicBrainz API,
    buscando especificamente por um release group e salvando a resposta JSON.

    Args:
        diretorio_origem: Caminho para o diretório com os arquivos MP3.
        diretorio_destino: Caminho para o diretório de destino.
        diretorio_json: Caminho para o diretório onde salvar os arquivos JSON.
        release_group: Nome do release group a ser buscado.
    """

    # Configuração do logging
    logging.basicConfig(filename='organizar_arquivos.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Lista de arquivos a serem processados
    arquivos = [f for f in os.listdir(diretorio_origem) if f.endswith(".mp3")]
    total_arquivos = len(arquivos)

    # Iterar sobre os arquivos com a barra de progresso
    with tqdm(total=total_arquivos, desc="Processando arquivos") as pbar:
        for arquivo in arquivos:
            caminho_completo = os.path.join(diretorio_origem, arquivo)

            # Extrair título e artista do nome do arquivo (pode ser usado para buscas adicionais)
            nome_arquivo, extensao = os.path.splitext(arquivo)
            partes = nome_arquivo.split('-')
            artista = partes[1].strip()
            titulo = ' '.join(partes[2:]).strip()

            try:
                # Consulta à MusicBrainz API
                resposta = requests.get(f"https://musicbrainz.org/ws/2/release/?query={release_group}&fmt=json")
                resposta.raise_for_status()  # Lança uma exceção se a requisição falhar
                dados = resposta.json()

                # Salvar o JSON em um arquivo
                with open(os.path.join(diretorio_json, f"{release_group}_{artista}_{titulo}.json"), 'w') as f:
                    json.dump(dados, f, indent=4)

                # Priorizar o primeiro release encontrado (assumindo que seja o mais relevante)
                release = dados['releases'][0]

                # Extrair metadados
                titulo_api = release['title']
                artista_api = release['artist-credit'][0]['name']
                genero = release['primary-type']
                data_lancamento = release['date']
                isrc = release['media'][0]['track'][0]['isrc']

                # ... (restante do código para renomear e atualizar tags)

            except requests.exceptions.RequestException as e:
                logging.error(f"Erro ao consultar a MusicBrainz API para {arquivo}: {e}")
            except (IndexError, KeyError) as e:
                logging.error(f"Dados da API inválidos para {arquivo}: {e}")
            except Exception as e:
                logging.error(f"Erro inesperado ao processar {arquivo}: {e}")

            pbar.update(1)  # Atualiza a barra de progresso

# Execução do script com os caminhos definidos
organizar_arquivos()