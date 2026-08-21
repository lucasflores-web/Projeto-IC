from taipy.gui import Gui

# Importando o conteúdo de cada arquivo/página
from pagina_inicio import pagina_inicio_md
from pagina_ies import *
from pagina_cursos import *
from pagina_panorama import pagina_panorama_md
from pagina_comparar import *

import warnings

# Filtra e ignora a mensagem específica sobre colunas duplicadas
warnings.filterwarnings(
    "ignore", 
    message="DataFrame columns are not unique", 
    category=UserWarning
)

# Página Raiz: Tudo o que estiver aqui aparecerá no TOPO DE TODAS AS PÁGINAS
root_md = """
<|layout|columns=100px 1fr|
<| 
<|{"img/IES_360.png"}|image|width=50px|alt=IES360s|>
|>

<|
<|navbar|>
|>
|>
"""

# Dicionário que monta o Menu Superior exatamente na ordem do seu cabeçalho
pages = {
    "/": root_md,                     # Cabeçalho 
    "Inicio": pagina_inicio_md,       # Aba 1
    "IES": pagina_ies_md,             # Aba 2
    "Cursos-Areas": pagina_cursos_md, # Aba 3
    "Panorama": pagina_panorama_md,   # Aba 4
    "Comparar": pagina_comparar_md    # Aba 5
}

if __name__ == "__main__":
    gui = Gui(pages=pages)
    gui.run(title="IES360 - Indicadores da Educação Superior", port=5000, dark_mode=False)