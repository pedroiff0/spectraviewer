.PHONY: help install run lint

help: ## Exibe a lista de comandos disponíveis
	@echo "Comandos disponíveis em SpectraViewer:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências do requirements.txt
	pip install -r requirements.txt

run: ## Inicia o aplicativo Streamlit localmente
	streamlit run spectraviewer.py

lint: ## Verifica a sintaxe dos arquivos Python
	python3 -m py_compile spectraviewer.py
	@echo "Sintaxe validada com sucesso."
