import os
import json
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app.config import settings


provider = GoogleProvider(api_key=settings.google_api_key)
model = GoogleModel('gemini-2.5-flash', provider=provider)
agent = Agent(model)

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
}

Se alguma informação não estiver presente no contrato, indique uma string vazia ("") no lugar da informação ausente, exceto para vencimento, onde você deve usar "Não informado".
"""

class Contract(BaseModel):
    n_contrato: str
    n_licitacao: str
    assinatura: str
    vencimento: str
    contratada: str
    cnpj: str
    modalidade: str
    objeto: str
    contratante: str
    valor: str
    

async def analyze_document(pdf_path: Path) -> dict:
    result = await agent.run(
        [
            PROMPT_ANALYZE,
            BinaryContent(data=pdf_path.read_bytes(), media_type='application/pdf'),
        ],
        output_type=Contract,
    )
    print(f"Result Analyze: {result}")
    return result.output.model_dump()


async def parse_document(text_analyzed: dict) -> dict:
    result = await agent.run(
        [
            PROMPT_PARSE,
            json.dumps(text_analyzed),
        ],
        output_type=Contract,
    )
    print(f"Result Parse: {result}")
    return result.output.model_dump()
