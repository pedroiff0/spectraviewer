# SpectraViewer - GALAH DR4 Spectra Viewer

Um visualizador interativo de espectros do catálogo GALAH DR4 (Gaia-ESO Spectroscopic Survey Data Release 4). A aplicação permite explorar espectros de estrelas de forma intuitiva, com suporte a múltiplas bandas, linhas espectrais de referência e classificação espectral automática.

## 🌟 Características

- **Visualização Interativa**: Plotagem de 4 bandas espectrais (Blue, Green, Red, IR) com interface interativa
- **Classificação Espectral**: Classificação automática das estrelas (O, B, A, F, G, K, M) baseada em temperatura efetiva
- **Linhas Espectrais**: Overlay de linhas espectrais de referência do GALAH DR4 com grupos (CNO, Alpha-process, Iron-peak, etc.)
- **Dados Locais**: Leitura direta de arquivos FITS do dataset local
- **Metadados Estelares**: Exibição de informações como Teff, log(g), [Fe/H] e outras abundâncias

## 📋 Requisitos

- Python 3.8+
- Datasets GALAH DR4 (FITS files)

## ⚙️ Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd spectraviewer
```

### 2. Crie um ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Executar localmente

```bash
streamlit run spectraviewer.py
```

A aplicação será aberta em `http://localhost:8501`.

### Usar a aplicação

1. **Pesquisa**: Digite um `sobject_id` de 15 dígitos no campo de pesquisa
2. **Visualizar Espectro**: O espectro das 4 bandas será carregado e exibido
3. **Linhas Espectrais**: Selecione grupos de linhas espectrais para sobrepô-las ao espectro
4. **Etiquetas**: Ative a opção "Show line labels" para mostrar identificações de linhas

## 📊 Estrutura de Dados

### Espectros FITS
- Localização: `data/spectra/galah/dr4/spectra/hermes/com/{YYMMDD}/`
- Arquivo: `{sobject_id}{CCD}.fits`
- Bandas:
  - CCD 1: Blue (~4713 Å)
  - CCD 2: Green (~5648 Å)  
  - CCD 3: Red (~6478 Å)
  - CCD 4: IR (~7585 Å)

### Metadados FITS
- TEFF_R: Temperatura efetiva
- LOGG_R: log(g) - gravidade superficial
- FE_H_R: Metalicidade [Fe/H]
- A_FE_R: Abundância [α/Fe]
- SNR_AA: Razão sinal-ruído em Ångströms
- RV: Velocidade radial
- E_RV: Erro na velocidade radial

## 🔬 Classificação Espectral

A classificação segue a sequência OBAFGKM baseada na temperatura efetiva (Teff):

| Tipo | Teff (K) |
|------|----------|
| O | ≥ 25000 |
| B | 10000 - 24999 |
| A | 7500 - 9999 |
| F | 6000 - 7499 |
| G | 5000 - 5999 |
| K | 3500 - 4999 |
| M | < 3500 |

## 🌐 Deploy na Streamlit Cloud

A forma mais simples e recomendada para fazer deploy da aplicação.

### Passos

1. **Faça push do repositório para GitHub**
   ```bash
   git add .
   git commit -m "Add SpectraViewer"
   git push origin main
   ```

2. **Acesse Streamlit Cloud**
   - Vá para https://streamlit.io/cloud
   - Clique em "Sign up" e autentique com sua conta GitHub

3. **Crie uma nova app**
   - Clique em "New app"
   - Selecione seu repositório `spectraviewer`
   - Configure:
     - Main file path: `spectraviewer.py`
     - Python version: 3.9+

4. **Deploy**
   - A aplicação será deployada automaticamente
   - URL: `https://{seu-username}-spectraviewer-{random}.streamlit.app`

### Dados FITS

Para funcionar na nuvem, você tem duas opções:

**Opção 1 - Incluir no repositório** (recomendado para datasets pequenos)
```bash
git lfs install  # GitHub Large File Storage
git lfs track "data/spectra/**/*.fits"
git add data/spectra/
git commit -m "Add FITS spectra"
```

**Opção 2 - Usar armazenamento remoto** (recomendado para datasets grandes)
Adicione ao `spectraviewer.py`:
```python
import s3fs  # para Amazon S3

SPECTRA_ROOT = s3fs.S3FileSystem().open("s3://bucket/spectra/")
```

## 📚 Referências

- [GALAH DR4 Survey](https://www.galah-survey.org/)
- [Gaia-ESO Spectroscopic Survey](http://www.gaia-eso.eu/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Astropy FITS](https://docs.astropy.org/en/stable/io/fits/)

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
spectraviewer/
├── spectraviewer.py          # Aplicação principal
├── requirements.txt          # Dependências Python
├── class.txt                 # Catálogo de classificação espectral
├── data/                     # Dados (não incluído, baixe separadamente)
│   ├── spectra/              # Arquivos FITS dos espectros
│   └── galah_dr4_lines.csv   # Linhas espectrais de referência
├── venv/                     # Ambiente virtual
└── README.md                 # Este arquivo
```

### Adicionar Novas Funcionalidades

1. Modifique `spectraviewer.py`
2. Teste localmente: `streamlit run spectraviewer.py`
3. Commit e push para GitHub

## 🐛 Troubleshooting

### "File not found" para espectros
- Verifique se os arquivos FITS existem em `data/spectra/galah/dr4/spectra/hermes/com/`
- Confirme que o `sobject_id` está correto (15 dígitos)

### Linhas espectrais não aparecem
- Verifique se `data/galah_dr4_lines.csv` existe
- Confirme que as wavelengths das linhas estão dentro do intervalo de cobertura do espectro

### Performance lenta
- Redimensione os gráficos
- Reduza o número de grupos de linhas selecionados
- Verifique a velocidade de leitura do disco para arquivos FITS

## 📝 Licença

Este projeto utiliza dados do GALAH DR4 Survey. Respeite os termos de uso dos dados.

## 👥 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📧 Suporte

Para questões, bug reports ou sugestões, abra uma issue no repositório.

---

**Última atualização**: Maio 2026  
**Versão**: 1.0.0
