from typing import Annotated
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .utils import upload_file, text_parser, update_datasheets, keywords_highlight
from .analyze_contract import analyze_document

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory="static"), name="static"
)

prompt_text = """
Você é um especialista em análise de contratos. Sua tarefa é extrair as seguintes informações de um contrato fornecido:

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
async def analyze_contract(file: Annotated[UploadFile, File(description="A contract pdf file")]):
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
<body>
<form action="/analyze-contract" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
