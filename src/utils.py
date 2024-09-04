import os
# import asyncio
from pathlib import Path
import pandas as pd
import fitz
from fastapi import UploadFile
from src.config import settings

# async def upload_file(file: UploadFile):
#     original_file_path = settings.static_dir / f"original_{file.filename}"
#     optimized_file_path = settings.static_dir / file.filename

#     # Salva o arquivo original temporariamente
#     with original_file_path.open(mode="wb") as f:
#         f.write(await file.read())

#     # Otimiza o PDF com Ghostscript (assíncrono)
#     try:
#         process = await asyncio.create_subprocess_exec(
#             'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/default', 
#             '-dNOPAUSE', '-dQUIET', '-dBATCH', '-o', str(optimized_file_path), str(original_file_path)
#         )
#         await process.wait()

#         if process.returncode != 0:
#             raise Exception(f"Ghostscript optimization failed with return code {process.stderr}")

#         # Remove o arquivo original (opcional, dependendo da sua lógica)
#         original_file_path.unlink()

#         return optimized_file_path

#     except Exception as e:
#         # Lidar com erros de otimização
#         print(f"Error optimizing PDF: {e}")
#         # Opcionalmente, retornar o caminho do arquivo original se a otimização falhar
#         return original_file_path


async def upload_file(file: UploadFile):
    file_path = settings.static_dir / file.filename
    # Salva o arquivo original temporariamente
    with file_path.open(mode="wb") as f:
        f.write(await file.read())
    return file_path


def text_parser(text: str):
    lines = text.strip().split('\n')
    data = {}
    for line in lines:
        key, value = line.split(': ', 1)
        data[key] = value
    return data


async def update_datasheets(data: dict):
    file_name = 'contratos.xlsx'
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(file_name, index=False)


async def keywords_highlight(file_path: Path, keywords: dict):
    bag_of_sentences: list[str] = []
    doc = fitz.open(file_path)
    text = ''
    for page in doc:
        text += str(page.get_text().lower()) + " "
    print(text)
    for kw in keywords.values():
        search_most_large_substrings(kw, text, bag_of_sentences)
    print(f"bag_of_sentences: {bag_of_sentences}")
    for page in doc:
        for sentence in bag_of_sentences:
            quads = page.search_for(sentence)
            for quad in quads:
                highlight = page.add_highlight_annot(quad)
                highlight.set_colors(stroke=[1,1,0]) # yellow
                highlight.update()
    doc.save(file_path.as_posix(), incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


def search_most_large_substrings(sentence: str, text: str, bag_of_words: list[str]):
    substrings = combinacoes_palavras(sentence)
    for substring in substrings:
        if substring in text and substring not in bag_of_words:
            bag_of_words.append(substring)
        


def combinacoes_palavras(sentence):
    """
    Gera todas as combinações de palavras de uma sentença, mantendo a ordem.

    Args:
        sentenca: A sentença de entrada.

    Returns:
        Uma lista contendo todas as combinações de palavras possíveis.
    """
    stopwords = ['RT', 'rt', 'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'há', 'nos', 'já', 'está', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo']

    palavras: list[str] = sentence.split()
    combinacoes: list[str] = [sentence]
    for i in range(len(palavras)):
        for j in range(i + 1, len(palavras) + 1):
            combinacoes.append(" ".join(palavras[i:j]))

    # to lower sentences
    combinacoes_lowercased = [s.lower() for s in combinacoes]

    # filtrar combinacoes
    combinacoes_filtradas = [comb for comb in combinacoes_lowercased if comb.lower() not in stopwords]

    # ordernar as combinacoes de maior comprimento para menor comprimento
    combinacoes_filtradas_ordenadas = sorted(combinacoes_filtradas, key=len, reverse=True)
    return combinacoes_filtradas_ordenadas


def json_to_text_with_newlines(json_object: dict):
  """Converts a JSON object to text with newlines between key-value pairs."""

  formatted_text = ""
  for key, value in json_object.items():
    formatted_text += f"{key}: {value}\n" 
  return formatted_text
