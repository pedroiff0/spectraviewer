# Setup Guide - SpectraViewer

Guia de configuração inicial para executar o SpectraViewer localmente.

## ✅ Checklist de Configuração

- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Repositório clonado
- [ ] Venv criado e ativado
- [ ] Dependências instaladas
- [ ] Dados FITS baixados/configurados
- [ ] Aplicação testada

## 🚀 Instruções Passo a Passo

### 1. Clonar o Repositório

```bash
git clone <repository-url>
cd spectraviewer
```

### 2. Criar Ambiente Virtual

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências:**
- streamlit>=1.28.0 - Framework web
- plotly>=5.17.0 - Gráficos interativos
- pandas>=2.0.0 - Manipulação de dados
- numpy>=1.24.0 - Computação numérica
- astropy>=5.3.0 - Leitura de FITS

### 4. Configurar Dados FITS

Os espectros FITS devem estar em:
```
spectraviewer/
└── data/
    └── spectra/
        └── galah/
            └── dr4/
                └── spectra/
                    └── hermes/
                        └── com/
                            ├── 131216/     ← Data (YYMMDD)
                            │   ├── 1312160011010251.fits
                            │   ├── 1312160011010252.fits
                            │   ├── 1312160011010253.fits
                            │   └── 1312160011010254.fits
                            └── ...
```

**Como estruturar:**
1. Baixe os arquivos FITS do GALAH DR4
2. Organize por data em `YYMMDD/`
3. Nomeie como `{sobject_id}{CCD}.fits` onde CCD ∈ {1,2,3,4}

**Alternativa:** Se usar dados de teste, copie espectros de exemplo:
```bash
# Criar estrutura de diretórios
mkdir -p data/spectra/galah/dr4/spectra/hermes/com/131216

# Os arquivos FITS devem ser adicionados manualmente
```

### 5. Executar Localmente

```bash
streamlit run spectraviewer.py
```

**Saída esperada:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Abra a URL em seu navegador.

### 6. Testar a Aplicação

1. Digite `131216001101090` no campo "sobject id"
2. Clique "Search"
3. Deve aparecer:
   - 4 subplots de espectros
   - Painel com informações de bandas
   - Painel com arquivos
   - Painel com metadados (incluindo classificação espectral)

## 📊 Estrutura de Arquivos

```
spectraviewer/
├── spectraviewer.py          # 🎯 Aplicação principal
├── streamlit_app.py          # Alias para alguns servidores
├── class.txt                 # Catálogo de classificações (4 estrelas de teste)
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação principal
├── TUTORIAL.md               # Guia de uso
├── SETUP.md                  # Este arquivo
├── DEPLOYMENT.md             # Guia de deployment
├── .gitignore                # Arquivos a ignorar no Git
├── .streamlit/
│   └── config.toml           # Configuração Streamlit
├── venv/                     # Ambiente virtual
├── data/
│   ├── spectra/              # 📂 Dados FITS (não incluído)
│   └── galah_dr4_lines.csv   # Linhas espectrais de referência
└── .github/                  # GitHub workflows (opcional)
```

## 🔧 Configurações Opcionais

### 1. Customizar Tema Streamlit

Edite `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF5C4D"
backgroundColor = "#F0F4FB"
font = "sans serif"
```

### 2. Variáveis de Ambiente

Crie `.env`:
```bash
SPECTRA_ROOT=/caminho/para/espectros
DATA_ROOT=/caminho/para/dados
STREAMLIT_SERVER_PORT=8501
```

### 3. Usar com Dados Remotos

Se preferir dados em bucket S3:
```python
# No início de spectraviewer.py
import os
from pathlib import Path

SPECTRA_ROOT = Path(os.getenv("SPECTRA_ROOT", "data/spectra/..."))
# Adicionar suporte S3 com boto3
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'streamlit'"

**Solução:**
```bash
# Verifique se venv está ativado
which python  # Deve mostrar .../venv/bin/python

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "FileNotFoundError: Arquivo FITS não encontrado"

**Solução:**
```bash
# Verifique a estrutura de diretórios
ls -la data/spectra/galah/dr4/spectra/hermes/com/131216/

# O arquivo deve ser nomeado como:
# {sobject_id}{CCD}.fits
# Exemplo: 1312160011010251.fits (CCD=1)
```

### Erro: "FITS file not found for CCD 1"

**Causa:** Arquivo FITS não existe ou está mal nomeado

**Solução:**
```bash
# Verificar nomeação correta
# Padrão esperado: YYMMDDSSSSSCCC.fits
# Exemplo: 131216001101025{1,2,3,4}.fits

# Renomear se necessário
mv old_name.fits 1312160011010251.fits
```

### Lentidão na Aplicação

**Causas possíveis:**
- Disco lento
- Muitos pontos de dados nos gráficos
- Muitas linhas espectrais sobrepostas

**Soluções:**
1. Use SSD se possível
2. Reduza a resolução dos gráficos
3. Filtre grupos de linhas espectrais

### Gráficos Não Aparecem

**Solução:**
```bash
# Verifique se o Plotly está instalado corretamente
pip install --upgrade plotly

# Reinicie a aplicação
streamlit run spectraviewer.py
```

## 📚 Próximos Passos

1. ✅ Leia [README.md](./README.md)
2. ✅ Explore [TUTORIAL.md](./TUTORIAL.md)
3. ✅ Configure dados FITS
4. ✅ Execute localmente
5. ✅ Estude espectros
5. ✅ Deploy em Streamlit Cloud (veja [DEPLOYMENT.md](./DEPLOYMENT.md))

## 📞 Suporte

Se encontrar problemas:
1. Verifique as mensagens de erro
2. Consulte [TUTORIAL.md](./TUTORIAL.md) → Troubleshooting
3. Abra uma issue no GitHub
4. Consulte documentação do Streamlit: https://docs.streamlit.io

## 🎓 Recursos Educacionais

- [GALAH Survey](https://www.galah-survey.org/)
- [Espectroscopia Estelar (Wikipedia)](https://en.wikipedia.org/wiki/Stellar_spectroscopy)
- [Classificação Espectral (Wikipedia)](https://en.wikipedia.org/wiki/Stellar_classification)
- [FITS Format (NASA)](https://fits.gsfc.nasa.gov/)
- [Python Astropy](https://www.astropy.org/)

---

**Versão**: 1.0.0  
**Última atualização**: Maio 2026

Divirta-se explorando espectros! 🔬⭐
