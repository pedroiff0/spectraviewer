"""
SPECTRAVIEWER — Academic Manifold Learning, Characterization & Anomaly Detection Platform
Sub-Amostra: 6.169 Estrelas Anãs M e Campo (Cruzamento GCNS x GALAH DR4)
Padrão de Publicação Científica e Interface Fiel ao Research Hub
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import astropy.io.fits as fits
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.neighbors import LocalOutlierFactor
import streamlit as st
import umap

# ==============================================================================
# CONFIGURAÇÃO GERAL DA PÁGINA
# ==============================================================================
st.set_page_config(
	page_title="SpectraViewer | GALAH DR4 x GCNS",
	page_icon="🌌",
	layout="wide",
	initial_sidebar_state="expanded"
)

# ==============================================================================
# DICIONÁRIO DE INTERNACIONALIZAÇÃO (i18n)
# ==============================================================================
I18N = {
	"pt": {
		"title": "🌌 SpectraViewer — Análise Espectral, Variedades e Anomalias",
		"subtitle": "Plataforma de caracterização astrofísica, manifold learning (14.800 px) e detecção não-supervisionada de anomalias (GALAH DR4 x GCNS).",
		"badge_sample": "🎯 6.169 Estrelas (GCNS x GALAH DR4)",
		"badge_coverage": "🔬 4713–7885 Å (4 Canais CCD)",
		"badge_dim": "⚡ 14.800 Pixels de Fluxo",
		"badge_methods": "📊 UMAP Direto (Cosseno), t-SNE, LOF & GLOSH",
		"tab_astro": "📊 Diagnóstico Astrofísico (Fase I)",
		"tab_spectra": "🌌 Visualizador Espectral",
		"tab_latent": "🗺️ Espaço Latente & Projeções",
		"tab_anomalies": "🔍 Detecção de Anomalias",
		"tab_theory": "📚 Metodologia e Fundamentação",
		"theme_label": "Tema:",
		"lang_label": "Idioma:",
		"filters_title": "⚙️ Filtros da Amostra",
		"teff_range": "Faixa de Teff (K):",
		"feh_range": "Faixa de [Fe/H] (dex):",
		"snr3_min": "S/N Mínimo CCD 3 (Vermelho):",
		"total_stars": "Total de Estrelas",
		"pixels_per_star": "Pixels / Espectro",
		"wavelength_range": "Intervalo λ",
	},
	"en": {
		"title": "🌌 SpectraViewer — Spectral Analysis, Manifolds & Anomalies",
		"subtitle": "Astrophysical characterization, 14,800-pixel manifold learning, and unsupervised anomaly detection platform (GALAH DR4 x GCNS).",
		"badge_sample": "🎯 6,169 Stars (GCNS x GALAH DR4)",
		"badge_coverage": "🔬 4713–7885 Å (4 CCD Bands)",
		"badge_dim": "⚡ 14,800 Flux Pixels",
		"badge_methods": "📊 Direct UMAP (Cosine), t-SNE, LOF & GLOSH",
		"tab_astro": "📊 Astrophysical Characterization (Phase I)",
		"tab_spectra": "🌌 Spectra Viewer",
		"tab_latent": "🗺️ Latent Space & Projections",
		"tab_anomalies": "🔍 Anomaly Detection",
		"tab_theory": "📚 Theory & Methodology",
		"theme_label": "Theme:",
		"lang_label": "Language:",
		"filters_title": "⚙️ Sample Filters",
		"teff_range": "Teff Range (K):",
		"feh_range": "[Fe/H] Range (dex):",
		"snr3_min": "Minimum SNR CCD 3 (Red):",
		"total_stars": "Total Stars",
		"pixels_per_star": "Pixels / Spectrum",
		"wavelength_range": "Wavelength Range",
	}
}

# ==============================================================================
# TOPBAR SUPERIOR: CONTROLE DE IDIOMA E TEMA
# ==============================================================================
top_col1, top_col2, top_col3 = st.columns([5.5, 1.2, 1.3])

with top_col2:
	lang_choice = st.selectbox(
		"🌐 Idioma",
		["Português (BR)", "English"],
		index=0,
		label_visibility="collapsed"
	)
	lang = "pt" if "Português" in lang_choice else "en"
	txt = I18N[lang]

with top_col3:
	theme_choice = st.selectbox(
		"🎨 Tema",
		["Escuro", "Claro", "Sistema"],
		index=0,
		label_visibility="collapsed"
	)

# ==============================================================================
# CONFIGURAÇÃO DE CORES DO TEMA
# ==============================================================================
if theme_choice == "Claro":
	BG_COLOR = "#f8fafc"
	SURFACE_COLOR = "#ffffff"
	CARD_BG = "#f1f5f9"
	TEXT_COLOR = "#0f172a"
	MUTED_COLOR = "#475569"
	BORDER_COLOR = "#cbd5e1"
	PRIMARY_COLOR = "#6d28d9"
	PRIMARY_LIGHT = "#7c3aed"
	PLOTLY_TEMPLATE = "plotly_white"
	PLOT_BG = "#ffffff"
	GRID_COLOR = "#e2e8f0"
else:
	# Escuro ou Sistema
	BG_COLOR = "#0b0e14"
	SURFACE_COLOR = "#131722"
	CARD_BG = "#1a202c"
	TEXT_COLOR = "#f8fafc"
	MUTED_COLOR = "#94a3b8"
	BORDER_COLOR = "#2d3748"
	PRIMARY_COLOR = "#8b5cf6"
	PRIMARY_LIGHT = "#a78bfa"
	PLOTLY_TEMPLATE = "plotly_dark"
	PLOT_BG = "#0f121a"
	GRID_COLOR = "#1f2937"

# CSS Injetado para Tema, Tipografia e Contraste Nítido
CSS_INJECTION = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {{
	font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
	background-color: {BG_COLOR} !important;
	color: {TEXT_COLOR} !important;
}}

/* Forçar textos a respeitarem a cor do tema */
p, span, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p, [data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] label, .stSelectbox label, .stSlider label,
.stRadio label, .stCheckbox label {{
	color: {TEXT_COLOR} !important;
}}

/* Banner Hero */
.hero-banner {{
	background: {SURFACE_COLOR};
	border: 1px solid {BORDER_COLOR};
	border-radius: 10px;
	padding: 1.25rem 1.6rem;
	margin-bottom: 1.2rem;
}}

.hero-title {{
	font-size: 1.65rem;
	font-weight: 800;
	color: {TEXT_COLOR} !important;
	margin: 0;
}}

.hero-subtitle {{
	color: {MUTED_COLOR} !important;
	font-size: 0.92rem;
	margin-top: 0.3rem;
	line-height: 1.45;
}}

.badge-pill {{
	display: inline-flex;
	align-items: center;
	padding: 0.2rem 0.6rem;
	border-radius: 9999px;
	font-size: 0.76rem;
	font-weight: 600;
	margin-right: 0.4rem;
	margin-top: 0.4rem;
	background: {CARD_BG};
	color: {PRIMARY_LIGHT} !important;
	border: 1px solid {BORDER_COLOR};
}}

/* KPI Cards */
.kpi-container {{
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
	gap: 0.6rem;
	margin-bottom: 0.9rem;
}}

.kpi-card {{
	background: {CARD_BG};
	border: 1px solid {BORDER_COLOR};
	border-radius: 8px;
	padding: 0.6rem 0.8rem;
	position: relative;
}}

.kpi-card::before {{
	content: '';
	position: absolute;
	top: 0; left: 0; right: 0;
	height: 3px;
	background: {PRIMARY_LIGHT};
}}

.kpi-label {{
	font-size: 0.72rem;
	font-weight: 600;
	color: {MUTED_COLOR} !important;
	text-transform: uppercase;
	letter-spacing: 0.04em;
}}

.kpi-value {{
	font-size: 1.15rem;
	font-weight: 700;
	color: {TEXT_COLOR} !important;
	margin-top: 0.15rem;
	font-family: 'JetBrains Mono', monospace;
}}

/* Callout Box */
.academic-callout {{
	background: {CARD_BG};
	border: 1px solid {BORDER_COLOR};
	border-left: 4px solid {PRIMARY_LIGHT};
	border-radius: 8px;
	padding: 0.8rem 1.1rem;
	margin: 0.75rem 0;
	font-size: 0.88rem;
	line-height: 1.5;
	color: {TEXT_COLOR} !important;
}}

/* Tabs Customizadas */
.stTabs [data-baseweb="tab-list"] {{
	gap: 6px;
	background-color: {SURFACE_COLOR};
	padding: 5px;
	border-radius: 8px;
	border: 1px solid {BORDER_COLOR};
}}

.stTabs [data-baseweb="tab"] {{
	height: 38px;
	border-radius: 6px;
	color: {MUTED_COLOR} !important;
	font-weight: 600;
	font-size: 0.88rem;
	padding: 0 12px;
}}

.stTabs [aria-selected="true"] {{
	background-color: {CARD_BG} !important;
	color: {TEXT_COLOR} !important;
	border-bottom: 2px solid {PRIMARY_LIGHT} !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
	background-color: {SURFACE_COLOR} !important;
	border-right: 1px solid {BORDER_COLOR} !important;
}}
</style>
"""
st.markdown(CSS_INJECTION, unsafe_allow_html=True)

# Paletas do Pedro (paletas.ipynb)
PEDRO_PALETTE_DISCRETE = ["#023e65", "#107ea7", "#75b0ad", "#f2deb0", "#f1a09b", "#e04c6d", "#8c0303"]

# ==============================================================================
# DIRETÓRIOS E CONSTANTES
# ==============================================================================
PROJECT_DIR = Path("/home/pedro/Repositorios/pesquisa/anomaly_detection")
DATA_DIR = PROJECT_DIR / "data"
CSV_RESULTS_PATH = DATA_DIR / "m_dwarfs_tsne_umap_anomaly_results.csv"
NPZ_MATRIX_PATH = DATA_DIR / "TCC" / "m_dwarfs_single_spectra_matrix.npz"
SINGLE_SPECTRA_DIR = Path("/media/pedro/galah/spectra_single")
VALIDATION_FIGS_DIR = PROJECT_DIR / "figuras" / "TCC" / "validacao"

KEY_ASTRO_LINES = [
	{"name": "Hβ", "wave": 4861.33, "ccd": 1, "color": "#38bdf8", "desc": "Balmer Hβ (Cromosfera/Atividade)"},
	{"name": "Mg I b", "wave": 5183.60, "ccd": 1, "color": "#2dd4bf", "desc": "Tripleto de Magnésio (Gravidade)"},
	{"name": "Na I D2", "wave": 5889.95, "ccd": 2, "color": "#facc15", "desc": "Dubleto de Sódio D2"},
	{"name": "Na I D1", "wave": 5895.92, "ccd": 2, "color": "#facc15", "desc": "Dubleto de Sódio D1"},
	{"name": "Hα", "wave": 6562.80, "ccd": 3, "color": "#f43f5e", "desc": "Balmer Hα (Traçador de Atividade/Flares)"},
	{"name": "TiO λ6599", "wave": 6599.00, "ccd": 3, "color": "#e879f9", "desc": "Cabeça de Banda TiO"},
	{"name": "Li I", "wave": 6707.80, "ccd": 3, "color": "#a855f7", "desc": "Lítio Ressonante (Limite de Queima/Idade)"},
	{"name": "K I λ7665", "wave": 7664.91, "ccd": 4, "color": "#fb923c", "desc": "Dubleto de Potássio K I"},
	{"name": "K I λ7699", "wave": 7698.97, "ccd": 4, "color": "#fb923c", "desc": "Dubleto de Potássio K I"},
	{"name": "TiO λ7670", "wave": 7670.00, "ccd": 4, "color": "#e879f9", "desc": "Cabeça de Banda TiO"},
]

CCD_BANDS = {
	1: {"name": "CCD 1 (Azul)", "min": 4713.0, "max": 4900.0, "color": "#38bdf8"},
	2: {"name": "CCD 2 (Verde)", "min": 5649.0, "max": 5872.0, "color": "#4ade80"},
	3: {"name": "CCD 3 (Vermelho)", "min": 6479.0, "max": 6735.0, "color": "#f87171"},
	4: {"name": "CCD 4 (IR)", "min": 7680.0, "max": 7885.0, "color": "#c084fc"},
}

# ==============================================================================
# CARREGAMENTO EM CACHE
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_catalog() -> pd.DataFrame:
	if not CSV_RESULTS_PATH.exists():
		st.error(f"Catálogo não encontrado: {CSV_RESULTS_PATH}")
		return pd.DataFrame()
	df = pd.read_csv(CSV_RESULTS_PATH)
	df["sobject_id_str"] = df["sobject_id"].astype(np.int64).astype(str)
	return df

@st.cache_data(show_spinner=False)
def load_matrix() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, int]]:
	if not NPZ_MATRIX_PATH.exists():
		return np.array([]), np.array([]), np.array([]), np.array([]), {}
	npz = np.load(NPZ_MATRIX_PATH)
	sobject_ids = npz["sobject_ids"]
	wave = npz["wave"]
	X_flux = npz["X_flux"]
	X_res = npz["X_res"]
	id_to_idx = {str(sid): i for i, sid in enumerate(sobject_ids)}
	return sobject_ids, wave, X_flux, X_res, id_to_idx

df_catalog = load_catalog()
sobject_ids_npz, wave_grid, X_flux_mat, X_res_mat, id_to_idx = load_matrix()

# ==============================================================================
# BARRA LATERAL: FILTROS ASTROFÍSICOS DA AMOSTRA (FAIXA TEFF 3000 A 8000 K)
# ==============================================================================
with st.sidebar:
	st.markdown(f"### {txt['filters_title']}")
	f_teff = st.slider(txt["teff_range"], min_value=3000, max_value=8000, value=(3000, 8000), step=100)
	f_feh = st.slider(txt["feh_range"], min_value=-1.6, max_value=0.6, value=(-1.6, 0.6), step=0.1)
	f_snr3 = st.slider(txt["snr3_min"], min_value=0, max_value=150, value=0, step=5)

	mask_filter = (
		(df_catalog["teff"] >= f_teff[0]) & (df_catalog["teff"] <= f_teff[1]) &
		(df_catalog["fe_h"] >= f_feh[0]) & (df_catalog["fe_h"] <= f_feh[1]) &
		(df_catalog["snr_c3"].fillna(0) >= f_snr3)
	)
	df_filtered = df_catalog[mask_filter].copy()

	st.markdown(
		f"""
		<div style="font-size: 0.8rem; color: {MUTED_COLOR}; margin-top: 0.5rem;">
			Estrelas filtradas: <b>{len(df_filtered):,}</b> de <b>{len(df_catalog):,}</b> ({len(df_filtered)/max(1, len(df_catalog))*100:.1f}%)
		</div>
		""",
		unsafe_allow_html=True
	)

# ==============================================================================
# BANNER HERO
# ==============================================================================
st.markdown(
	f"""
	<div class="hero-banner">
		<h1 class="hero-title">{txt['title']}</h1>
		<div class="hero-subtitle">{txt['subtitle']}</div>
		<div style="margin-top: 0.5rem;">
			<span class="badge-pill">{txt['badge_sample']}</span>
			<span class="badge-pill">{txt['badge_coverage']}</span>
			<span class="badge-pill">{txt['badge_dim']}</span>
			<span class="badge-pill">{txt['badge_methods']}</span>
		</div>
	</div>
	""",
	unsafe_allow_html=True
)

# ==============================================================================
# SUB-ABAS PRINCIPAIS
# ==============================================================================
tab_astro, tab_spectra, tab_latent, tab_anomalies, tab_theory = st.tabs([
	txt["tab_astro"],
	txt["tab_spectra"],
	txt["tab_latent"],
	txt["tab_anomalies"],
	txt["tab_theory"],
])

# ==============================================================================
# ABA 1: DIAGNÓSTICO ASTROFÍSICO (FASE I DO TCC)
# ==============================================================================
with tab_astro:
	st.markdown("### 📊 Caracterização Astrofísica & Catálogos (Fase I — GCNS x GALAH DR4)")
	
	col_view_opt, col_spacer = st.columns([2.5, 4.5])
	with col_view_opt:
		plot_render_mode = st.radio(
			"Formato de Visualização dos Gráficos:",
			["Interativo (Plotly HD)", "Publicação Oficial (Matplotlib 300 DPI do Notebook 08)"],
			horizontal=True
		)

	# KPIs Gerais
	st.markdown(
		f"""
		<div class="kpi-container">
			<div class="kpi-card">
				<div class="kpi-label">{txt['total_stars']}</div>
				<div class="kpi-value">{len(df_catalog):,}</div>
			</div>
			<div class="kpi-card">
				<div class="kpi-label">Amostra Filtrada</div>
				<div class="kpi-value" style="color: {PRIMARY_LIGHT};">{len(df_filtered):,}</div>
			</div>
			<div class="kpi-card">
				<div class="kpi-label">Matriz Espectral (.npz)</div>
				<div class="kpi-value">6.169 x 14.800 px</div>
			</div>
			<div class="kpi-card">
				<div class="kpi-label">Teff Médio</div>
				<div class="kpi-value">{df_filtered['teff'].mean():.0f} K</div>
			</div>
			<div class="kpi-card">
				<div class="kpi-label">[Fe/H] Médio</div>
				<div class="kpi-value">{df_filtered['fe_h'].mean():.2f} dex</div>
			</div>
			<div class="kpi-card">
				<div class="kpi-label">S/N Médio (CCD 3)</div>
				<div class="kpi-value">{df_filtered['snr_c3'].mean():.1f}</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True
	)

	if plot_render_mode.startswith("Interativo"):
		col_d1, col_d2 = st.columns(2)

		# 1. Diagrama de Kiel (Teff vs logg)
		with col_d1:
			fig_kiel = px.scatter(
				df_filtered,
				x="teff", y="logg",
				color="fe_h",
				color_continuous_scale="Viridis",
				hover_data={"sobject_id_str": True, "teff": ":.0f", "logg": ":.2f", "fe_h": ":.2f", "snr_c3": ":.1f"},
				labels={"teff": "Temperatura Efetiva Teff (K)", "logg": "Gravidade Superficial log g (cgs)", "fe_h": "[Fe/H] (dex)"},
				title="1. Diagrama de Kiel (Teff vs log g) — Sequência de Anãs M e Gigantes"
			)
			fig_kiel.update_xaxes(range=[8000, 2800], gridcolor=GRID_COLOR, zeroline=False)
			fig_kiel.update_yaxes(range=[5.6, 0.5], gridcolor=GRID_COLOR, zeroline=False)
			fig_kiel.update_traces(marker=dict(size=4.5, opacity=0.75))
			fig_kiel.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=520, font=dict(color=TEXT_COLOR))
			st.plotly_chart(fig_kiel, use_container_width=True)

		# 2. Diagrama de Tinsley-Wallerstein ([Fe/H] vs [alpha/Fe])
		with col_d2:
			y_elem = "alpha_fe" if "alpha_fe" in df_filtered.columns else "mg_fe"
			y_name = "[α/Fe]" if y_elem == "alpha_fe" else "[Mg/Fe]"
			fig_tinsley = px.scatter(
				df_filtered,
				x="fe_h", y=y_elem,
				color="teff",
				color_continuous_scale="Plasma",
				hover_data={"sobject_id_str": True, "teff": ":.0f", "fe_h": ":.2f", y_elem: ":.2f"},
				labels={"fe_h": "Metalicidade [Fe/H] (dex)", y_elem: f"{y_name} (dex)", "teff": "Teff (K)"},
				title=f"2. Diagrama de Tinsley-Wallerstein ([Fe/H] vs {y_name}) — Disco Fino / Espesso"
			)
			fig_tinsley.add_shape(type="line", x0=-1.2, y0=0.22, x1=0.3, y1=0.04, line=dict(color="#f59e0b", dash="dash", width=2.0))
			fig_tinsley.update_xaxes(range=[-1.6, 0.6], gridcolor=GRID_COLOR, zeroline=False)
			fig_tinsley.update_yaxes(range=[-0.25, 0.65], gridcolor=GRID_COLOR, zeroline=False)
			fig_tinsley.update_traces(marker=dict(size=4.5, opacity=0.75))
			fig_tinsley.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=520, font=dict(color=TEXT_COLOR))
			st.plotly_chart(fig_tinsley, use_container_width=True)

		col_d3, col_d4 = st.columns(2)

		# 3. Diagrama de Toomre (Cinemática)
		with col_d3:
			df_toomre = df_filtered.dropna(subset=["Vvel50", "v_perp"]).copy() if "v_perp" in df_filtered.columns else pd.DataFrame()
			if len(df_toomre) > 0:
				fig_toomre = px.scatter(
					df_toomre,
					x="Vvel50", y="v_perp",
					color="fe_h",
					color_continuous_scale="Turbo",
					hover_data={"sobject_id_str": True, "Vvel50": ":.1f", "v_perp": ":.1f", "v_tot": ":.1f", "fe_h": ":.2f"},
					labels={"Vvel50": "V (km/s) — Rotação Galáctica Relativa", "v_perp": "√(U² + W²) (km/s) — Velocidade Perpendicular", "fe_h": "[Fe/H]"},
					title="3. Diagrama de Toomre (Cinemática) — Disco Fino, Espesso e Halo"
				)
				theta = np.linspace(0, np.pi, 100)
				for v_circ in [50, 100, 180]:
					fig_toomre.add_trace(go.Scatter(
						x=v_circ * np.cos(theta),
						y=v_circ * np.sin(theta),
						mode="lines",
						line=dict(color="#94a3b8", dash="dot", width=1.5),
						name=f"V_tot = {v_circ} km/s",
						showlegend=False
					))
				fig_toomre.update_xaxes(range=[-160, 160], gridcolor=GRID_COLOR, zeroline=False)
				fig_toomre.update_yaxes(range=[0, 180], gridcolor=GRID_COLOR, zeroline=False)
				fig_toomre.update_traces(marker=dict(size=4.5, opacity=0.75))
				fig_toomre.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=520, font=dict(color=TEXT_COLOR))
				st.plotly_chart(fig_toomre, use_container_width=True)
			else:
				st.info("Dados cinemáticos (U, V, W) não disponíveis para o filtro atual.")

		# 4. Distribuição do S/N nos 4 CCDs
		with col_d4:
			fig_snr = go.Figure()
			fig_snr.add_trace(go.Scatter(x=df_filtered["teff"], y=df_filtered["snr_c1"], mode="markers", name="CCD 1 (Azul)", marker=dict(color="#38bdf8", size=4, opacity=0.5)))
			fig_snr.add_trace(go.Scatter(x=df_filtered["teff"], y=df_filtered["snr_c2"], mode="markers", name="CCD 2 (Verde)", marker=dict(color="#4ade80", size=4, opacity=0.5)))
			fig_snr.add_trace(go.Scatter(x=df_filtered["teff"], y=df_filtered["snr_c3"], mode="markers", name="CCD 3 (Vermelho)", marker=dict(color="#f87171", size=4, opacity=0.5)))
			fig_snr.add_trace(go.Scatter(x=df_filtered["teff"], y=df_filtered["snr_c4"], mode="markers", name="CCD 4 (IR)", marker=dict(color="#c084fc", size=4, opacity=0.5)))
			fig_snr.update_layout(
				title="4. S/N por CCD vs Teff (Curva de Planck de 3000 a 8000 K)",
				xaxis_title="Temperatura Efetiva Teff (K)",
				yaxis_title="S/N por Pixel",
				template=PLOTLY_TEMPLATE,
				plot_bgcolor=PLOT_BG,
				paper_bgcolor=PLOT_BG,
				height=520,
				font=dict(color=TEXT_COLOR),
				legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
			)
			fig_snr.update_xaxes(range=[8000, 2800], gridcolor=GRID_COLOR, zeroline=False)
			fig_snr.update_yaxes(range=[0, 200], gridcolor=GRID_COLOR, zeroline=False)
			st.plotly_chart(fig_snr, use_container_width=True)

	else:
		# Exibição direta das figuras de alta resolução 300 DPI geradas pelo Notebook 08
		st.markdown("#### 📷 Figuras Publicadas do Notebook de Validação (`08_validacao_completa_pesquisa_e_figuras_tcc.ipynb`):")
		c_p1, c_p2 = st.columns(2)
		with c_p1:
			st.image(str(VALIDATION_FIGS_DIR / "01_kiel_diagram_full_teff.png"), caption="1. Diagrama de Kiel (Teff [3000, 8000] K vs log g)", use_container_width=True)
			st.image(str(VALIDATION_FIGS_DIR / "03_toomre_kinematic_diagram.png"), caption="3. Diagrama de Toomre (Cinemática Galáctica)", use_container_width=True)
		with c_p2:
			st.image(str(VALIDATION_FIGS_DIR / "02_tinsley_wallerstein_diagram.png"), caption="2. Diagrama de Tinsley-Wallerstein ([Fe/H] vs [alpha/Fe])", use_container_width=True)
			st.image(str(VALIDATION_FIGS_DIR / "04_snr_distribution_4ccds_teff.png"), caption="4. Relação Sinal-Ruído nos 4 CCDs do GALAH DR4", use_container_width=True)

# ==============================================================================
# ABA 2: VISUALIZADOR ESPECTRAL (SPECTRA VIEWER)
# ==============================================================================
with tab_spectra:
	col_s1, col_s2, col_s3 = st.columns([2.2, 1.8, 2.0])

	with col_s1:
		src_type = st.radio(
			"Origem do Espectro:",
			["Amostra GCNS+GALAH DR4 (Matriz .npz)", "Buscar por sobject_id", "Carregar FITS"],
			horizontal=True
		)

	active_sid = None
	spec_obj = None

	if src_type.startswith("Amostra"):
		with col_s2:
			s_idx = st.number_input("Índice na Amostra (0 a 6168):", min_value=0, max_value=len(df_catalog)-1, value=0, step=1)
			active_sid = str(df_catalog.iloc[s_idx]["sobject_id"])
		with col_s3:
			sel_quick = st.selectbox("Ou selecione da lista:", options=df_catalog["sobject_id_str"].tolist(), index=s_idx)
			if sel_quick != active_sid:
				active_sid = sel_quick

	elif src_type.startswith("Buscar"):
		with col_s2:
			typed_sid = st.text_input("Digite o sobject_id:", value=str(df_catalog.iloc[0]["sobject_id"]) if len(df_catalog)>0 else "")
			if typed_sid.strip():
				active_sid = typed_sid.strip()

	else:
		with col_s2:
			fit_file = st.file_uploader("FITS _single_fit_spectrum.fits:", type=["fits"])
			if fit_file is not None:
				try:
					with fits.open(fit_file) as h:
						h0 = h[0].header
						m_info = {
							"sobject_id": h0.get("SOBJECT_ID", "Upload"),
							"teff": h0.get("TEFF", np.nan),
							"logg": h0.get("LOGG", np.nan),
							"fe_h": h0.get("FE_H", np.nan),
							"snr_px_ccd1": h0.get("SNR_PX_CCD1", np.nan),
							"snr_px_ccd2": h0.get("SNR_PX_CCD2", np.nan),
							"snr_px_ccd3": h0.get("SNR_PX_CCD3", np.nan),
							"snr_px_ccd4": h0.get("SNR_PX_CCD4", np.nan),
						}
						sob = h[1].data.astype(np.float64)
						smod = h[3].data.astype(np.float64) if len(h)>3 else None
						res = h[4].data.astype(np.float64) if len(h)>4 else None
						crval = h[1].header.get("CRVAL1", 4713.0)
						cdelt = h[1].header.get("CDELT1", (7885.0 - 4713.0)/len(sob))
						w_arr = crval + np.arange(len(sob))*cdelt
						spec_obj = {"meta": m_info, "wave": w_arr, "sob": sob, "smod": smod, "res": res}
						active_sid = str(m_info["sobject_id"])
				except Exception as e:
					st.error(f"Erro ao ler FITS: {e}")

	if spec_obj is None and active_sid:
		row_cat = df_catalog[df_catalog["sobject_id_str"] == active_sid]
		meta_info = {}
		if len(row_cat) > 0:
			r = row_cat.iloc[0]
			meta_info = {
				"sobject_id": active_sid,
				"teff": r.get("teff", np.nan),
				"logg": r.get("logg", np.nan),
				"fe_h": r.get("fe_h", np.nan),
				"alpha_fe": r.get("alpha_fe", np.nan),
				"snr_px_ccd1": r.get("snr_c1", np.nan),
				"snr_px_ccd2": r.get("snr_c2", np.nan),
				"snr_px_ccd3": r.get("snr_c3", np.nan),
				"snr_px_ccd4": r.get("snr_c4", np.nan),
				"rv_comp_1": r.get("rv_comp_1", np.nan),
				"lof_score": r.get("lof_score", np.nan),
				"glosh_score": r.get("glosh_outlier_score", np.nan),
			}

		if active_sid in id_to_idx:
			idx_mat = id_to_idx[active_sid]
			flux_arr = X_flux_mat[idx_mat]
			res_arr = X_res_mat[idx_mat] if len(X_res_mat) > 0 else None
			smod_arr = flux_arr - res_arr if res_arr is not None else None
			spec_obj = {"meta": meta_info, "wave": wave_grid, "sob": flux_arr, "smod": smod_arr, "res": res_arr}
		else:
			fits_disk = SINGLE_SPECTRA_DIR / f"{active_sid[:6]}" / f"{active_sid}_single_fit_spectrum.fits"
			if fits_disk.exists():
				with fits.open(fits_disk) as h:
					h0 = h[0].header
					sob = h[1].data.astype(np.float64)
					smod = h[3].data.astype(np.float64) if len(h)>3 else None
					res = h[4].data.astype(np.float64) if len(h)>4 else None
					crval = h[1].header.get("CRVAL1", 4713.0)
					cdelt = h[1].header.get("CDELT1", (7885.0 - 4713.0)/len(sob))
					w_arr = crval + np.arange(len(sob))*cdelt
					spec_obj = {"meta": meta_info, "wave": w_arr, "sob": sob, "smod": smod, "res": res}

	if spec_obj is not None:
		meta = spec_obj["meta"]

		# KPIs Astrofísicos
		st.markdown(
			f"""
			<div class="kpi-container">
				<div class="kpi-card">
					<div class="kpi-label">sobject_id</div>
					<div class="kpi-value" style="font-size: 1.0rem; color: {PRIMARY_LIGHT};">{active_sid}</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-label">Teff</div>
					<div class="kpi-value">{meta.get('teff', np.nan):.0f} K</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-label">log g</div>
					<div class="kpi-value">{meta.get('logg', np.nan):.2f}</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-label">[Fe/H]</div>
					<div class="kpi-value">{meta.get('fe_h', np.nan):.2f}</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-label">LOF Score</div>
					<div class="kpi-value" style="color: {'#ef4444' if float(meta.get('lof_score', 1.0) or 1.0)>1.3 else '#10b981'};">{meta.get('lof_score', np.nan):.3f}</div>
				</div>
				<div class="kpi-card">
					<div class="kpi-label">GLOSH</div>
					<div class="kpi-value" style="color: {'#f59e0b' if float(meta.get('glosh_score', 0.0) or 0.0)>0.8 else '#38bdf8'};">{meta.get('glosh_score', np.nan):.3f}</div>
				</div>
			</div>
			""",
			unsafe_allow_html=True
		)

		# Diagnóstico S/N Simplificado
		snr1 = meta.get('snr_px_ccd1', 0.0)
		snr2 = meta.get('snr_px_ccd2', 0.0)
		snr3 = meta.get('snr_px_ccd3', 0.0)
		snr4 = meta.get('snr_px_ccd4', 0.0)

		st.markdown(
			f"""
			<div class="academic-callout">
				<b>Sinal-Ruído por Canal Óptico:</b> 
				CCD 1 (Azul: 4713–4900 Å): <b>{snr1:.1f}</b> | 
				CCD 2 (Verde: 5649–5872 Å): <b>{snr2:.1f}</b> | 
				CCD 3 (Vermelho: 6479–6735 Å): <b>{snr3:.1f}</b> | 
				CCD 4 (IR: 7680–7885 Å): <b>{snr4:.1f}</b>
				<br><small style="color: {MUTED_COLOR};">
					<i>Interpretação:</i> Em anãs frias (Teff ≤ 4000 K), a emissão máxima ocorre no infravermelho (CCD 3 e CCD 4), tornando-os os balizadores estatísticos de qualidade.
				</small>
			</div>
			""",
			unsafe_allow_html=True
		)

		col_opt1, col_opt2, col_opt3, col_opt4 = st.columns([1.5, 1.2, 1.2, 1.5])
		with col_opt1:
			p_mode = st.radio("Layout:", ["Completo Contínuo (4713–7885 Å)", "4 CCDs Separados"], horizontal=True)
		with col_opt2:
			tog_mod = st.checkbox(r"Modelo Sintético ($s_{\mathrm{mod}}$)", value=True)
		with col_opt3:
			tog_res = st.checkbox(r"Resíduo ($\Delta s$)", value=True)
		with col_opt4:
			tog_lines = st.checkbox("Linhas Atômicas Chave", value=True)

		w_f = spec_obj["wave"]
		s_f = spec_obj["sob"]
		m_f = spec_obj["smod"]
		r_f = spec_obj["res"]

		if p_mode.startswith("Completo"):
			has_res = tog_res and (r_f is not None)
			if has_res:
				fig_sp = make_subplots(
					rows=2, cols=1,
					shared_xaxes=True,
					vertical_spacing=0.06,
					row_heights=[0.72, 0.28],
					subplot_titles=[
						f"Espectro Normalizado vs Modelo Sintético — {active_sid}",
						"Resíduo Espectral (Δs = Fluxo Obs - Modelo) — Picos positivos indicam emissão"
					]
				)
			else:
				fig_sp = make_subplots(rows=1, cols=1, subplot_titles=[f"Espectro Normalizado — {active_sid}"])

			for ccd_k, ccd_v in CCD_BANDS.items():
				msk = (w_f >= ccd_v["min"]) & (w_f <= ccd_v["max"])
				if not np.any(msk):
					continue
				fig_sp.add_trace(
					go.Scatter(x=w_f[msk], y=s_f[msk], mode="lines", name=ccd_v["name"], line=dict(color=ccd_v["color"], width=1.3)),
					row=1, col=1
				)
				if tog_mod and m_f is not None:
					fig_sp.add_trace(
						go.Scatter(x=w_f[msk], y=m_f[msk], mode="lines", name="Modelo", line=dict(color="#f97316", width=1.1, dash="dot"), showlegend=(ccd_k==1)),
						row=1, col=1
					)
				if has_res:
					fig_sp.add_trace(
						go.Scatter(x=w_f[msk], y=r_f[msk], mode="lines", line=dict(color=ccd_v["color"], width=1.0), showlegend=False),
						row=2, col=1
					)

			if has_res:
				fig_sp.add_hline(y=0.0, line_dash="dash", line_color="#64748b", row=2, col=1)

			if tog_lines:
				for line in KEY_ASTRO_LINES:
					fig_sp.add_vline(x=line["wave"], line_dash="dot", line_color=line["color"], line_width=1.1, annotation_text=line["name"], row=1, col=1)

			fig_sp.update_layout(
				template=PLOTLY_TEMPLATE,
				plot_bgcolor=PLOT_BG,
				paper_bgcolor=PLOT_BG,
				height=580,
				font=dict(color=TEXT_COLOR),
				margin=dict(l=40, r=30, t=50, b=40),
			)
			fig_sp.update_xaxes(title_text="Comprimento de Onda no Vácuo (Å)", row=2 if has_res else 1, col=1, gridcolor=GRID_COLOR, zeroline=False)
			fig_sp.update_yaxes(title_text="Fluxo", row=1, col=1, gridcolor=GRID_COLOR, range=[0.0, 1.8], zeroline=False)
			if has_res:
				fig_sp.update_yaxes(title_text="Δs", row=2, col=1, gridcolor=GRID_COLOR, range=[-0.5, 0.8], zeroline=False)
			st.plotly_chart(fig_sp, use_container_width=True)

		else:
			# 4 CCDs Subplots
			fig_cc = make_subplots(
				rows=2, cols=2,
				subplot_titles=["CCD 1: Azul (Hβ, Mg I)", "CCD 2: Verde (Na I D)", "CCD 3: Vermelho (Hα, Li I, TiO)", "CCD 4: IR (K I, TiO)"],
				vertical_spacing=0.12, horizontal_spacing=0.06
			)
			cds = {1:(1,1), 2:(1,2), 3:(2,1), 4:(2,2)}
			for ccd_k, (r_pos, c_pos) in cds.items():
				info = CCD_BANDS[ccd_k]
				msk = (w_f >= info["min"]) & (w_f <= info["max"])
				if not np.any(msk):
					continue
				fig_cc.add_trace(go.Scatter(x=w_f[msk], y=s_f[msk], mode="lines", name=info["name"], line=dict(color=info["color"], width=1.3), showlegend=(r_pos==1 and c_pos==1)), row=r_pos, col=c_pos)
				if tog_mod and m_f is not None:
					fig_cc.add_trace(go.Scatter(x=w_f[msk], y=m_f[msk], mode="lines", line=dict(color="#f97316", width=1.1, dash="dot"), showlegend=False), row=r_pos, col=c_pos)
				if tog_lines:
					for line in KEY_ASTRO_LINES:
						if line["ccd"] == ccd_k and info["min"] <= line["wave"] <= info["max"]:
							fig_cc.add_vline(x=line["wave"], line_dash="dot", line_color=line["color"], line_width=1.0, annotation_text=line["name"], row=r_pos, col=c_pos)

			fig_cc.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=600, font=dict(color=TEXT_COLOR))
			fig_cc.update_xaxes(gridcolor=GRID_COLOR, title_text="λ (Å)", zeroline=False)
			fig_cc.update_yaxes(gridcolor=GRID_COLOR, title_text="Fluxo", range=[0.0, 1.8], zeroline=False)
			st.plotly_chart(fig_cc, use_container_width=True)

# ==============================================================================
# ABA 3: ESPAÇO LATENTE & PROJEÇÕES
# ==============================================================================
with tab_latent:
	st.markdown("### 🗺️ Espaço Latente & Reduções de Dimensionalidade")

	col_vm, col_cb, col_pl = st.columns([2.0, 1.6, 1.4])
	with col_vm:
		view_opt = st.radio(
			"Modo de Exibição:",
			["Projeção Individual Detalhada", "Painel Comparativo Combinado (Grid 2x2)", "Ajuste Interativo de Hiperparâmetros (Sliders)"],
			horizontal=True
		)

	with col_cb:
		c_var = st.selectbox(
			"Coloração do Gráfico:",
			["Teff (K)", "log g", "[Fe/H] (dex)", "[alpha/Fe] (dex)", "S/N CCD 3 (Hα)", "LOF Score", "GLOSH Score", "Cluster HDBSCAN", "V_perp (Cinemática)"]
		)

	with col_pl:
		cmap_opt = st.selectbox("Colormap:", ["Viridis", "Plasma", "Turbo", "Magma", "Cividis", "Pedro Paleta (paletas.ipynb)"], index=0)

	c_map_plt = PEDRO_PALETTE_DISCRETE if cmap_opt.startswith("Pedro") else cmap_opt

	c_dict = {
		"Teff (K)": ("teff", "Teff (K)"),
		"log g": ("logg", "log g"),
		"[Fe/H] (dex)": ("fe_h", "[Fe/H]"),
		"[alpha/Fe] (dex)": ("alpha_fe", "[α/Fe]"),
		"S/N CCD 3 (Hα)": ("snr_c3", "S/N CCD3"),
		"LOF Score": ("lof_score", "LOF Score"),
		"GLOSH Score": ("glosh_outlier_score", "GLOSH Score"),
		"Cluster HDBSCAN": ("hdbscan_cluster", "Cluster"),
		"V_perp (Cinemática)": ("v_perp", "V_perp (km/s)"),
	}
	c_col, c_lbl = c_dict[c_var]

	# 1. Projeção Individual
	if view_opt.startswith("Projeção Individual"):
		col_p1, col_p2 = st.columns([2.5, 1.5])
		with col_p1:
			p_type = st.selectbox(
				"Método de Projeção:",
				[
					"UMAP Direto (14.800 px — Métrica Cosseno — Sem PCA)",
					"UMAP via PCA (50 PCs — Euclidiana)",
					"t-SNE (Perplexidade 30)",
					"t-SNE (Perplexidade 50)",
					"PCA 2D (PC1 vs PC2 — 36.9% da Variância)",
					"PCA 3D Interativo (PC1 vs PC2 vs PC3)"
				]
			)
		with col_p2:
			pt_sz = st.slider("Tamanho do Ponto:", min_value=2.0, max_value=10.0, value=4.5, step=0.5)

		if p_type.startswith("UMAP Direto"):
			xc, yc = "umap_direct_1", "umap_direct_2"
			xl, yl = "UMAP Direto 1 (14.800 px — Métrica Cosseno)", "UMAP Direto 2"
			is_3d = False
		elif p_type.startswith("UMAP via PCA"):
			xc, yc = "umap_1_nn15", "umap_2_nn15"
			xl, yl = "UMAP (PCA 50) 1", "UMAP (PCA 50) 2"
			is_3d = False
		elif "30" in p_type:
			xc, yc = "tsne_1_p30", "tsne_2_p30"
			xl, yl = "t-SNE 1 (p=30)", "t-SNE 2 (p=30)"
			is_3d = False
		elif "50" in p_type:
			xc, yc = "tsne_1_p50", "tsne_2_p50"
			xl, yl = "t-SNE 1 (p=50)", "t-SNE 2 (p=50)"
			is_3d = False
		elif p_type.startswith("PCA 2D"):
			xc, yc = "pca_1", "pca_2"
			xl, yl = "PC 1 (24.6% da Variância)", "PC 2 (12.3% da Variância)"
			is_3d = False
		else:
			is_3d = True

		if not is_3d:
			fig_ind = px.scatter(
				df_filtered,
				x=xc, y=yc,
				color=c_col,
				color_continuous_scale=c_map_plt if c_col != "hdbscan_cluster" else None,
				color_discrete_sequence=px.colors.qualitative.Alphabet if c_col == "hdbscan_cluster" else None,
				hover_data={"sobject_id_str": True, "teff": ":.0f", "logg": ":.2f", "fe_h": ":.2f", "lof_score": ":.3f", "glosh_outlier_score": ":.3f"},
				labels={c_col: c_lbl},
				title=f"{p_type} — {len(df_filtered):,} Estrelas"
			)
			fig_ind.update_traces(marker=dict(size=pt_sz, opacity=0.75))
			fig_ind.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=620, font=dict(color=TEXT_COLOR))
			fig_ind.update_xaxes(title_text=xl, gridcolor=GRID_COLOR, zeroline=False)
			fig_ind.update_yaxes(title_text=yl, gridcolor=GRID_COLOR, zeroline=False)
			st.plotly_chart(fig_ind, use_container_width=True)
		else:
			fig_3d = px.scatter_3d(
				df_filtered,
				x="pca_1", y="pca_2", z="pca_3",
				color=c_col,
				color_continuous_scale=c_map_plt if c_col != "hdbscan_cluster" else None,
				hover_data={"sobject_id_str": True, "teff": ":.0f", "logg": ":.2f", "fe_h": ":.2f", "lof_score": ":.3f"},
				title=f"PCA 3D (PC1 vs PC2 vs PC3) — {len(df_filtered):,} Estrelas"
			)
			fig_3d.update_traces(marker=dict(size=pt_sz*0.7, opacity=0.7))
			fig_3d.update_layout(template=PLOTLY_TEMPLATE, paper_bgcolor=PLOT_BG, height=650, font=dict(color=TEXT_COLOR))
			st.plotly_chart(fig_3d, use_container_width=True)

	# 2. Painel Combinado Grid 2x2
	elif view_opt.startswith("Painel Comparativo"):
		st.markdown("#### 🔬 Comparação Lado a Lado da Coerência Topológica das Variedades")
		fig_grid = make_subplots(
			rows=2, cols=2,
			subplot_titles=[
				"A. UMAP Direto (14.800 px — Métrica Cosseno)",
				"B. UMAP via PCA (50 Componentes)",
				"C. t-SNE (Perplexidade 30)",
				"D. PCA 2D (PC1 vs PC2 — Linear)"
			],
			horizontal_spacing=0.08, vertical_spacing=0.12
		)

		grid_meta = [
			("umap_direct_1", "umap_direct_2", 1, 1),
			("umap_1_nn15", "umap_2_nn15", 1, 2),
			("tsne_1_p30", "tsne_2_p30", 2, 1),
			("pca_1", "pca_2", 2, 2),
		]

		c_arr = df_filtered[c_col].values
		for (xc_g, yc_g, rp_g, cp_g) in grid_meta:
			fig_grid.add_trace(
				go.Scatter(
					x=df_filtered[xc_g], y=df_filtered[yc_g],
					mode="markers",
					marker=dict(
						size=3.5,
						color=c_arr,
						colorscale=cmap_opt if cmap_opt != "Pedro Paleta (paletas.ipynb)" else "Viridis",
						showscale=(rp_g==1 and cp_g==2),
						colorbar=dict(title=c_lbl, x=1.02) if (rp_g==1 and cp_g==2) else None,
						opacity=0.75
					),
					text=[f"ID: {sid}<br>Teff: {t:.0f} K<br>[Fe/H]: {fe:.2f}" for sid, t, fe in zip(df_filtered["sobject_id_str"], df_filtered["teff"], df_filtered["fe_h"])],
					hoverinfo="text",
					showlegend=False
				),
				row=rp_g, col=cp_g
			)

		fig_grid.update_layout(
			template=PLOTLY_TEMPLATE,
			plot_bgcolor=PLOT_BG,
			paper_bgcolor=PLOT_BG,
			height=720,
			font=dict(color=TEXT_COLOR),
			margin=dict(l=30, r=40, t=50, b=30),
		)
		fig_grid.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
		fig_grid.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
		st.plotly_chart(fig_grid, use_container_width=True)

	# 3. Sliders de Hiperparâmetros em Tempo Real
	else:
		st.markdown("#### ⚡ Ajuste Interativo de Hiperparâmetros em Tempo Real")
		st.markdown(
			"""
			<div class="academic-callout">
				Ajuste os parâmetros abaixo e clique em <b>Recomputar Modelo Dinâmico</b> para avaliar a sensibilidade das variedades aos hiperparâmetros.
			</div>
			""",
			unsafe_allow_html=True
		)

		col_h1, col_h2, col_h3 = st.columns(3)
		with col_h1:
			st.markdown("<b>Hiperparâmetros UMAP</b>", unsafe_allow_html=True)
			u_nn = st.slider("n_neighbors:", min_value=5, max_value=100, value=15, step=5)
			u_md = st.slider("min_dist:", min_value=0.01, max_value=0.8, value=0.1, step=0.05)
			u_met = st.selectbox("Métrica UMAP:", ["cosine", "euclidean", "manhattan"], index=0)

		with col_h2:
			st.markdown("<b>Hiperparâmetros t-SNE</b>", unsafe_allow_html=True)
			t_perp = st.slider("Perplexidade:", min_value=5, max_value=80, value=30, step=5)
			t_lr = st.slider("Taxa de Aprendizado (learning_rate):", min_value=50, max_value=800, value=200, step=50)

		with col_h3:
			st.markdown("<b>Hiperparâmetros LOF</b>", unsafe_allow_html=True)
			l_k = st.slider("k-vizinhos (n_neighbors):", min_value=5, max_value=50, value=20, step=5)
			l_cnt = st.slider("Contaminação (%):", min_value=0.5, max_value=10.0, value=2.0, step=0.5) / 100.0

		if st.button("⚡ Executar e Recomputar Modelo Dinâmico"):
			with st.spinner("Recomputando projeções com novos hiperparâmetros..."):
				pca_cols = [f"pca_{i+1}" for i in range(5) if f"pca_{i+1}" in df_filtered.columns]
				X_pca_sub = df_filtered[pca_cols].values

				reducer_dyn = umap.UMAP(n_neighbors=u_nn, min_dist=u_md, metric=u_met, random_state=42)
				u_dyn = reducer_dyn.fit_transform(X_pca_sub)
				df_filtered["umap_dyn_1"] = u_dyn[:, 0]
				df_filtered["umap_dyn_2"] = u_dyn[:, 1]

				lof_dyn_model = LocalOutlierFactor(n_neighbors=l_k, contamination=l_cnt, metric=u_met)
				df_filtered["lof_dyn_score"] = -lof_dyn_model.fit_predict(X_pca_sub) * lof_dyn_model.negative_outlier_factor_

				fig_dyn = px.scatter(
					df_filtered,
					x="umap_dyn_1", y="umap_dyn_2",
					color="lof_dyn_score",
					color_continuous_scale="Reds",
					hover_data={"sobject_id_str": True, "teff": ":.0f", "fe_h": ":.2f", "lof_dyn_score": ":.3f"},
					title=f"UMAP Dinâmico (n_neighbors={u_nn}, min_dist={u_md}, métrica={u_met}) com LOF Dinâmico"
				)
				fig_dyn.update_traces(marker=dict(size=4.5, opacity=0.8))
				fig_dyn.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=580, font=dict(color=TEXT_COLOR))
				fig_dyn.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
				fig_dyn.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
				st.plotly_chart(fig_dyn, use_container_width=True)

# ==============================================================================
# ABA 4: DETECÇÃO DE ANOMALIAS (RANKING & INSPEÇÃO INSTANTÂNEA)
# ==============================================================================
with tab_anomalies:
	st.markdown("### 🔍 Detecção de Anomalias & Inspeção Imediata")

	col_r1, col_r2, col_r3 = st.columns([1.5, 1.5, 3.0])
	with col_r1:
		sort_opt = st.selectbox("Ordenar por:", ["LOF Score (Decrescente)", "GLOSH Score (Decrescente)", "S/N CCD 3 (Decrescente)", "Teff (Crescente)"])
	with col_r2:
		top_qty = st.slider("Top Estrelas:", 10, 100, 25, 5)

	if "LOF" in sort_opt:
		df_top = df_filtered.sort_values(by="lof_score", ascending=False).head(top_qty)
	elif "GLOSH" in sort_opt:
		df_top = df_filtered.sort_values(by="glosh_outlier_score", ascending=False).head(top_qty)
	elif "S/N" in sort_opt:
		df_top = df_filtered.sort_values(by="snr_c3", ascending=False).head(top_qty)
	else:
		df_top = df_filtered.sort_values(by="teff", ascending=True).head(top_qty)

	dsp_cols = ["sobject_id", "lof_score", "glosh_outlier_score", "teff", "logg", "fe_h", "snr_c1", "snr_c3", "snr_c4", "rv_comp_1"]
	st.dataframe(
		df_top[dsp_cols].style.format({
			"lof_score": "{:.3f}",
			"glosh_outlier_score": "{:.3f}",
			"teff": "{:.0f}",
			"logg": "{:.2f}",
			"fe_h": "{:.2f}",
			"snr_c1": "{:.1f}",
			"snr_c3": "{:.1f}",
			"snr_c4": "{:.1f}",
			"rv_comp_1": "{:.1f}",
		}),
		use_container_width=True,
		height=300
	)

	st.markdown("#### 🔬 Inspeção Rápida: Espectro e Resíduo da Anomalia Selecionada")
	anom_sid = st.selectbox(
		"Selecione uma estrela para inspecionar:",
		options=df_top["sobject_id_str"].tolist(),
		format_func=lambda s: f"ID: {s} | LOF: {df_top[df_top['sobject_id_str']==s]['lof_score'].values[0]:.3f} | Teff: {df_top[df_top['sobject_id_str']==s]['teff'].values[0]:.0f} K"
	)

	if anom_sid and anom_sid in id_to_idx:
		idx_a = id_to_idx[anom_sid]
		f_a = X_flux_mat[idx_a]
		r_a = X_res_mat[idx_a] if len(X_res_mat)>0 else None
		m_a = f_a - r_a if r_a is not None else None

		fig_anom_sp = make_subplots(
			rows=2, cols=1,
			shared_xaxes=True,
			vertical_spacing=0.06,
			row_heights=[0.7, 0.3],
			subplot_titles=[
				f"Espectro Observado vs Modelo Sintético — {anom_sid}",
				"Resíduo Espectral (Δs = Fluxo Obs - Modelo) — Desvios positivos indicam emissão / anomalia"
			]
		)

		for ccd_k, ccd_v in CCD_BANDS.items():
			msk_a = (wave_grid >= ccd_v["min"]) & (wave_grid <= ccd_v["max"])
			if not np.any(msk_a):
				continue
			fig_anom_sp.add_trace(go.Scatter(x=wave_grid[msk_a], y=f_a[msk_a], mode="lines", name=ccd_v["name"], line=dict(color=ccd_v["color"], width=1.3)), row=1, col=1)
			if m_a is not None:
				fig_anom_sp.add_trace(go.Scatter(x=wave_grid[msk_a], y=m_a[msk_a], mode="lines", name="Modelo", line=dict(color="#f97316", width=1.1, dash="dot"), showlegend=(ccd_k==1)), row=1, col=1)
			if r_a is not None:
				fig_anom_sp.add_trace(go.Scatter(x=wave_grid[msk_a], y=r_a[msk_a], mode="lines", line=dict(color=ccd_v["color"], width=1.0), showlegend=False), row=2, col=1)

		fig_anom_sp.add_hline(y=0.0, line_dash="dash", line_color="#64748b", row=2, col=1)

		for line in KEY_ASTRO_LINES:
			fig_anom_sp.add_vline(x=line["wave"], line_dash="dot", line_color=line["color"], line_width=1.1, annotation_text=line["name"], row=1, col=1)

		fig_anom_sp.update_layout(template=PLOTLY_TEMPLATE, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=520, font=dict(color=TEXT_COLOR))
		fig_anom_sp.update_xaxes(title_text="Comprimento de Onda no Vácuo (Å)", row=2, col=1, gridcolor=GRID_COLOR, zeroline=False)
		fig_anom_sp.update_yaxes(title_text="Fluxo", row=1, col=1, gridcolor=GRID_COLOR, zeroline=False)
		fig_anom_sp.update_yaxes(title_text="Δs", row=2, col=1, gridcolor=GRID_COLOR, zeroline=False)
		st.plotly_chart(fig_anom_sp, use_container_width=True)

# ==============================================================================
# ABA 5: METODOLOGIA & FUNDAMENTAÇÃO TEÓRICA (COM LATEX NATIVO)
# ==============================================================================
with tab_theory:
	st.markdown("### 📚 Fundamentação Teórica & Metodologia Rigorosa")
	
	# 1. PARADIGMAS
	st.markdown("#### 1. Por que Aprendizado Não-Supervisionado?")
	st.markdown(
		"""
		No contexto da astrofísica observacional e de grandes *surveys* espectroscópicos como o GALAH DR4, a análise divide-se fundamentalmente em dois paradigmas:
		"""
	)

	col_th1, col_th2 = st.columns(2)
	with col_th1:
		st.markdown("##### 🔓 Aprendizado Não-Supervisionado (Nossa Abordagem)")
		st.markdown(
			r"""
			- **Entrada:** Matriz de fluxos $\mathbf{X} \in \mathbb{R}^{N \times D}$ ($N = 6.169$ estrelas, $D = 14.800$ pixels) **sem rótulos de classe prévios ($y$)**.
			- **Objetivo Científico:** *Descoberta (*Discovery*)*. Mapear a variedade intrínseca de tipos espectrais e isolar estrelas anômalas (ex: estrelas com emissão cromosférica de $H\alpha$, flares, binárias SB2, enriquecimento anômalo de Lítio) sem preconceber o que será encontrado.
			- **Vantagem:** Não induz viés de confirmação e é capaz de detectar anomalias raras únicas (ex: 1 estrela em 6.180).
			"""
		)
	with col_th2:
		st.markdown("##### 🔒 Aprendizado Supervisionado (Por que não se aplica aqui?)")
		st.markdown(
			r"""
			- **Formulação:** Minimização de risco empírico $\min_{\theta} \sum_{i=1}^N \mathcal{L}(f_\theta(\mathbf{x}_i), y_i)$.
			- **Por que NÃO se aplica ao objetivo principal de descoberta:**
			  1. **Inexistência de *Ground Truth* Completo:** Não existe um catálogo que rotule todas as possíveis anomalias físicas na amostra.
			  2. **Desbalanceamento Extremo:** Anomalias raras representam $< 0.1\%$ da amostra (ex: 5 em 6.180).
			  3. **Viés de Classificação:** Um classificador supervisionado é cego para classes novas que não constavam no treinamento.
			"""
		)

	st.markdown("---")

	# 2. LOF TERMO A TERMO
	st.markdown("#### 2. Local Outlier Factor (LOF) — Desmistificado Termo a Termo")
	st.markdown(
		r"""
		O algoritmo **LOF (Breunig et al., 2000)** mede o grau de anomalia de um ponto $p$ comparando a sua densidade local com a densidade de seus vizinhos mais próximos no espaço vetorial de alta dimensão ($14.800$ pixels com métrica Cosseno).
		"""
	)

	st.markdown(r"**Passo 1: $k$-distância de um ponto $p$ ($d_k(p)$)**")
	st.markdown(r"É a distância $d(p, o)$ entre o espectro $p$ e o seu $k$-ésimo vizinho mais próximo $o \in \mathcal{N}_k(p)$.")

	st.markdown(r"**Passo 2: Distância de Alcançabilidade (*Reachability Distance*)**")
	st.latex(r"\mathrm{reach\text{-}dist}_k(p, o) = \max \left\{ d_k(o), \, d(p, o) \right\}")
	st.markdown(r"*Significado Físico:* Se o espectro $p$ estiver muito próximo do vizinho $o$, a distância é limitada inferiormente pelo raio do cluster $d_k(o)$, evitando ruídos estatísticos do detector.")

	st.markdown(r"**Passo 3: Densidade de Alcançabilidade Local (*Local Reachability Density - LRD*)**")
	st.latex(r"\mathrm{lrd}_k(p) = \frac{|\mathcal{N}_k(p)|}{\sum_{o \in \mathcal{N}_k(p)} \mathrm{reach\text{-}dist}_k(p, o)}")
	st.markdown(r"*Significado Físico:* É o inverso da distância média de alcançabilidade dos seus $k$ vizinhos. Quanto mais compactos os vizinhos, maior é o $\mathrm{lrd}$.")

	st.markdown(r"**Passo 4: Fator de Outlier Local ($\mathrm{LOF}_k(p)$)**")
	st.latex(r"\mathrm{LOF}_k(p) = \frac{\sum_{o \in \mathcal{N}_k(p)} \frac{\mathrm{lrd}_k(o)}{\mathrm{lrd}_k(p)}}{|\mathcal{N}_k(p)|}")
	st.markdown(
		r"""
		- $\mathrm{LOF} \approx 1.0$: A estrela possui densidade similar à de seus vizinhos (**Estrela Padrão / Inlier**).
		- $\mathrm{LOF} < 1.0$: A estrela está em um núcleo superdenso da sequência principal.
		- $\mathrm{LOF} > 1.3$: A estrela reside em uma região muito mais rarefeita que seus vizinhos (**Anomalia Espectral Isolada**).
		"""
	)

	st.markdown("---")

	# 3. GLOSH TERMO A TERMO
	st.markdown("#### 3. GLOSH (*Global-Local Outlier Score from Hierarchies*) — Termo a Termo")
	st.markdown(
		"""
		O **GLOSH (Campello et al., 2015)** extrai scores de anomalia a partir da árvore de agrupamento hierárquica do algoritmo **HDBSCAN**.
		"""
	)

	st.markdown(r"**1. Escala de Densidade Recíproca ($\lambda$):**")
	st.latex(r"\lambda = \frac{1}{d_{\mathrm{mreach}}(p, o)}")

	st.markdown(r"**2. O Score GLOSH normalizado:**")
	st.latex(r"\mathrm{GLOSH}(p) = 1 - \frac{\lambda_p}{\lambda_{\mathrm{death}}(C(p))}")
	st.markdown(
		r"""
		- $\mathrm{GLOSH} \to 0$: O espectro permanece conectado ao cluster até os níveis mais finos de densidade.
		- $\mathrm{GLOSH} \to 1$: O espectro se desconecta prematuramente da árvore hierárquica (**Outlier Multiescala**).
		"""
	)

	st.markdown("---")

	# 4. COMPARATIVO PCA vs t-SNE vs UMAP & SCREE PLOT
	st.markdown("#### 4. Comparativo Rigoroso: PCA vs t-SNE vs UMAP")

	col_comp_tbl, col_scree_plot = st.columns([1.5, 1.2])

	with col_comp_tbl:
		st.markdown(
			r"""
			| Característica | **PCA** (Linear Global) | **t-SNE** (Não-Linear Local) | **UMAP Direto** (Variedade Riemanniana) |
			| :--- | :--- | :--- | :--- |
			| **Formulação** | $\mathbf{Z} = \mathbf{X}\mathbf{W}_K$ | $\min \mathcal{D}_{\mathrm{KL}}(P \parallel Q)$ | $\min \text{Fuzzy Cross Entropy}(P, Q)$ |
			| **Métrica** | Euclidiana na variância | Gaussiana $\to$ $t$-Student | **Cosseno direta nos 14.800 pixels** |
			| **Estrutura** | Variância global ($T_{\mathrm{eff}}, [\mathrm{Fe/H}]$) | Apenas vizinhança local | **Local (Anomalias) + Global (Sequência)** |
			| **Sensibilidade a Linhas Fracas** | Baixa (apaga $<0.1\%$ variância) | Média | **Alta (compara morfologia de perfis de linha)** |
			| **Necessita PCA prévio?** | É o próprio PCA | Recomendado por $O(N^2)$ | **Não necessário (direto em 14.800 px)** |
			"""
		)

	with col_scree_plot:
		pca_variances = np.array([0.2461, 0.1228, 0.0758, 0.0652, 0.0571, 0.0395, 0.0335, 0.0304, 0.0297, 0.0206])
		pca_cum = np.cumsum(pca_variances) * 100

		fig_scree = go.Figure()
		fig_scree.add_trace(go.Bar(x=[f"PC{i+1}" for i in range(10)], y=pca_variances*100, name="Variância Individual (%)", marker_color=PRIMARY_COLOR))
		fig_scree.add_trace(go.Scatter(x=[f"PC{i+1}" for i in range(10)], y=pca_cum, name="Acumulada (%)", mode="lines+markers", line=dict(color="#38bdf8", width=2)))
		fig_scree.update_layout(
			title="Scree Plot: Variância Explicada PCA (10 PCs)",
			template=PLOTLY_TEMPLATE,
			plot_bgcolor=PLOT_BG,
			paper_bgcolor=PLOT_BG,
			height=320,
			font=dict(color=TEXT_COLOR),
			margin=dict(l=30, r=20, t=40, b=30),
			legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
		)
		fig_scree.update_yaxes(title_text="%", gridcolor=GRID_COLOR, zeroline=False)
		st.plotly_chart(fig_scree, use_container_width=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
	f"""
	<div style="text-align: center; color: {MUTED_COLOR}; font-size: 0.82rem; padding: 0.8rem 0;">
		SpectraViewer Platform • GALAH DR4 & GCNS Analysis • Universidade Federal / Pesquisa Acadêmica
	</div>
	""",
	unsafe_allow_html=True
)
