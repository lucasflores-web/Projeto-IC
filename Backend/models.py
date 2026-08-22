from sqlalchemy import Table, MetaData, select, and_, inspect
from database import engine

metadata = MetaData()

def get_table(dataset: str, ano: str) -> Table:
    tablename = f"{ano}_{dataset}"
    return Table(tablename, metadata, autoload_with=engine)


def list_available_tables(dataset: str) -> list[str]:
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    return sorted(
        t.replace(f"_{dataset}", "")
        for t in all_tables
        if t.endswith(f"_{dataset}")
    )


def get_filtered_data(dataset: str, anos: list[str], filtros: dict[str, str] | None = None) -> list[dict]:
    filtros = filtros or {}
    resultado = []

    for ano in anos:
        table = get_table(dataset, ano)

        condicoes = [
            table.c[coluna] == valor
            for coluna, valor in filtros.items()
            if valor not in (None, "", "Todos") and coluna in table.c
        ]

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


def get_distinct_values(dataset: str, column_name: str) -> list:
    valores = set()
    for ano in list_available_tables(dataset):
        table = get_table(dataset, ano)
        if column_name in table.c:
            with engine.connect() as conn:
                valores.update(conn.execute(select(table.c[column_name]).distinct()).scalars().all())
    return sorted(v for v in valores if v is not None)


def get_distinct_values_filtered(dataset: str, column_name: str, filtro_coluna: str, filtro_valor: str) -> list:
    valores = set()
    for ano in list_available_tables(dataset):
        table = get_table(dataset, ano)
        if column_name in table.c and filtro_coluna in table.c:
            with engine.connect() as conn:
                query = select(table.c[column_name]).where(table.c[filtro_coluna] == filtro_valor).distinct()
                valores.update(conn.execute(query).scalars().all())
    return sorted(v for v in valores if v is not None)