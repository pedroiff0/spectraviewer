# AGENTS.md — SpectraViewer (Visualizador de Espectros Estelares)

> Diretrizes e regras operacionais para Agentes de IA no repositório `spectraviewer`.

---

## 1. Visão Geral
- **Repositório:** `pedroiff0/spectraviewer` (`~/Repositorios/pesquisa/spectraviewer`).
- **Propósito:** Aplicação interativa em Streamlit para visualização, comparação e classificação de espectros estelares, identificação de linhas de emissão/absorção e análise comparativa de modelos sintéticos.
- **Stack:** Python 3.10+, Streamlit, Plotly, NumPy, SciPy, Astropy.

---

## 2. Regras Operacionais para Agentes
1. **Otimização de Renderização:**
   - Usar amostragem inteligente de pontos ao renderizar espectros de alta resolução para evitar lentidão no navegador.
2. **Modularidade:**
   - Manter funções de parsing e normalização de fluxo desacopladas dos componentes visuais do Streamlit.
3. **CI/CD:**
   - Validações rápidas de sintaxe com timeout máximo de 5 minutos (`timeout-minutes: 5`).
