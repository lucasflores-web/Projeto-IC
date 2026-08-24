import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("RENDER_API_URL")


def buscar_anos_disponiveis(tipo: str) -> list[str]:
    resp = requests.get(f"{API_URL}/anos_disponiveis/{tipo}", timeout=90)
    resp.raise_for_status()
    return resp.json().get("anos", [])


def buscar_valores_filtro(tipo: str, coluna: str) -> list[str]:
    resp = requests.get(f"{API_URL}/filtros/{tipo}/{coluna}", timeout=90)
    resp.raise_for_status()
    return sorted(resp.json().get("valores", []))


def buscar_valores_filtro_condicionado(tipo: str, coluna: str, filtro_coluna: str, filtro_valor: str) -> list[str]:
    if not filtro_valor:
        return []
    url = f"{API_URL}/filtros/{tipo}/{coluna}/por/{filtro_coluna}"
    resp = requests.get(url, params={"valor": filtro_valor}, timeout=90)
    resp.raise_for_status()
    return sorted(resp.json().get("valores", []))


def carregar_serie_historica(tipo: str, anos: list[str], filtros: dict | None = None) -> pd.DataFrame:
    filtros = filtros or {}
    params = [("anos", ano) for ano in anos]
    for coluna, valor in filtros.items():
        if valor not in (None, "", "Todos"):
            params.append((coluna, valor))

    resp = requests.get(f"{API_URL}/dados_filtrados/{tipo}", params=params, timeout=90)
    resp.raise_for_status()
    return pd.DataFrame(resp.json())


def carregar_tabela(tipo: str, ano: str, filtros: dict | None = None) -> pd.DataFrame:
    return carregar_serie_historica(tipo, [ano], filtros)