import os
import json
import google.generativeai as genai
from src.config import settings

genai.configure(api_key=settings.google_api_key)

PROMPT_ANALYZE = """
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

PROMPT_PARSE = """
Sua tarefa é extrair as seguintes informações de um resumo de contrato fornecido e apresentá-las em um formato JSON estruturado:

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
  "vencimento": "21/07/2025",
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

async def analyze_document(file_path):
    model = genai.GenerativeModel(
        "gemini-1.5-pro",
        generation_config={"response_mime_type": "application/json"}
    )
    sample_pdf = genai.upload_file(file_path)
    contents = [PROMPT_ANALYZE, sample_pdf]
    raw_response = model.generate_content(contents)
    response = json.loads(raw_response.text)
    return response


async def parse_document(text_analyzed: dict):
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )
    contents = [PROMPT_PARSE, json.dumps(text_analyzed)]
    raw_response = model.generate_content(contents)
    response = json.loads(raw_response.text)
    return response
