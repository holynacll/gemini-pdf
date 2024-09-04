from typing import Annotated
from pathlib import Path
import mimetypes
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.utils import upload_file, update_datasheets, keywords_highlight, json_to_text_with_newlines
from src.analyze_contract import analyze_document


static_path = settings.base_dir / "static"
if not static_path.exists():
    static_path.mkdir(parents=True, exist_ok=True)


app = FastAPI()

app.mount(settings.static_dir.as_posix(), StaticFiles(directory="static"), name="static")

prompt_text = """
Você é um especialista em análise de contratos. Sua tarefa é extrair as seguintes informações de um contrato fornecido e apresentá-las em um formato JSON estruturado:

* **n_contrato:** Número do contrato (no formato que corresponde à expressão regular "\d+/\d+")
* **n_licitacao:** Número da licitação (no formato que corresponde à expressão regular "\d+/\d+")
* **assinatura:** Data da assinatura (no formato "DD/MM/AAAA")
* **vencimento:** Data de vencimento (no formato "DD/MM/AAAA" ou string vazia se não informado)
* **contratada:** Nome do Fornecedor 
* **cnpj:** CNPJ do Fornecedor (contratada) (no formato "XX.XXX.XXX/XXXX-XX")
* **modalidade:** Modalidade da licitação
* **objeto:** Objeto do contrato
* **contratante:** Nome da Contratante
* **valor:** Valor do contrato (apenas números e vírgula, sem "R$" ou texto)
* **filename:** Nome do arquivo PDF

Exemplo de saída JSON:

```json
{
  "n_contrato": "242/2024",
  "n_licitacao": "145/2024",
  "assinatura": "22/07/2024",
  "vencimento": "",
  "contratada": "LEANDRO ROBERTO DOS SANTOS",
  "cnpj": "10.755.146/0001-09",
  "modalidade": "Inexigibilidade de Licitação",
  "objeto": "apresentação musical de Forró",
  "contratante": "Município de Caetité-BA",
  "valor": "12.000,00",
  "filename": "caetite.pdf"
}

Se alguma informação não estiver presente no contrato, indique uma string vazia ("") no lugar da informação ausente, exceto para vencimento, onde você deve usar "Não informado".
"""


@app.post("/analyze-contract")
async def analyze_contract(
    file: Annotated[UploadFile, File(description="A contract pdf file")]
):
    file_path = await upload_file(file)
    text_parsed = await analyze_document(file_path, prompt_text)
    await update_datasheets(text_parsed)
    await keywords_highlight(file_path, text_parsed)
    text_parsed.update({"filename": file_path.name})
    return JSONResponse(content=text_parsed)


@app.get("/get-contract-pdf/{filename}")
async def get_contract_pdf(filename: str):
    filepath: Path = Path(settings.static_dir) / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail='Contract file not found')

    # Detecta automáticamente o tipo de mídia com base na extensão do arquivo
    media_type, _ = mimetypes.guess_type(filepath)

    return FileResponse(
        path=filepath.resolve(),
        filename=filepath.name,
        media_type=media_type,
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


@app.post("/analyze-contract-html")
async def analyze_contract_html(
    file: Annotated[UploadFile, File(description="A contract pdf file")]
):
    file_path = await upload_file(file)
    text_parsed = await analyze_document(file_path, prompt_text)
    await update_datasheets(text_parsed)
    await keywords_highlight(file_path, text_parsed)

    # Construção do HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Análise de Contrato</title>
        <style>
            .container {{
                display: flex;
            }}
            .pdf-container {{
                width: 50%;
                padding: 20px;
            }}
            .analysis-container {{
                width: 50%;
                padding: 20px;
                border-left: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="pdf-container">
                <h2>Contrato</h2>
                <embed src="{file_path.as_posix()}" width="100%" height="600px" type="application/pdf">
            </div>
            <div class="analysis-container">
                <h2>Análise</h2>
                <pre>{json_to_text_with_newlines(text_parsed)}</pre>
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/")
async def main():
    content = """
<!DOCTYPE html>
<html>
<head>
<style>
.upload-container {
  display: inline-block; 
  position: relative;    
}

.upload-label {
  display: block;
  width: 240px;
  height: 30px;
  background-color: #6c757d; /* Cinza médio */
  color: white;
  text-align: center;
  line-height: 30px; 
  border-radius: 5px;  
  cursor: pointer;     
}

.upload-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;          
  cursor: pointer;     
}

input[type="submit"] {
  background-color: #6c757d; /* Mesma cor do botão de upload */
  color: white;
  padding: 8px 15px; 
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px; 
}

input[type="submit"]:hover {
  background-color: #495057; /* Cinza mais escuro ao passar o mouse */
}
</style>
</head>
<body>

<form action="/analyze-contract-html" enctype="multipart/form-data" method="post">
  <div class="upload-container">
    <label for="files" class="upload-label">Selecione o Contrato</label>
    <input id="files" name="file" class="upload-input" type="file">
  </div>
  <input type="submit" value="Enviar"> 
</form>

</body>
</html>
"""
    return HTMLResponse(content=content)
