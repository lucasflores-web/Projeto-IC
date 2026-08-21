import os
import logging
import pandas as pd
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")


def buscar_anos_disponiveis(tipo: str) -> list[str]:
    """Busca os anos disponíveis direto do endpoint /anos_disponiveis/{dataset}."""
    url = f"{API_BASE_URL}/anos_disponiveis/{tipo}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("Falha ao buscar anos disponíveis de '%s' em %s: %s", tipo, url, e)
        return []
    return resp.json().get("anos", [])


def buscar_valores_filtro(tipo: str, coluna: str) -> list[str]:
    """Busca valores distintos de uma coluna via /filtros/{dataset}/{coluna}."""
    url = f"{API_BASE_URL}/filtros/{tipo}/{coluna}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("Falha ao buscar filtros '%s/%s' em %s: %s", tipo, coluna, url, e)
        return []
    return sorted(resp.json().get("valores", []))


def buscar_valores_filtro_condicionado(tipo: str, coluna: str, filtro_coluna: str, filtro_valor: str) -> list[str]:
    """Busca valores distintos de `coluna`, filtrando por outra coluna já conhecida."""
    if not filtro_valor:
        return []
    url = f"{API_BASE_URL}/filtros/{tipo}/{coluna}/por/{filtro_coluna}"
    try:
        resp = requests.get(url, params={"valor": filtro_valor}, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("Falha ao buscar '%s' condicionado por '%s'='%s': %s", coluna, filtro_coluna, filtro_valor, e)
        return []
    return sorted(resp.json().get("valores", []))


def carregar_serie_historica(tipo: str, anos: list[str], filtros: dict | None = None) -> pd.DataFrame:
    """
    Busca dados já filtrados no banco (WHERE), via /dados_filtrados/{dataset}.
    `filtros` usa nomes REAIS de coluna (ex: {"sigla_da_uf": "SP"}).
    Não baixa mais o dataset completo.
    """
    filtros = filtros or {}
    params = [("anos", ano) for ano in anos]
    for coluna, valor in filtros.items():
        if valor in (None, "", "Todos"):
            continue
        params.append((coluna, valor))

    url = f"{API_BASE_URL}/dados_filtrados/{tipo}"
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("Falha ao buscar dados filtrados de '%s': %s", tipo, e)
        return pd.DataFrame()

    return pd.DataFrame(resp.json())


def carregar_tabela(tipo: str, ano: str, filtros: dict | None = None) -> pd.DataFrame:
    """Caso particular de carregar_serie_historica, pra um único ano."""
    return carregar_serie_historica(tipo, [ano], filtros)