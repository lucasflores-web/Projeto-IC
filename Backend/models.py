from sqlalchemy import Table, MetaData, select, and_
from database import engine, Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import text

# Metadata separada para as tabelas refletidas (anos), não interfere no Base.metadata
_reflected_metadata = MetaData()

# Cache: evita reconsultar o banco toda vez que a mesma tabela for pedida
_table_cache: dict = {}


def get_table(dataset: str, ano: str) -> Table:
    """
    dataset: 'conceito_enade' | 'cpc' | 'idd' | 'igc'
    ano: '2023', '2024', etc.
    Retorna o objeto Table refletido a partir da estrutura real no banco.
    Lança ValueError se a tabela não existir.
    """
    tablename = f"{ano}_{dataset}"

    if tablename in _table_cache:
        return _table_cache[tablename]

    try:
        table = Table(
            tablename,
            _reflected_metadata,
            autoload_with=engine,
        )
    except Exception as e:
        raise ValueError(f"Tabela '{tablename}' não encontrada ou inválida: {e}")

    _table_cache[tablename] = table
    return table


def list_available_tables(dataset: str) -> list[str]:
    #Retorna os anos disponíveis para um dataset, olhando o banco diretamente.
    from sqlalchemy import inspect
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    anos = []
    for t in all_tables:
        if t.endswith(f"_{dataset}"):
            ano = t.replace(f"_{dataset}", "")
            anos.append(ano)
    return sorted(anos)


def get_all_years_data(dataset: str) -> list[dict]:
    """
    Busca TODOS os anos disponíveis de um dataset e devolve tudo junto,
    numa lista única de dicts, cada um com uma chave extra "ano".

    Lança ValueError se não houver nenhuma tabela para o dataset.

    OBS: mantido por compatibilidade, mas prefira get_filtered_data quando
    possível — este endpoint traz o dataset inteiro, sem filtro no banco.
    """
    anos = list_available_tables(dataset)
    if not anos:
        raise ValueError(f"Nenhuma tabela encontrada para dataset '{dataset}'")

    resultado: list[dict] = []
    for ano in anos:
        table = get_table(dataset, ano)
        with engine.connect() as conn:
            rows = conn.execute(table.select()).fetchall()
        for row in rows:
            item = {col.name: getattr(row, col.name) for col in table.columns}
            item["ano"] = ano
            resultado.append(item)

    return resultado


def get_filtered_data(dataset: str, anos: list[str], filtros: dict[str, str] | None = None) -> list[dict]:
    """
    Busca dados de um dataset já filtrados no banco (WHERE), só para os anos pedidos.
    filtros: {nome_coluna_real: valor}. Colunas que não existem numa tabela
    de um ano específico são ignoradas silenciosamente (evita erro entre anos
    com esquemas levemente diferentes).
    """
    filtros = filtros or {}
    resultado: list[dict] = []

    for ano in anos:
        try:
            table = get_table(dataset, ano)
        except ValueError:
            continue

        condicoes = []
        for coluna, valor in filtros.items():
            if valor in (None, "", "Todos"):
                continue
            if coluna in table.c:
                condicoes.append(table.c[coluna] == valor)

        query = table.select()
        if condicoes:
            query = query.where(and_(*condicoes))

        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        for row in rows:
            item = {col.name: getattr(row, col.name) for col in table.columns}
            item["ano"] = ano
            resultado.append(item)

    return resultado


# Tabela fixa de mensagens continua declarativa normalmente
class Model_Mensagem(Base):
    __tablename__ = 'mensagem'
    builtin_function_id = Column(Integer, primary_key=True, nullable=False)
    titulo = Column(String, nullable=False)
    conteudo = Column(String, nullable=False)
    publicada = Column(Boolean, server_default='true', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)


from sqlalchemy import distinct

def get_distinct_values(dataset: str, column_name: str) -> list:
    """
    Busca valores distintos, validando se a coluna existe em cada tabela
    antes de executar o SQL, evitando erros de 'column does not exist'.
    """
    anos = list_available_tables(dataset)
    valores = set()

    for ano in anos:
        try:
            table = get_table(dataset, ano)

            if column_name in table.c:
                with engine.connect() as conn:
                    query = select(table.c[column_name]).distinct()
                    results = conn.execute(query).scalars().all()
                    valores.update(results)
            else:
                continue

        except Exception:
            continue

    return sorted([v for v in valores if v is not None])


def get_distinct_values_filtered(dataset: str, column_name: str, filtro_coluna: str, filtro_valor: str) -> list:
    """Como get_distinct_values, mas filtrando por outra coluna antes (ex: áreas de uma IES)."""
    anos = list_available_tables(dataset)
    valores = set()

    for ano in anos:
        try:
            table = get_table(dataset, ano)
            if column_name not in table.c or filtro_coluna not in table.c:
                continue
            with engine.connect() as conn:
                query = (
                    select(table.c[column_name])
                    .where(table.c[filtro_coluna] == filtro_valor)
                    .distinct()
                )
                results = conn.execute(query).scalars().all()
                valores.update(results)
        except Exception:
            continue

    return sorted([v for v in valores if v is not None])