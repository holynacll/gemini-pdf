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
                quads = page.search_for(kw)
                for quad in quads:
                    highlight = page.add_highlight_annot(quad)
                    highlight.set_colors(stroke=[0,1,0])
                    highlight.update()
    # file_path.unlink()
    doc.save(file_path.as_posix(), incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
