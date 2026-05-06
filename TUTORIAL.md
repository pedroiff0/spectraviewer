# Tutorial de Uso - SpectraViewer

Um guia passo a passo para usar o SpectraViewer e explorar espectros de estrelas do GALAH DR4.

## Sumário

1. [Primeiros Passos](#primeiros-passos)
2. [Pesquisando Estrelas](#pesquisando-estrelas)
3. [Interpretando Espectros](#interpretando-espectros)
4. [Usando Linhas Espectrais](#usando-linhas-espectrais)
5. [Classificação Espectral](#classificação-espectral)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Perguntas Frequentes](#perguntas-frequentes)

---

## Primeiros Passos

### Instalação Inicial

```bash
# 1. Navegue até o diretório do projeto
cd ~/Documents/Repositorios/Academicos/spectraviewer

# 2. Ative o ambiente virtual
source venv/bin/activate

# 3. Instale as dependências (se não estiverem instaladas)
pip install -r requirements.txt

# 4. Inicie a aplicação
streamlit run spectraviewer.py
```

A aplicação será aberta automaticamente em seu navegador em `http://localhost:8501`.

### Interface Principal

```
┌─────────────────────────────────────────┐
│     GALAH DR4 Spectra Viewer            │
│                                         │
│  Pesquise um sobject_id para carregar   │
│  e visualizar as quatro bandas          │
└─────────────────────────────────────────┘

┌─ SIDEBAR (Esquerda) ────────────────────┐
│ 📊 Search                               │
│   sobject_id: [________________]        │
│   [Search] button                       │
│                                         │
│ 🔬 Spectral lines (GALAH DR4)           │
│   Show groups: [multiselect]            │
│   ☑ Show spectral lines                 │
│   ☐ Show line labels                    │
│                                         │
│ ℹ️ About                                 │
└─────────────────────────────────────────┘

┌─ MAIN AREA (Direita) ───────────────────┐
│ Dataset │ Bands │ Mode                  │
│ ────────────────────────────────────────│
│ 📊 Loaded Bands │ 📁 Files │ 🔬 Metadata│
│ ────────────────────────────────────────│
│                                         │
│ [Interactive Plot - 4 Subplots]        │
│                                         │
└─────────────────────────────────────────┘
```

---

## Pesquisando Estrelas

### Passo 1: Obter um sobject_id

O SpectraViewer funciona com **sobject_ids** - identificadores únicos de 15 dígitos para cada observação espectral.

**Formato**: `YYMMDDSSSSSCCC`
- `YYMMDD`: Data de observação (ano, mês, dia)
- `SSSSS`: Identificador da estrela/campo
- `CCC`: Campo interno

**Exemplo válido**: `131216001101025`

### Passo 2: Digitar o ID

1. Localize o campo **"sobject id"** na barra lateral esquerda
2. Digite um ID válido (vazio = usa o padrão `131216001101090`)
3. Clique no botão **"Search"**

### Passo 3: Esperando o Carregamento

A aplicação:
1. ✅ Localiza os 4 arquivos FITS correspondentes
2. ✅ Lê os dados espectrais e metadados
3. ✅ Processa as wavelengths
4. ✅ Gera a visualização

**Tempo típico**: 2-5 segundos

### Exemplo com IDs no Arquivo

Se você tiver o arquivo `class.txt`, IDs válidos incluem:
```
131216001101025
131216001101028
131216001101084
131216001101090
```

---

## Interpretando Espectros

### Estrutura do Plot

O SpectraViewer mostra **4 subplots**, um para cada CCD (banda espectral):

```
┌─────────────────────────────────────────┐
│ CCD 1 - Blue (4713 Å)                   │  ← Ultravioleta próximo
│ [Flux vs Wavelength]                    │
├─────────────────────────────────────────┤
│ CCD 2 - Green (5648 Å)                  │  ← Luz visível
│ [Flux vs Wavelength]                    │
├─────────────────────────────────────────┤
│ CCD 3 - Red (6478 Å)                    │  ← Luz visível
│ [Flux vs Wavelength]                    │
├─────────────────────────────────────────┤
│ CCD 4 - IR (7585 Å)                     │  ← Infravermelho próximo
│ [Flux vs Wavelength]                    │
└─────────────────────────────────────────┘
```

### Eixos

- **X (Wavelength)**: Comprimento de onda em Ångströms (Å)
- **Y (Normalised Flux)**: Fluxo normalizado da radiação estelar
- **Unidade wavelength**: 1 Å = 0.1 nm

### Lendo o Espectro

**Características Principais**:

1. **Continuum**: Linha base suave = radiação térmica da estrela
2. **Absorption Lines**: Dips nos espectro = elementos absorvendo luz (linhas escuras)
3. **Emission Lines**: Picos acima do continuum = emissão (raro em GALAH)
4. **Noise**: Flutuações aleatórias = ruído observacional

**Exemplo Visual**:
```
Flux
  1.0 |     ╱╲      ← Continuum
      |    ╱  ╲      
  0.8 |  ╱      ╲    
      | V        V   ← Absorption lines
  0.6 |║  ║      ║║  
      | |  |      ||  
  0.4 |_|__|______|_  
      +━━━━━━━━━━━━━  Wavelength
     4700          4800 Å
```

### Interatividade

- **Hover**: Passe o mouse sobre pontos para ver λ e Flux
- **Zoom**: Arraste para selecionar uma região, double-click para resetar
- **Pan**: Clique + arraste (com a tecla de pan ativa)
- **Exportar**: Ícone de câmera no topo do gráfico → PNG

---

## Usando Linhas Espectrais

### O que são Linhas Espectrais?

Linhas espectrais são comprimentos de onda específicos onde átomos e moléculas absorvem luz. Cada elemento (Fe, Mg, Ca, etc.) tem um padrão único de linhas.

### Ativar Linhas

1. Na barra lateral, encontre **"Show groups"**
2. Selecione os grupos desejados (ex: "All", "Alpha-process", "Iron-peak")
3. Marque ☑ **"Show spectral lines"**

### Grupos Disponíveis

| Grupo | Elementos | Cor | Uso Científico |
|-------|-----------|-----|---|
| **All** | Todos | Preto | Visão geral completa |
| **CNO** | C, N, O | Verde | Nucleossíntese |
| **Alpha-process** | Mg, Si, Ca, Ti | Azul | Supernovas tipo II |
| **Light Odd-Z** | Na, Al, K, Sc | Laranja | Formação de galáxias |
| **Iron-peak** | V, Cr, Mn, Fe, Co, Ni | Roxo | Processo r e s |
| **Post iron-peak** | Cu, Zn | Marrom | Nucleossíntese |
| **Neutron capture strong** | Y, Ba, La, Nd, Eu | Rosa | Processo r rápido |
| **Neutron capture weak** | Rb, Sr, Zr, Mo, Ce, Sm | Cinza | Processo s lento |
| **Miscellaneous** | H, Li, Dy, Ru | Vermelho | Especiais |

### Exibir Etiquetas

1. Marque ☑ **"Show line labels"**
2. As linhas visíveis serão etiquetadas com:
   - Nome do elemento
   - Wavelength em repouso vs observada (se RV aplicável)

**Exemplo com etiqueta**:
```
      H_alpha        Mg_b
        ↓             ↓
Flux  ─────────────────────
      λ rest → λ obs
      6562.8 → 6563.1 Å
```

### Interpretando Velocidade Radial (RV)

Se a estrela tem movimento radial (RV ≠ 0):
- **Redshift (RV > 0)**: Estrela se afastando → linhas se deslocam para comprimentos de onda maiores (vermelho)
- **Blueshift (RV < 0)**: Estrela se aproximando → linhas se deslocam para comprimentos de onda menores (azul)

---

## Classificação Espectral

### Tipos Espectrais

O SpectraViewer classifica automaticamente a estrela usando a **Sequência de Harvard**:

```
O ─→ B ─→ A ─→ F ─→ G ─→ K ─→ M
(Quente)                      (Fria)
```

### Classificação por Temperatura

```python
Teff (K)    Tipo Espectral    Características
≥ 25000        O             Quentes, azuis, massivas
10000-25000    B             Azuis-brancas
7500-10000     A             Brancas
6000-7500      F             Amarelo-brancas
5000-6000      G             Amarelas (Sol = G2V)
3500-5000      K             Laranja
< 3500         M             Vermelhas, frias
```

### Exemplo de Classificação

**Entrada**: `TEFF_R = 5777 K` (do header FITS)  
**Saída**: Tipo espectral = **G**

O SpectraViewer exibe essa classificação no painel de metadados.

### Visualização de Teff

Procure no painel **"🔬 Metadata"**:
```
TEFF_R:        5777
LOGG_R:        4.43
FE_H_R:       -0.05
A_FE_R:        0.00
SNR_AA:        150.2
RV:             -0.5
E_RV:            0.1
```

---

## Exemplos Práticos

### Exemplo 1: Estudar o Sol

**ID**: Use um tipo G (ex: `131216001101090`, que é tipo M)

**Passos**:
1. Digite `131216001101090` e clique Search
2. Observe o espectro em 4 bandas
3. Ative "All" em linhas espectrais
4. Compare com o espectro solar conhecido

**O que procurar**:
- Linhas de H-alpha (6562.8 Å)
- Linhas de Mg (5172, 5183 Å)
- Linhas de Na D (5889, 5895 Å)

### Exemplo 2: Comparar Tipos Espectrais

1. Pesquise `131216001101025` (Tipo K)
2. Anote o Teff e características do espectro
3. Pesquise `131216001101084` (Tipo M)
4. Compare:
   - Qual é mais avermelhado?
   - Qual tem Teff maior?
   - Como as linhas espectrais diferem?

### Exemplo 3: Análise de Abundâncias

1. Pesquise uma estrela
2. Abra o painel "🔬 Metadata"
3. Observe:
   - **FE_H_R**: Metalicidade ([Fe/H])
     - Negativo = pobre em metais (antiga)
     - Positivo = rica em metais (jovem)
   - **A_FE_R**: Abundância [α/Fe]
     - Alto = formação rápida
     - Baixo = formação lenta

---

## Perguntas Frequentes

### P1: Como obtenho novos sobject_ids?

**R**: O arquivo `class.txt` contém IDs válidos. Você pode também:
- Consultar o catálogo GALAH em https://www.galah-survey.org/
- Usare bancos de dados como VizieR ou SIMBAD

### P2: Posso exportar os dados espectrais?

**R**: Atualmente o SpectraViewer é apenas visualização. Para exportar:
1. Use o ícone de câmera para salvar o gráfico (PNG)
2. Para dados FITS brutos: acesse diretamente `data/spectra/.../*.fits`
3. Use ferramentas como `astropy.fits` para análise posterior em Python

### P3: Por que algumas linhas não aparecem?

**R**: Possíveis razões:
- A wavelength não está coberta por aquele CCD
- A linha está no continuum ou muito fraca
- O grupo selecionado não contém aquela linha
- Redshift/blueshift deixou a linha fora do intervalo

### P4: O que é SNR_AA?

**R**: Razão Sinal-Ruído por Ångström. Indica a qualidade do espectro:
- **SNR > 100**: Excelente
- **SNR 50-100**: Bom
- **SNR < 50**: Marginal

Espectros com SNR baixo têm mais ruído nas linhas.

### P5: Como aplico Streamlit em Vercel?

**R**: Veja [README.md - Deploy na Vercel](./README.md#-deploy-na-vercel)

### P6: Posso usar isso offline?

**R**: Sim! Desde que:
1. O venv esteja ativo (`source venv/bin/activate`)
2. Os dados FITS estejam em `data/spectra/...`
3. Você execute `streamlit run spectraviewer.py` localmente

### P7: Qual é a diferença entre CCD 1, 2, 3, 4?

**R**: São 4 detectores diferentes:
- **CCD 1 (Blue)**: 4700-4900 Å (violeta)
- **CCD 2 (Green)**: 5600-5700 Å (verde)
- **CCD 3 (Red)**: 6400-6600 Å (vermelho)
- **CCD 4 (IR)**: 7500-7700 Å (infravermelho próximo)

Juntos cobrem o intervalo óptico-IV próximo completo.

### P8: Como leio um arquivo FITS manualmente?

**R**: Em Python:
```python
from astropy.io import fits
import numpy as np

# Abrir FITS
with fits.open('spectra.fits') as hdul:
    header = hdul[0].header
    flux = hdul[1].data
    
# Extrair wavelength
crval1 = header['CRVAL1']  # Wavelength no primeiro pixel
cdelt1 = header['CDELT1']  # Delta wavelength por pixel
n_pix = len(flux)
wavelength = crval1 + np.arange(n_pix) * cdelt1

print(f"Wavelength range: {wavelength[0]:.1f} - {wavelength[-1]:.1f} Å")
```

---

## Dicas e Truques

💡 **Dica 1**: Use "All" para uma visão completa, depois filtre grupos específicos

💡 **Dica 2**: Desabilite labels quando há muitas linhas muito próximas

💡 **Dica 3**: Compare espectros de mesma data (YYMMDD) para validar calibração

💡 **Dica 4**: Use o zoom do Plotly para estudar detalher finas de linhas

💡 **Dica 5**: Correlacione Teff com o continuum shape (mais quente = mais azul)

---

## Próximos Passos

- 📚 Leia o [README.md](./README.md) para mais contexto
- 🔬 Explore dados do [GALAH Survey](https://www.galah-survey.org/)
- 🐍 Modifique `spectraviewer.py` para adicionar suas próprias análises
- 🌐 Faça deploy na Vercel (veja instruções no README)

---

**Versão**: 1.0.0  
**Última atualização**: Maio 2026

Para ajuda adicional, abra uma issue no repositório ou consulte a documentação do Streamlit.
