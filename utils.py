import os
from pathlib import Path
import pandas as pd
import pymupdf
import fitz
from difflib import SequenceMatcher
from fastapi import UploadFile

async def upload_file(file: UploadFile):
    p = Path("static")
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    file_path = p / file.filename
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
    doc = pymupdf.open(file_path)
    for page in doc:
        text = str(page.get_text().encode("utf8"))
        for kw in keywords.values():
            if kw in text:
            # substring = search_most_large_substring(kw, text)
            # if substring != "":
                quads = page.search_for(kw)
                for quad in quads:
                    highlight = page.add_highlight_annot(quad)
                    highlight.set_colors(stroke=[0,1,0])
                    highlight.update()
    doc.save(file_path.as_posix(), incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


def search_most_large_substring(sentence: str, text: str):
    substrings = combinacoes_palavras(sentence)
    for substring in substrings:
        if substring in text:
            return substring        
    return ''

def combinacoes_palavras(sentence):
    """
    Gera todas as combinações de palavras de uma sentença, mantendo a ordem.

    Args:
        sentenca: A sentença de entrada.

    Returns:
        Uma lista contendo todas as combinações de palavras possíveis.
    """
    stopwords = ['RT', 'rt', 'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'há', 'nos', 'já', 'está', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo']

    palavras = sentence.split()
    combinacoes = [sentence]
    for i in range(len(palavras)):
        for j in range(i + 1, len(palavras) + 1):
            combinacoes.append(" ".join(palavras[i:j]))
    # filtrar combinacoes
    combinacoes_filtradas = [comb for comb in combinacoes if comb.lower() not in stopwords]
    
    # ordernar as combinacoes de maior comprimento para menor comprimento
    combinacoes_filtradas_ordenadas = sorted(combinacoes_filtradas, key=len, reverse=True)
    return combinacoes_filtradas_ordenadas