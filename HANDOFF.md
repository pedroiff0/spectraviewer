# HANDOFF — SpectraViewer

## 1. Contexto Rápido
- **Repositório:** `pedroiff0/spectraviewer` (`~/Repositorios/pesquisa/spectraviewer`).
- **Função Principal:** Aplicativo Streamlit de análise espectroscópica interativa para visualização de linhas atômicas e moleculares em espectros estelares.
- **Porta Padrão:** 8501 (`http://localhost:8501`).

## 2. Arquitetura & Stack
- **Framework:** Python 3.10+ / Streamlit.
- **Visualização:** Plotly para gráficos interativos de alta resolução.
- **Dados Astronômicos:** Astropy e SciPy para manipulação de tabelas FITS e interpolação de contínuo.

## 3. Estado Atual & Diretrizes Operacionais
- **Governança:** AGENTS.md, DESIGN.md, Makefile e templates do GitHub ativos.
- **Comandos Principais:**
  - `make help`: Exibe comandos disponíveis.
  - `make install`: Instala dependências do `requirements.txt`.
  - `make run`: Inicia a aplicação Streamlit (`streamlit run spectraviewer.py`).
  - `make lint`: Verifica sintaxe dos arquivos Python.
- **Próximos Passos:**
  - Integrar catálogo de linhas espectrais padrão do NIST e GALAH diretamente na barra lateral de identificação.
