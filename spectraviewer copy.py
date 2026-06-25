from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from astropy.io import fits


st.set_page_config(
	page_title="Spectra Viewer",
	page_icon="📈",
	layout="wide",
	initial_sidebar_state="expanded",
	)

BASE_DIR = Path(__file__).resolve().parent
SPECTRA_ROOT = BASE_DIR / "spectra" / "galah" / "dr4" / "spectra" / "hermes" / "com"

BAND_INFO = {
	1: {"name": "Blue", "color": "#4AA3FF", "approx_wavelength": 4713},
	2: {"name": "Green", "color": "#59C36A", "approx_wavelength": 5648},
	3: {"name": "Red", "color": "#FF5C4D", "approx_wavelength": 6478},
	4: {"name": "IR", "color": "#C57B57", "approx_wavelength": 7585},
}


st.markdown(
	"""
	<style>
		.stApp {
			background:
				radial-gradient(1200px 500px at 8% -10%, rgba(116, 185, 255, 0.20), rgba(116, 185, 255, 0)),
				radial-gradient(900px 500px at 92% 0%, rgba(129, 236, 236, 0.18), rgba(129, 236, 236, 0)),
				linear-gradient(180deg, #f7fbff 0%, #f2f7fd 100%);
		}
		.hero {
			padding: 0.5rem 0 0.8rem 0;
		}
		.hero h1 {
			font-size: 2.8rem;
			line-height: 1.05;
			margin-bottom: 0.35rem;
			letter-spacing: -0.03em;
		}
		.hero p {
			font-size: 1rem;
			color: #5a6775;
			margin-top: 0;
		}
		.card {
			background: rgba(255, 255, 255, 0.92);
			border: 1px solid rgba(30, 41, 59, 0.08);
			border-radius: 18px;
			padding: 1rem 1.1rem;
			box-shadow: 0 10px 35px rgba(15, 23, 42, 0.06);
			height: 100%;
		}
		.info-box {
			background: rgba(255, 255, 255, 0.84);
			border: 1px solid rgba(30, 41, 59, 0.08);
			border-radius: 16px;
			padding: 0.7rem 0.9rem;
		}
		.panel-title {
			font-weight: 700;
			color: #1f2937;
			margin: 0 0 0.3rem 0;
			padding: 0;
		}
		.stat-label {
			color: #6b7280;
			font-size: 0.82rem;
			text-transform: uppercase;
			letter-spacing: 0.08em;
			margin-bottom: 0.15rem;
		}
		.stat-value {
			color: #0f172a;
			font-size: 1.15rem;
			font-weight: 700;
		}
		.band-pill {
			display: inline-block;
			padding: 0.2rem 0.6rem;
			border-radius: 999px;
			background: #eff6ff;
			color: #1d4ed8;
			margin-right: 0.35rem;
			margin-bottom: 0.35rem;
			font-size: 0.82rem;
		}
		.block-container {
			padding-top: 1.1rem;
			padding-bottom: 1.2rem;
		}
	</style>
	""",
	unsafe_allow_html=True,
)


@lru_cache(maxsize=1024)
def resolve_spectrum_path(sobject_id: int, ccd: int) -> Path | None:
	star_id = f"{int(sobject_id):015d}"
	date_dir = star_id[:6]
	direct_path = SPECTRA_ROOT / date_dir / f"{star_id}{ccd}.fits"
	if direct_path.exists():
		return direct_path

	candidates = list(SPECTRA_ROOT.rglob(f"{star_id}{ccd}.fits"))
	if candidates:
		return candidates[0]
	return None


def extract_wavelength(header: fits.Header, n_pixels: int) -> np.ndarray:
	crval1 = header.get("CRVAL1")
	cdelt1 = header.get("CDELT1")
	crpix1 = float(header.get("CRPIX1", 1.0))

	if crval1 is None or cdelt1 is None:
		return np.arange(n_pixels, dtype=np.float64)

	pixel_index = np.arange(n_pixels, dtype=np.float64)
	return crval1 + (pixel_index + 1.0 - crpix1) * cdelt1


def read_band_spectrum(sobject_id: int, ccd: int) -> dict:
	path = resolve_spectrum_path(sobject_id, ccd)
	if path is None:
		raise FileNotFoundError(f"File not found for CCD {ccd}.")

	with fits.open(path, memmap=False) as hdul:
		header = hdul[0].header
		flux_source = hdul[1].data if len(hdul) > 1 and hdul[1].data is not None else hdul[0].data
		flux = np.asarray(flux_source, dtype=np.float64).reshape(-1)
		wavelength = extract_wavelength(header, flux.size)

		return {
			"ccd": ccd,
			"path": path,
			"header": header,
			"wavelength": wavelength,
			"flux": np.nan_to_num(flux, nan=0.0, posinf=0.0, neginf=0.0),
		}


def load_star_spectra(sobject_id: int) -> list[dict]:
	spectra = []
	missing_ccds = []
	for ccd in range(1, 5):
		try:
			spectra.append(read_band_spectrum(sobject_id, ccd))
		except FileNotFoundError:
			missing_ccds.append(ccd)

	if not spectra:
		raise FileNotFoundError(
			f"None FITS files found for sobject_id {sobject_id}."
		)

	if missing_ccds:
		raise FileNotFoundError(
			f"Missing FITS files for sobject_id {sobject_id}: CCDs {missing_ccds}."
		)

	return spectra


def collect_metadata(headers: list[fits.Header]) -> dict:
	header = headers[0]
	metadata_keys = ["TEFF_R", "LOGG_R", "FE_H_R", "A_FE_R", "SNR_AA", "RV", "E_RV"]
	return {key: header.get(key) for key in metadata_keys if header.get(key) is not None}


def load_galah_line_list() -> pd.DataFrame:
	"""Load GALAH DR4 line list from data if available.

	Primary: data/galah_dr4_important_lines.csv (official GALAH DR4 important lines)
	Fallback: data/galah_dr4_lines.csv (vital lines from spectrum_masks/vital_lines.fits)
	Expected columns: wavelength (float, Å), element (str)
	"""
	# Try important_lines first (official GALAH DR4 important lines)
	important_path = BASE_DIR / "data" / "galah_dr4_important_lines.csv"
	if important_path.exists():
		try:
			df = pd.read_csv(important_path)
			if "wavelength" in df.columns and "element" in df.columns:
				df["wavelength"] = pd.to_numeric(df["wavelength"], errors="coerce")
				df = df.dropna(subset=["wavelength"]).copy()
				if "group" not in df.columns:
					df["group"] = df["element"].apply(infer_galah_group)
				return df[["wavelength", "element", "group"]].copy()
		except Exception:
			pass

	# Fallback: Try vital_lines CSV
	csv_path = BASE_DIR / "data" / "galah_dr4_lines.csv"
	if csv_path.exists():
		try:
			df = pd.read_csv(csv_path)

			# Normalize official/alternative schemas to: wavelength, element, group
			if "wavelength" not in df.columns and "line" in df.columns:
				df["wavelength"] = pd.to_numeric(df["line"], errors="coerce")
			if "element" not in df.columns:
				df["element"] = ""

			df = df.dropna(subset=["wavelength"]).copy()
			df["wavelength"] = pd.to_numeric(df["wavelength"], errors="coerce")
			df = df.dropna(subset=["wavelength"]).copy()

			if "group" not in df.columns:
				df["group"] = df["element"].apply(infer_galah_group)

			if {"wavelength", "element", "group"}.issubset(df.columns):
				return df[["wavelength", "element", "group"]].copy()
		except Exception:
			pass

	# Fallback default lines (representative, not exhaustive)
	default = [
		{"wavelength": 4861.33, "element": "H-beta", "group": "Miscellaneous"},
		{"wavelength": 5172.68, "element": "Mg I (b)", "group": "Alpha-process"},
		{"wavelength": 5183.60, "element": "Mg I (b)", "group": "Alpha-process"},
		{"wavelength": 5167.32, "element": "Mg I (b)", "group": "Alpha-process"},
		{"wavelength": 5889.95, "element": "Na I D1", "group": "Light Odd-Z"},
		{"wavelength": 5895.92, "element": "Na I D2", "group": "Light Odd-Z"},
		{"wavelength": 6562.79, "element": "H-alpha", "group": "Miscellaneous"},
		{"wavelength": 6707.80, "element": "Li I", "group": "Miscellaneous"},
		{"wavelength": 7664.90, "element": "K I", "group": "Light Odd-Z"},
	]
	return pd.DataFrame(default, columns=["wavelength", "element", "group"])


def infer_galah_group(element_name: str) -> str:
	"""Infer GALAH group from a line element label.

	Examples of element labels: "Fe", "Fe I", "C2", "H_alpha".
	"""
	if element_name is None:
		return "Miscellaneous"

	label = str(element_name).strip()
	if not label:
		return "Miscellaneous"

	# Keep only alphabetic prefix as element token (e.g. "Fe I" -> "FE", "C2" -> "C")
	token = ""
	for ch in label:
		if ch.isalpha():
			token += ch
		else:
			break
	token = token.upper()

	if token in {"C", "N", "O", "CN", "CO", "CH"}:
		return "CNO"
	if token in {"MG", "SI", "CA", "TI"}:
		return "Alpha-process"
	if token in {"NA", "AL", "K", "SC"}:
		return "Light Odd-Z"
	if token in {"V", "CR", "MN", "FE", "CO", "NI"}:
		return "Iron-peak"
	if token in {"CU", "ZN"}:
		return "Post iron-peak"
	if token in {"Y", "BA", "LA", "ND", "EU"}:
		return "Neutron capture strong"
	if token in {"RB", "SR", "ZR", "MO", "CE", "SM"}:
		return "Neutron capture weak"
	if token in {"H", "HA", "HB", "LI", "RU", "DY", "HE"}:
		return "Miscellaneous"

	return "Miscellaneous"


def build_line_dict(lines_df: pd.DataFrame) -> dict:
	"""Return a dictionary mapping group -> list of lines with wavelengths in Å.

	Output format:
	  { group_name: [ {"wavelength": float, "element": str, "rest_wavelength": float}, ... ], "All": [...] }
	"""
	if lines_df is None or lines_df.empty:
		return {"All": []}

	# ensure columns
	df = lines_df.copy()
	if "wavelength" not in df.columns:
		return {"All": []}

	df["wavelength"] = df["wavelength"].astype(float)
	if "element" not in df.columns:
		df["element"] = ""
	if "group" not in df.columns:
		df["group"] = "Miscellaneous"

	grouped = {}
	for grp, sub in df.groupby("group"):
		lst = []
		for _, row in sub.iterrows():
			wl = float(row["wavelength"])
			lst.append({
				"wavelength": wl,
				"element": str(row.get("element", "")),
				"rest_wavelength": wl,
				"group": grp,
			})
		grouped[grp] = sorted(lst, key=lambda x: x["wavelength"])

	# All group contains every line
	all_lines = []
	for lst in grouped.values():
		all_lines.extend(lst)
	grouped["All"] = sorted(all_lines, key=lambda x: x["wavelength"])

	return grouped


GROUP_COLORS = {
	"All": "#222222",
	"CNO": "#6B8E23",
	"Alpha-process": "#1f77b4",
	"Light Odd-Z": "#ff7f0e",
	"Iron-peak": "#9467bd",
	"Post iron-peak": "#8c564b",
	"Neutron capture strong": "#e377c2",
	"Neutron capture weak": "#7f7f7f",
	"Miscellaneous": "#d62728",
}


# Groups/dictionary inspired by the GALAH Viewer grouping (display name and common elements)
GALAH_LINE_GROUPS = {
	"CNO": {"display": "CNO (C, N, O)", "elements": ["C", "N", "O"]},
	"Alpha-process": {"display": "Alpha-process (Mg, Si, Ca, Ti)", "elements": ["Mg", "Si", "Ca", "Ti"]},
	"Light Odd-Z": {"display": "Light Odd-Z (Na, Al, K, Sc)", "elements": ["Na", "Al", "K", "Sc"]},
	"Iron-peak": {"display": "Iron-peak elements (V, Cr, Mn, Fe, Co, Ni)", "elements": ["V", "Cr", "Mn", "Fe", "Co", "Ni"]},
	"Post iron-peak": {"display": "Post iron-peak elements (Cu, Zn)", "elements": ["Cu", "Zn"]},
	"Neutron capture strong": {"display": "Neutron capture strong (Y, Ba, La, Nd, Eu)", "elements": ["Y", "Ba", "La", "Nd", "Eu"]},
	"Neutron capture weak": {"display": "Neutron capture weak (Rb, Sr, Zr, Mo, Ce, Sm)", "elements": ["Rb", "Sr", "Zr", "Mo", "Ce", "Sm"]},
	"Miscellaneous": {"display": "Miscellaneous (H_alpha, H_beta, Dy, Li, Ru)", "elements": ["H_alpha", "H_beta", "Dy", "Li", "Ru"]},
}


def build_plot(sobject_id: int, spectra: list[dict]) -> go.Figure:
	# compute subplot titles including full wavelength ranges from provided spectra
	# spectra may not be ordered by CCD, so map by ccd and compute ranges
	def _make_subplot_titles(spectra_list: list[dict]) -> list[str]:
		titles = []
		spec_map = {spec['ccd']: spec for spec in spectra_list}
		for ccd in (1, 2, 3, 4):
			band = BAND_INFO.get(ccd, {})
			spec = spec_map.get(ccd)
			if spec is not None:
				wl_min = float(spec['wavelength'].min())
				wl_max = float(spec['wavelength'].max())
				titles.append(f"CCD {ccd} - {band.get('name','')} ({wl_min:.1f}–{wl_max:.1f} Å)")
			else:
				titles.append(f"CCD {ccd} - {band.get('name','')}")
		return titles

	subplot_titles = _make_subplot_titles(spectra)

	fig = make_subplots(
		rows=4,
		cols=1,
		shared_xaxes=False,
		vertical_spacing=0.12,
		subplot_titles=subplot_titles,
	)

	for row, spec in enumerate(spectra, start=1):
		band = BAND_INFO[spec["ccd"]]
		fig.add_trace(
			go.Scatter(
				x=spec["wavelength"],
				y=spec["flux"],
				mode="lines",
				line={"color": band["color"], "width": 1.5},
				hovertemplate="λ=%{x:.2f} Å<br>Flux=%{y:.4f}<extra></extra>",
				name=f"CCD {spec['ccd']} - {band['name']}",
				showlegend=False,
			),
			row=row,
			col=1,
		)

	# fig.update_layout(
	# 	template="plotly_white",
	# 	height=1120,
	# 	margin={"l": 25, "r": 25, "t": 235, "b": 55},
	# 	title={"text": f"Spectrum for sobject_id {sobject_id}", "x": 0.5, "xanchor": "center", "yanchor": "top", "y": 0.95, "font": {"size": 20, "family": "Trebuchet MS, Verdana, sans-serif"}},
  	# 	hovermode="x unified",
	# 	font={"family": "Trebuchet MS, Verdana, sans-serif"},
	# 	legend={
	# 		"orientation": "h",
	# 		"yanchor": "top",
	# 		"y": 1.15,
	# 		"xanchor": "center",
	# 		"x": 0.5,
	# 		"bgcolor": "rgba(255,255,255,0.86)",
	# 		"bordercolor": "rgba(30,41,59,0.12)",
	# 		"borderwidth": 1,
	# 		"font": {"size": 10},
	# 		"entrywidthmode": "fraction",
	# 		"entrywidth": 0.30,
	# 		"itemsizing": "constant",
	# 		"tracegroupgap": 3,
	# 		"groupclick": "togglegroup",
	# 	},
	# )

	fig.update_layout(
        template="plotly_white",
        height=1120,
        margin={"l": 25, "r": 25, "t": 300, "b": 55},
        title={"text": f"Spectrum for sobject_id {sobject_id}", "x": 0.5, "xanchor": "center", "yanchor": "top", "y": 0.98, "font": {"size": 20, "family": "Trebuchet MS, Verdana, sans-serif"}},
        hovermode="x unified",
        font={"family": "Trebuchet MS, Verdana, sans-serif"},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 1.33,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": "rgba(255,255,255,0.86)",
            "bordercolor": "rgba(30,41,59,0.12)",
            "borderwidth": 1,
            "font": {"size": 10},
            # --- MUDANÇAS PARA RESPONSIVIDADE AQUI ---
            "entrywidthmode": "pixels", # Mudado de fraction para pixels
            "entrywidth": 250,          # Define um tamanho mínimo por item em vez de % da tela
            "itemsizing": "constant",
            "tracegroupgap": 3,
            "groupclick": "togglegroup",
        },
    )

	for axis_idx in range(1, 5):
		fig.update_yaxes(title_text="Normalised Flux", row=axis_idx, col=1, zeroline=False)
		fig.update_xaxes(title_text="Wavelength (Å)", row=axis_idx, col=1, showgrid=True, gridcolor="rgba(148,163,184,0.25)")

	return fig


def build_plot_with_lines(
	sobject_id: int,
	spectra: list[dict],
	lines: pd.DataFrame | dict,
	groups: set,
	show_lines: bool,
	show_labels: bool,
	apply_rv: bool = True,
	rv_kms: float | None = None,
) -> go.Figure:
	"""Plot spectra and overlay lines.

	`lines` can be either a DataFrame (columns: wavelength, element, group) or a dict produced by `build_line_dict()`.
	"""
	fig = build_plot(sobject_id, spectra)

	# handle empty
	if not show_lines:
		return fig

	# normalize into a flat list of line dicts to plot
	to_plot = []
	if isinstance(lines, dict):
		# lines is grouped dict
		if "All" in groups:
			to_plot = lines.get("All", [])
		else:
			for g in groups:
				to_plot.extend(lines.get(g, []))
	else:
		# DataFrame
		df = lines
		if df is None or df.empty:
			return fig
		if "group" not in df.columns:
			df["group"] = "Miscellaneous"
		if "element" not in df.columns:
			df["element"] = ""
		if "All" in groups:
			iter_rows = df.itertuples(index=False)
			for row in iter_rows:
				to_plot.append({"wavelength": float(row.wavelength), "element": str(row.element), "group": str(row.group), "rest_wavelength": float(row.wavelength)})
		else:
			sel = df[df["group"].isin(list(groups))]
			for _, row in sel.iterrows():
				to_plot.append({"wavelength": float(row["wavelength"]), "element": str(row.get("element", "")), "group": str(row.get("group", "Miscellaneous")), "rest_wavelength": float(row["wavelength"])})

	if not to_plot:
		return fig

	# speed of light in km/s
	C_KMS = 299792.458

	# Track which groups have had their legend entry added
	legend_groups_added = set()

	# For each CCD subplot, overlay lines that fall into the wavelength range
	for row, spec in enumerate(spectra, start=1):
		wl_min, wl_max = float(spec["wavelength"].min()), float(spec["wavelength"].max())
		y_min, y_max = float(spec["flux"].min()), float(spec["flux"].max())

		for line in to_plot:
			grp = line.get("group", "Miscellaneous")
			rest_wl = float(line.get("rest_wavelength", line.get("wavelength")))
			obs_wl = float(line.get("wavelength", rest_wl))

			if apply_rv and rv_kms is not None:
				try:
					obs_wl = rest_wl * (1.0 + float(rv_kms) / C_KMS)
				except Exception:
					obs_wl = rest_wl

			# only draw if within this CCD wavelength range
			if obs_wl < wl_min or obs_wl > wl_max:
				continue

			color = GROUP_COLORS.get(grp, "#222222")

			# Vertical line as a trace (instead of shape) to support hover tooltips.
			hover_text = (
				f"Elemento: {line.get('element', '')}<br>"
				f"Grupo: {grp}<br>"
				f"Lambda_rest: {rest_wl:.3f} Å<br>"
				f"Lambda_obs: {obs_wl:.3f} Å"
			)

			# Only show legend entry for first line of each group
			show_legend_entry = grp not in legend_groups_added
			if show_legend_entry:
				legend_groups_added.add(grp)

			label_text = GALAH_LINE_GROUPS.get(grp, {}).get("display", grp) if show_legend_entry else None

			fig.add_trace(
				go.Scatter(
					x=[obs_wl, obs_wl],
					y=[y_min, y_max],
					mode="lines",
					line=dict(color=color, width=1, dash="dot"),
					showlegend=show_legend_entry,
					name=label_text,
					legendgroup=grp,
					hovertemplate=hover_text + "<extra></extra>",
				),
				row=row,
				col=1,
			)

			if show_labels:
				y_pos = float(spec["flux"].max()) * 0.92
				label = line.get("element", "")
				if apply_rv and rv_kms is not None:
					label = f"{label} ({rest_wl:.2f}→{obs_wl:.2f})"

				fig.add_trace(
					go.Scatter(
						x=[obs_wl],
						y=[y_pos],
						mode="markers+text",
						marker=dict(size=6, color=color),
						text=[label],
						textposition="top center",
						showlegend=False,
						legendgroup=grp,
						hoverinfo="skip",
					),
					row=row,
					col=1,
				)


	# Add legend entries for groups that had no visible lines (for completeness)
	# This ensures groups with no lines in the wavelength range still appear in the legend
	try:
		for grp in groups:
			if grp in legend_groups_added:
				continue
			color = GROUP_COLORS.get(grp, "#222222")
			label = GALAH_LINE_GROUPS.get(grp, {}).get("display", grp)
			fig.add_trace(
				go.Scatter(
					x=[None],
					y=[None],
					mode="lines",
					line=dict(color=color, width=2),
					name=label,
					legendgroup=grp,
					showlegend=True,
					hoverinfo="skip",
				),
				row=1,
				col=1,
			)
	except Exception:
		pass

	return fig


st.markdown(
	"""
	<div class="hero">
		<h1>Spectra Viewer</h1>
		<p>Search for <strong>sobject_id</strong> to load and visualize the four bands of the corresponding spectrum.</p>
  		<p>Disclaimer: This is a simple viewer for demonstration purposes only, and it's only available one of each AFGKM spectral type.</p>
	</div>
	""",
	unsafe_allow_html=True,
)

with st.sidebar:
	st.markdown("### Search")
	
	# Load available sobject_ids from class.txt
	df_classes = pd.read_csv("class.txt", sep="\t")
	id_options = [
		f"{int(row['sobject_id'])} ({row['spectral_type']})"
		for _, row in df_classes.iterrows()
	]
	default_idx = 0  # First option (A-type star)
	
	with st.form("search_form"):
		selected = st.selectbox(
			"Select Star",
			id_options,
			index=default_idx,
			help="Select a star within the classification (O, B, A, F, G, K, M)"
		)
		# Extract sobject_id from selected string (format: "ID (type)")
		input_value = int(selected.split()[0])
		submitted = st.form_submit_button("Search", type="primary", width='stretch')

	st.markdown("---")
	st.markdown("### Spectral lines (GALAH DR4)")
	lines_df = load_galah_line_list()
	# build grouped dictionary (wavelengths in Å)
	lines_dict = build_line_dict(lines_df)
	# write JSON copy for easy access (overwrite if exists)
	try:
		out_path = BASE_DIR / "data" / "galah_dr4_lines.json"
		pd.Series(lines_dict).to_json(out_path, orient="index")
	except Exception:
		pass
	GROUP_OPTIONS = [
		"All",
		"CNO",
		"Alpha-process",
		"Light Odd-Z",
		"Iron-peak",
		"Post iron-peak",
		"Neutron capture strong",
		"Neutron capture weak",
		"Miscellaneous",
	]
	default_groups = ["All"]
	selected_groups = st.multiselect("Show groups", GROUP_OPTIONS, default=default_groups)
	if not selected_groups:
		selected_groups = ["All"]
	show_lines = st.checkbox("Show spectral lines", value=True)
	show_labels = st.checkbox("Show line labels", value=False)

	st.markdown("---")
	st.markdown("### About")
	st.caption("This repository is open-source and available on [GitHub](https://github.com/pedroiff0/spectraviewer)")
	st.write("This viewer reads the joint of GNSC and GALAH DR4 FITS spectra directly from the local dataset. For more info, please check: [SAB - inProceedings](https://sab-astro.org.br/wp-content/uploads/2026/04/PedroAndrade.pdf)")
	if not lines_df.empty:
		st.caption(f"Loaded {len(lines_df)} reference lines; using local file if present. Source: [GALAH DR4 Github](https://github.com/svenbuder/GALAH_DR4/blob/main/spectrum_analysis/spectrum_masks/important_lines)")
		st.caption(f"Special thanks to the GALAH team for providing the data and line lists, which made this viewer possible!")
	


def render_intro() -> None:
	cols = st.columns(3)
	cols[0].markdown(
		'<div class="card"><div class="stat-label">Dataset</div><div class="stat-value">GALAH DR4</div></div>',
		unsafe_allow_html=True,
	)
	cols[1].markdown(
		'<div class="card"><div class="stat-label">Bands</div><div class="stat-value">4 CCD files per star</div></div>',
		unsafe_allow_html=True,
	)
	cols[2].markdown(
		'<div class="card"><div class="stat-label">Mode</div><div class="stat-value">Interactive viewer</div></div>',
		unsafe_allow_html=True,
	)


def render_top_info_panels(spectra: list[dict], metadata: dict) -> None:
	cols = st.columns(3, gap="medium")

	with cols[0]:
		st.markdown('<div class="panel-title">📊 Loaded Bands</div>', unsafe_allow_html=True)
		bands_data = []
		for spec in spectra:
			band = BAND_INFO[spec["ccd"]]
			bands_data.append({"CCD": spec["ccd"], "Name": band["name"], "Pixels": spec["wavelength"].size})
		bands_df = pd.DataFrame(bands_data).set_index("CCD")
		st.dataframe(bands_df, width='stretch')

	with cols[1]:
		st.markdown('<div class="panel-title">📁 Files</div>', unsafe_allow_html=True)
		files_data = []
		for spec in spectra:
			files_data.append({"CCD": spec["ccd"], "File": spec["path"].name})
		files_df = pd.DataFrame(files_data).set_index("CCD")
		st.dataframe(files_df, width='stretch')

	with cols[2]:
		st.markdown('<div class="panel-title">🔬 Metadata</div>', unsafe_allow_html=True)
		if metadata:
			meta_df = pd.DataFrame(metadata, index=[0]).T
			meta_df.columns = ["Value"]
			st.dataframe(meta_df, width='stretch')
		else:
			st.info("Metadata not available in the loaded FITS headers.")


render_intro()

if submitted:
	try:
		sobject_id = int(str(input_value).strip())
	except ValueError:
		st.error("Type a valid sobject_id (integer) to load the spectra.")
		st.stop()

	try:
		spectra = load_star_spectra(sobject_id)
	except FileNotFoundError as exc:
		st.error(str(exc))
		st.stop()

	metadata = collect_metadata([spec["header"] for spec in spectra])
	render_top_info_panels(spectra, metadata)

	# Full-width chart below the info panels
	rv_kms = metadata.get("RV") if metadata is not None else None
	fig = build_plot_with_lines(
		sobject_id,
		spectra,
		lines_dict,
		set(selected_groups),
		show_lines,
		show_labels,
		apply_rv=False,
		rv_kms=rv_kms,
	)
	st.plotly_chart(fig, width='stretch', config={"responsive": True})

else:
	st.info("Use the search box on the left to load a star and plot its 4 CCD bands.")

