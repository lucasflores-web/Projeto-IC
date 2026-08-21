from fastapi import FastAPI, status, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from schemas import Mensagem
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

app = FastAPI()
origins = ['http://localhost:3000']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
# Compacta as respostas grandes (dataset completo, todos os anos) automaticamente
app.add_middleware(GZipMiddleware, minimum_size=1000)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"message": "No favicon"}


@app.get("/conceito_enade", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_conceito_enade(db: Session = Depends(get_db)):
    try:
        return models.get_all_years_data("conceito_enade")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/cpc", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_cpc(db: Session = Depends(get_db)):
    try:
        return models.get_all_years_data("cpc")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/idd", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_idd(db: Session = Depends(get_db)):
    try:
        return models.get_all_years_data("idd")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/igc", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_igc(db: Session = Depends(get_db)):
    try:
        return models.get_all_years_data("igc")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# endpoint pra descobrir quais anos existem de cada dataset, sem hardcode
@app.get("/anos_disponiveis/{dataset}", status_code=status.HTTP_200_OK)
def get_anos_disponiveis(dataset: str):
    anos = models.list_available_tables(dataset)
    if not anos:
        raise HTTPException(status_code=404, detail=f"Nenhuma tabela encontrada para dataset '{dataset}'")
    return {"dataset": dataset, "anos": anos}


@app.get("/filtros/{dataset}/{coluna}", status_code=status.HTTP_200_OK)
def get_valores_filtro(dataset: str, coluna: str):
    """
    Endpoint para alimentar os dropdowns do front.
    Ex: /filtros/cpc/uf ou /filtros/cpc/area_de_avaliacao
    """
    try:
        valores = models.get_distinct_values(dataset, coluna)
        if not valores:
            return {"dataset": dataset, "coluna": coluna, "valores": []}
        return {"dataset": dataset, "coluna": coluna, "valores": valores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/filtros/{dataset}/{coluna}/por/{filtro_coluna}", status_code=status.HTTP_200_OK)
def get_valores_filtro_condicionado(dataset: str, coluna: str, filtro_coluna: str, valor: str):
    """
    Valores distintos de `coluna`, filtrando por outra coluna já conhecida.
    Ex: /filtros/cpc/area_de_avaliacao/por/nome_da_ies?valor=Universidade X
    """
    try:
        valores = models.get_distinct_values_filtered(dataset, coluna, filtro_coluna, valor)
        return {"dataset": dataset, "coluna": coluna, "valores": valores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 
# ---------------------------------------------------------------------------
# Endpoint eficiente de dados filtrados — GET com parâmetros fixos por dataset
# (Opção 2: sem mapa de nomes, sem JSON em query string, cacheável por URL)
# ---------------------------------------------------------------------------

_FILTROS_POR_DATASET = {
    "igc": ["sigla_da_uf", "categoria_administrativa", "igc_faixa"],
    "cpc": [
        "nome_do_curso", "cpc_faixa", "area_de_avaliacao",
        "sigla_da_uf", "conceito_enade_continuo", "nome_da_ies",
    ],
    "idd": ["sigla_da_uf", "area_de_avaliacao", "nome_da_ies"],
    "conceito_enade": ["sigla_da_uf", "area_de_avaliacao", "nome_da_ies"],
}


@app.get("/dados_filtrados/{dataset}", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_dados_filtrados(
    dataset: str,
    anos: List[str] = Query(...),
    sigla_da_uf: Optional[str] = None,
    categoria_administrativa: Optional[str] = None,
    igc_faixa: Optional[str] = None,
    cpc_faixa: Optional[str] = None,
    area_de_avaliacao: Optional[str] = None,
    conceito_enade_continuo: Optional[str] = None,
    nome_do_curso: Optional[str] = None,
    nome_da_ies: Optional[str] = None,
):
    """
    Retorna dados já filtrados no banco (WHERE), para os anos e colunas pedidos.
    Só os parâmetros válidos para o dataset (ver _FILTROS_POR_DATASET) são
    aplicados; os demais são ignorados mesmo se enviados.

    Ex: /dados_filtrados/igc?anos=2022&anos=2023&sigla_da_uf=SP&igc_faixa=4
    """
    colunas_permitidas = _FILTROS_POR_DATASET.get(dataset)
    if colunas_permitidas is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' desconhecido")

    candidatos = {
        "sigla_da_uf": sigla_da_uf,
        "categoria_administrativa": categoria_administrativa,
        "igc_faixa": igc_faixa,
        "cpc_faixa": cpc_faixa,
        "area_de_avaliacao": area_de_avaliacao,
        "conceito_enade_continuo": conceito_enade_continuo,
        "nome_do_curso": nome_do_curso,
        "nome_da_ies": nome_da_ies,
    }
    filtros = {
        col: val for col, val in candidatos.items()
        if col in colunas_permitidas and val not in (None, "", "Todos")
    }

    try:
        return models.get_filtered_data(dataset, anos, filtros)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))