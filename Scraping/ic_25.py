#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from openpyxl import load_workbook


# In[3]:


BASE_URL = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/indicadores-de-qualidade-da-educacao-superior"

# ========================================== extrai os links base por ano ==========================================
print("\n entrando na páginas para buscar os anos")

resp = requests.get(BASE_URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
tabs = soup.find("div", class_="tabs-content")

urls_por_ano = {}
# Pega a URL de cada ano (que está no atributo data-url)
if tabs:
    for tab in tabs.find_all("div", class_="tab-content"):
        ano = tab.get("data-id")
        url_aba = tab.get("data-url")

        if ano and url_aba:
            urls_por_ano[ano] = url_aba
            print(f"{ano}: {url_aba}")


# In[4]:


# ========================================== entra em cada link e pega os <a>  ==========================================
print("\n entrando nas páginas de cada ano")

arquivos_finais = []

for ano, url_pagina_ano in urls_por_ano.items():
    try:
        # Acessa a URL específica daquele ano
        r_ano = requests.get(url_pagina_ano)
        r_ano.raise_for_status()

        soup_ano = BeautifulSoup(r_ano.text, "html.parser")

        links_encontrados = soup_ano.find_all("a", href=True) # Encontra todas as tags <a> que tenham um link (href)
        for link in links_encontrados:
            href = link['href']

            # Filtro simples para pegar apenas os arquivos de dados (ajuste conforme necessidade)
            if href.endswith('.xlsx') or href.endswith('.xls'): # filtro para pegar apenas arquivos .xlsx e .xls
                print(f"[{ano}] Arquivo: {href}")
                arquivos_finais.append(ano+';'+href)
        print("\n")

    except Exception as e:
        print(f"Erro ano ")


#arquivos_finais.pop(0)##para evitar erros de ssl que esta dando devido ao enade 2025 de medicina


# In[5]:


print(f"\nN° de arquivos : {len(arquivos_finais)}")


# In[ ]:


from dotenv import load_dotenv
import os
load_dotenv(override=True) # configuração do banco e engine, override=True para carregar sempre que o .env mudar

DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

engine = create_engine(DATABASE_URL)

lista_urls = arquivos_finais


# # tratando as colunas e vizualizando n° de não correspondencia

# In[8]:


import pandas as pd
import unicodedata
import re
import json

lista_urls

# 1. Carregar o JSON 
with open('mapa.json', 'r', encoding='utf-8') as f:
    mapa = json.load(f)

mapa_colunas = {}

# Navega pela estrutura do JSON: categoria (ex: "comum") -> nome_padrao -> lista de variacoes
for categoria, colunas in mapa.items():
    for nome_padrao, variacoes in colunas.items():
        for variacao in variacoes:
            # Associa cada variação encontrada ao seu respectivo nome padrão
            # Ex: mapa_colunas["concluintes_participantes"] = "n_de_concluintes_participantes"
            mapa_colunas[variacao] = nome_padrao


def padronizar_nomes(index):

    novos_nomes = []

    for coluna in index:
        #espaços em branco e maiusculo
        coluna_limpa = str(coluna).strip().lower()
        #acentos
        coluna_limpa = ''.join(c for c in unicodedata.normalize('NFD', coluna_limpa )if unicodedata.category(c) != 'Mn')
        #caracteres especiais
        coluna_limpa = re.sub(r'[^\w\s]', '', coluna_limpa, flags=re.ASCII)
        coluna_limpa = re.sub(r'\s+', '_', coluna_limpa)

        novos_nomes.append(coluna_limpa)
    df.columns = novos_nomes

cont_ok=0
cont_not_ok=0
info_colunas_diferentes = []
for url in lista_urls:
    df = pd.DataFrame()

    #parte que eu tenho que alterar, pegar a tabela de acordo com o nome ou se n achar correspondencia pegar a maior
    '''for i in range (get_sheets(url.split(';')[1])):
        temp = pd.read_excel(url.split(';')[1],sheet_name=i)
        if len(temp)> len(df):
            df = temp'''


    if url.endswith('.xlsx'):
        df = pd.read_excel(url.split(';')[1], engine='openpyxl')
    else:
        df = pd.read_excel(url.split(';')[1], engine='xlrd')

    #df = pd.read_excel(url.split(';')[0], engine='openpyxl')
    print(f"onde estamos: {url}")
    padronizar_nomes(df.columns)

    dicionario_renomeio = {}


    #print("entrando no filtro")
    for col in df.columns:
        if col in mapa_colunas:
                cont_ok=cont_ok+1
                # Se existir, o novo nome será a chave oficial (nome_padrao)
                dicionario_renomeio[col] = mapa_colunas[col]
        else:
            cont_not_ok=cont_not_ok+1
            #Se não existir, guardamos para avisar você no print final
            info_colunas_diferentes.append(f"coluna: '{col}' ano e url: '{url}'")
    df.rename(columns=dicionario_renomeio, inplace=True) 

print(f"numeros de erros:'{cont_not_ok}', acertos:'{cont_ok}' ")
print("onde estão as diferenças:")
print(info_colunas_diferentes)


# ### mostrando os erros/oque há de diferente

# In[10]:


for i in info_colunas_diferentes:
    print(i)


# ### busca por nome da aba no xlsx - teste

# In[11]:


import pandas as pd
import json

with open("mapa_abas.json") as f:
    MAPA = json.load(f)

def filtro_por_aba(url, nome_da_tabela):
    engine = 'openpyxl' if url.endswith('.xlsx') else 'xlrd'
    excel_file = pd.ExcelFile(url, engine=engine)

    nome_arq = nome_da_tabela
    arquivos_especificos = ['2014_igc', '2015_igc', '2016_igc']
    if nome_arq in arquivos_especificos:
        nome_abas = ["universidades e ifet", "centros univ e cefet", "faculdades"]
        df_list = []
        for nome_aba in excel_file.sheet_names:
            if any(termo in nome_aba.strip().lower() for termo in nome_abas):
                df_temp = pd.read_excel(url, sheet_name=nome_aba, engine=engine)
                df_temp.columns = df_temp.columns.str.strip().str.lower()
                df_list.append(df_temp)
        if df_list:
            return pd.concat(df_list, ignore_index=True)

    for nome_aba in excel_file.sheet_names:
        nome_aba_limpo = nome_aba.strip().lower()
        for aliases in MAPA["abas"].values():
            if any(alias in nome_aba_limpo for alias in aliases):
                return pd.read_excel(url, sheet_name=nome_aba, engine=engine)

    return max(
        (pd.read_excel(url, sheet_name=aba, engine=engine) for aba in excel_file.sheet_names),
        key=len
    )

'''df = filtro_por_aba("https://download.inep.gov.br/educacao_superior/indicadores/resultados/2025/conceito_enade_licenciaturas.xlsx")
print(df.head)'''


# # salvando na tabela

# In[ ]:


import pandas as pd, requests
from io import BytesIO
from openpyxl import load_workbook
from datetime import datetime
from pathlib import Path
import re

data = datetime.now() 
cont_nomes_tratados = 0
possivel_erro_leitura = 0
cont_erros = 0
#
for url in lista_urls:#[26:38]:
    df = pd.DataFrame()
    try:

        # Pega o nome do arquivo para usar como nome da tabela (ex: arquivo1)
        nome_tabela = url.split(';')[0] + url.split('/')[-1] + data.strftime("%d/%m/%Y %H:%M:%S")#.replace('.xlsx', '').replace('.xls', '')
        print(nome_tabela)
        lower = url.lower()

        if lower.find('idd') != -1:
            nome_reduzido = lower.split(';')[0] + '_idd'
        elif lower.find('med')  != -1:
            nome_reduzido = lower.split(';')[0] + '_conceito_enade_med'
        elif lower.find('licen')  != -1:
            nome_reduzido = lower.split(';')[0] + '_conceito_enade_licenciatura'
        elif lower.find('conceito_enade')  != -1 or lower.find('resultado_enade')!= -1:
            nome_reduzido = lower.split(';')[0] + '_conceito_enade'
        elif lower.find('igc_cpc') != -1 and  lower.find('_igc_') != -1:
            nome_reduzido = lower.split(';')[0] + '_igc'
        elif lower.find('igc_cpc') != -1 and  lower.find('_cpc_') != -1:
            nome_reduzido = lower.split(';')[0] + '_cpc'
        elif lower.find('cpc') != -1:
              nome_reduzido = lower.split(';')[0] + '_cpc'
        elif lower.find('igc') != -1:
             nome_reduzido = lower.split(';')[0] + '_igc'
        elif lower.find('enade')  != -1:
            nome_reduzido = lower.split(';')[0] + '_conceito_enade'
        else:
            cont_nomes_tratados +=1

        if url.endswith('.xlsx'):
            df = pd.read_excel(url.split(';')[1], engine='openpyxl')
        else:
            df = pd.read_excel(url.split(';')[1], engine='xlrd')

        #print(f"Linhas encontradas: {len(df)}")
        df = filtro_por_aba(url.split(';')[1], nome_reduzido)#aplica o filtro por aba com base no map

        df = df.astype(str)#forçar o tipo str
        df.insert(0,id, range(1,len(df)+1))#enserir a coluda id
        if len(df) < 1000:
            possivel_erro_leitura +=1
        #print(f"{nome_reduzido}: N° de linhas {len(df)}")
        padronizar_nomes(df.columns)
        dicionario_renomeio = {}

        for col in df.columns:
            if col in mapa_colunas:
                    cont_ok=cont_ok+1
                    # Se existir, o novo nome será a chave oficial (nome_padrao)
                    dicionario_renomeio[col] = mapa_colunas[col]
            else:
                cont_not_ok=cont_not_ok+1
                #Se não existir, guardamos para avisar você no print final
                info_colunas_diferentes.append(f"coluna: '{col}' ano e url: '{url}'")

        df.rename(columns=dicionario_renomeio, inplace=True) 



        #SALVAR NO BANCO
        df.to_sql(
            name= nome_reduzido,
            con=engine,
            index=False,
        )
        print(f"'{nome_reduzido}' salvo, n° de linhas:{len(df)}, url: '{url}'")

        #SALVAR NO DISCO

        # Substitui ; / espaço . e : por _ tudo de uma vez
        nome_tratado = re.sub(r'[;/\s.:]', '_', nome_reduzido)

        pasta_destino = Path("pasta_dos_xlsx")
        pasta_destino.mkdir(parents=True, exist_ok=True)

        caminho_arquivo = pasta_destino / f"{nome_tratado}.xlsx"
        df.to_excel(caminho_arquivo, index=False)


    except Exception as e:
        print(f"Erro na URL {url}: {e}")
        cont_erros += 1

if cont_nomes_tratados > 0:
            print(cont_nomes_tratados)
else:
     print("Todos os nomes tratados")
print(f"Numeros de erros = {cont_erros}")
print(f"possiveis erros de leitura {possivel_erro_leitura}")
print("Fim do processo")


# In[13]:


print(arquivos_finais)

