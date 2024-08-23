from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .utils import upload_file, text_parser, update_datasheets, keywords_highlight
from .analyze_contract import analyze_document

static_path = Path("static")
if not static_path.exists():
    static_path.mkdir(parents=True, exist_ok=True)


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

prompt_text = """
Você é um especialista em análise de contratos. Sua tarefa é extrair as seguintes informações de um contrato fornecido, **mantendo o formato original em que aparecem no texto, sem realizar qualquer transformação:**

* Número do contrato
* Número da licitação
* Data da assinatura
* Data de vencimento
* Fornecedor (contratada), incluindo o CNPJ
* Modalidade da licitação
* Objeto do contrato
* Contratante
* Valor do contrato

Apresente as informações extraídas no seguinte formato:

Número do contrato: [número do contrato]
Número da licitação: [número da licitação]
Data da assinatura: [data da assinatura]
Data de vencimento: [data de vencimento]
Fornecedor (contratada): [nome do fornecedor], CNPJ [CNPJ do fornecedor]
Modalidade da licitação: [modalidade da licitação]
Objeto do contrato: [objeto do contrato]
Contratante: [contratante]
Valor do contrato: [valor do contrato]

Se alguma informação não estiver presente no contrato, indique 'Não informado' no lugar da informação ausente.
"""


@app.post("/analyze-contract")
async def analyze_contract(
    file: Annotated[UploadFile, File(description="A contract pdf file")]
):
    file_path = await upload_file(file)
    text_analyzed = await analyze_document(file_path, prompt_text)
    text_parsed = text_parser(text_analyzed)
    await update_datasheets(text_parsed)
    await keywords_highlight(file_path, text_parsed)
    # return JSONResponse(content=text_parsed)
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
                <pre>{text_analyzed}</pre>
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

<form action="/analyze-contract" enctype="multipart/form-data" method="post">
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
