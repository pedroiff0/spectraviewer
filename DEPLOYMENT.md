# Deployment Guide - SpectraViewer

Guia para fazer deploy do SpectraViewer em Streamlit Cloud.

## 🚀 Streamlit Cloud (Recomendado)

A forma mais simples e rápida de fazer deploy.

### Vantagens
- ✅ Sem configuração complexa
- ✅ Deploy automático com GitHub
- ✅ Suporte completo para Streamlit
- ✅ Free tier generoso
- ✅ HTTPS automático
- ✅ Domínio personalizado disponível

### Requisitos

- Repositório GitHub público
- Conta Streamlit Cloud (gratuita)
- Arquivo `requirements.txt` atualizado

### Passo 1: Preparar o Repositório

```bash
# Garantir que requirements.txt está atualizado
pip freeze > requirements.txt

# Adicionar ao Git
git add requirements.txt
git commit -m "Update requirements"
git push origin main
```

### Passo 2: Configurar Streamlit Cloud

1. **Acesse** https://streamlit.io/cloud
2. **Faça login** com sua conta GitHub (ou crie uma)
3. **Clique** em "New app"

### Passo 3: Selecionar Repositório

Na interface "New app":
- **Repository**: `seu-usuario/spectraviewer`
- **Branch**: `main` (ou sua branch padrão)
- **Main file path**: `spectraviewer.py`

### Passo 4: Deploy

Clique em "Deploy" e aguarde (2-5 minutos).

**URL gerada**: 
```
https://{seu-usuario}-spectraviewer-{random-string}.streamlit.app
```

### Passo 5: Compartilhar

- A app está público e pode ser acessada por qualquer pessoa
- Compartilhe a URL com colegas/colaboradores

## 📊 Gerenciar Dados FITS

### Opção 1: GitHub LFS (Recomendado para <1GB)

```bash
# Instalar Git LFS
git lfs install

# Rastrear arquivos FITS
git lfs track "data/spectra/**/*.fits"
git add .gitattributes data/spectra/

# Commit e push
git commit -m "Add FITS spectra data"
git push origin main
```

**Limite**: GitHub oferece 1GB grátis; depois cobra por uso adicional.

### Opção 2: Armazenamento em Nuvem (Recomendado para >1GB)

#### Amazon S3

1. **Criar bucket S3** com dados FITS
2. **Instalar boto3**:
   ```bash
   pip install boto3
   echo "boto3>=1.26.0" >> requirements.txt
   ```

3. **Modificar espectraviewer.py**:
   ```python
   import os
   import boto3
   from pathlib import Path
   
   # Detectar se está em Streamlit Cloud
   if "STREAMLIT_SERVER_HEADLESS" in os.environ:
       s3 = boto3.client('s3')
       BUCKET = 'seu-bucket-spectra'
       # Usar S3 para ler arquivos
   else:
       SPECTRA_ROOT = Path("data/spectra/...")
   ```

4. **Adicionar credenciais em Streamlit Cloud**:
   - Dashboard da app → Settings → Secrets
   - Adicionar:
     ```toml
     [aws]
     access_key_id = "seu-key"
     secret_access_key = "seu-secret"
     bucket = "seu-bucket"
     ```

#### Google Cloud Storage

Similar ao S3, mas usando `google-cloud-storage`:

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('seu-bucket')
blob = bucket.blob('spectra/data.fits')
blob.download_to_filename('local_file.fits')
```

### Opção 3: Apenas Metadados (Sem Espectros)

Se preferir manter apenas o catálogo (`class.txt`) no repo:

1. Remova dados FITS do repositório
2. Usuários podem copiar arquivos FITS localmente
3. Mantenha apenas a documentação e código

## 🔐 Secrets e Variáveis de Ambiente

Para acessar dados restritos ou configurações sensíveis:

### Em Streamlit Cloud

1. Dashboard da app
2. Settings → Secrets
3. Adicione variáveis em formato TOML:
   ```toml
   database_password = "..."
   api_key = "..."
   s3_bucket = "..."
   ```

4. Acesse no código:
   ```python
   import streamlit as st
   
   password = st.secrets["database_password"]
   ```

## 📈 Monitoramento

### Streamlit Cloud Dashboard

- Acesse https://share.streamlit.io/admin
- Veja status da sua app
- Logs de execução
- Uso de recursos

### Métricas Úteis

- **Viewers**: Número de usuários acessando
- **Script runs**: Quantas vezes o script foi executado
- **Memory usage**: Consumo de memória
- **Runtime**: Tempo de carregamento

## 🚨 Troubleshooting

### "Module not found" na nuvem

**Causa**: Dependência não está em `requirements.txt`

**Solução**:
```bash
pip install pacote-faltante
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push origin main
```

### App trava ao carregar dados

**Causa**: Arquivo FITS muito grande

**Solução**:
- Use cache: `@st.cache_data`
- Comprima os dados
- Implemente lazy loading
- Use armazenamento em nuvem

### Dados não aparecem

**Verificar**:
1. Estrutura de diretórios está correta?
2. Arquivos FITS têm nome correto?
3. Path no código está correto (relativo vs absoluto)?

**Debug**:
```python
import os
from pathlib import Path

st.write(f"Working dir: {os.getcwd()}")
st.write(f"Files in data/: {os.listdir('data/')}")
```

## ⚡ Performance Tips

### Otimizar Carregamento

```python
@st.cache_data
def load_fits_data(path):
    """Cache dos dados para não recarregar a cada run"""
    return load_star_spectra(path)

# Usar função em cache
spectra = load_fits_data(sobject_id)
```

### Reduzir Tamanho de Gráficos

```python
fig.update_layout(
    height=600,  # Reduzir altura
    margin=dict(l=50, r=50, t=50, b=50)  # Margens menores
)
```

### Filtrar Dados

```python
# Em vez de carregar tudo
selected_ccd = st.selectbox("CCD", [1, 2, 3, 4])
spectra_filtered = [s for s in spectra if s["ccd"] == selected_ccd]
```

## 📚 Recursos

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/secrets-management)
- [GitHub LFS](https://git-lfs.com/)
- [AWS S3 Documentation](https://aws.amazon.com/s3/)
- [Google Cloud Storage](https://cloud.google.com/storage/docs)

---

**Versão**: 1.0.0  
**Última atualização**: Maio 2026

Dúvidas? Consulte a documentação oficial do Streamlit ou abra uma issue no GitHub!
