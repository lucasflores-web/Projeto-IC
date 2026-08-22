'''
from pydantic import BaseModel
from typing import Optiona

class ConceitoEnadeSchema(BaseModel):
    builtin_function_id: int
    ano: Optional[str] = None
    codigo_da_area: Optional[str] = None
    area_de_avaliacao: Optional[str] = None
    grau_academico: Optional[str] = None
    codigo_da_ies: Optional[str] = None
    nome_da_ies: Optional[str] = None
    sigla_da_ies: Optional[str] = None
    organizacao_academica: Optional[str] = None
    categoria_administrativa: Optional[str] = None
    codigo_do_curso: Optional[str] = None
    modalidade_de_ensino: Optional[str] = None
    codigo_do_municipio: Optional[str] = None
    municipio_do_curso: Optional[str] = None
    sigla_da_uf: Optional[str] = None
    n_de_concluintes_inscritos: Optional[str] = None
    n_de_concluintes_participantes: Optional[str] = None
    nota_bruta_fg: Optional[str] = None
    nota_padronizada_fg: Optional[str] = None
    nota_bruta_ce: Optional[str] = None
    nota_padronizada_ce: Optional[str] = None
    conceito_enade_continuo: Optional[str] = None
    conceito_enade_faixa: Optional[str] = None#
    entidade_beneficiente_de_assistencia_social_cebas: Optional[str] = None#

class CPCSchema(BaseModel):
    builtin_function_id: int
    ano: Optional[str]#diferente do enade 2023 que era string
    codigo_da_area: Optional[str]
    area_de_avaliacao: Optional[str]
    codigo_da_ies: Optional[str]
    nome_da_ies: Optional[str]
    sigla_da_ies: Optional[str]
    organizacao_academica: Optional[str]
    categoria_administrativa: Optional[str]
    codigo_do_curso: Optional[str]
    modalidade_de_ensino: Optional[str]
    codigo_do_municipio: Optional[str]
    municipio_do_curso: Optional[str]
    sigla_da_uf: Optional[str]#
    n_de_concluintes_inscritos: Optional[str]
    n_de_concluintes_participantes: Optional[str]
    nota_bruta_fg: Optional[str]
    nota_padronizada_fg: Optional[str]
    nota_bruta_ce: Optional[str]
    nota_padronizada_ce: Optional[str]
    conceito_enade_continuo: Optional[str]
    entidade_beneficiente_de_assistencia_social_cebas: Optional[str]#
    #n_de_concluintes_participantes_com_nota_no_enem : Optional[int]#bigint
    proporcao_de_concluintes_participantes_com_nota_no_enem: Optional[str]
    nota_bruta_organizacao_didaticopedagogica: Optional[str]
    nota_padronizada_organizacao_didaticopedagogica: Optional[str]
    nota_bruta_infraestrutura_e_instalacoes_fisicas: Optional[str]
    nota_padronizada_infraestrutura_e_instalacoes_fisicas: Optional[str]
    nota_bruta_oportunidade_de_ampliacao_da_formacao: Optional[str]
    nota_padronizada_oportunidade_de_ampliacao_da_formacao: Optional[str]
    nota_bruta_mestres: Optional[str]
    nota_padronizada_mestres: Optional[str]
    nota_bruta_doutores: Optional[str]
    nota_padronizada_doutores: Optional[str]
    nota_bruta_regime_de_trabalho: Optional[str]
    nota_padronizada_regime_de_trabalho: Optional[str]
    cpc_continuo: Optional[str]
    cpc_faixa: Optional[str]
    entidade_beneficiente_de_assistencia_social_cebas: Optional[str]

class IDDSchema(BaseModel):
    builtin_function_id: int
    ano: Optional[str]
    codigo_da_area: Optional[str]
    area_de_avaliacao: Optional[str]
    codigo_da_ies: Optional[str]
    nome_da_ies: Optional[str]
    sigla_da_ies: Optional[str]
    organizacao_academica: Optional[str]
    categoria_administrativa: Optional[str]
    codigo_do_curso: Optional[str]
    modalidade_de_ensino: Optional[str]
    codigo_do_municipio: Optional[str]
    municipio_do_curso: Optional[str]
    sigla_da_uf: Optional[str]#
    n_de_concluintes_inscritos: Optional[str]
    n_de_concluintes_participantes: Optional[str]
    #n_de_concluintes_participantes_com_nota_no_enem = Optional[str]#agora diferente do cpc é dp, e não bigint
    proporcao_de_concluintes_participantes_com_nota_no_enem: Optional[str]
    nota_bruta_idd: Optional[str]
    idd_continuo: Optional[str]
    idd_faixa: Optional[str]
    #entidade_beneficiente_de_assistencia_social_cebas: Optional[str]#
    '''