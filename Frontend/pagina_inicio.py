# pagina_inicio.py
from taipy.gui import navigate

def ir_para_page(state, nome_pagina):
    navigate(state, nome_pagina)

# Layout baseado no protótipo da Página Inicial
pagina_inicio_md = """
<|layout|columns=2 1|gap=40px|
<|
# **Bem-Vindo à Plataforma<br/> de Indicadores da Educação Superior - IES360**

A plataforma reúne e disponibiliza indicadores de qualidade<br/>
da Educação Superior brasileira, permitindo consultas,<br/> 
análises e comparações entre Instituições de Educação<br/> 
Superior (IES) e cursos.
|>

<|
<|{"./img/educacao.png"}|image|width=300px|alt=IES360s|>
|>
|>

---

"""