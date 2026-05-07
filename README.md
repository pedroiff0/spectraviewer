# SpectraViewer - GALAH DR4 Spectra Viewer

An interactive viewer for spectra from the GALAH DR4 catalog (Galactic Archeology with Hermes Data Release 4). The application allows you to explore stellar spectra intuitively, with support for multiple bands, reference spectral lines, and automatic spectral classification.

## 🌟 Features

- **Interactive Visualization**: Plotting of 4 spectral bands (Blue, Green, Red, IR) with interactive interface
- **Spectral Lines**: Overlay of reference spectral lines from GALAH DR4 with groups (CNO, Alpha-process, Iron-peak, etc.)
- **Local Data**: Direct reading of FITS files from the local dataset
- **Stellar Metadata**: Display of information such as Teff, log(g), [Fe/H] and other abundances

## 📋 Requirements

- Python 3.8+
- GALAH DR4 Datasets (FITS files)

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/pedroiff0/spectraviewer.git
cd spectraviewer
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Run locally

```bash
streamlit run spectraviewer.py
```

The application will open at `http://localhost:8501`.

### Using the application

1. **Search**: Select a star from the dropdown menu
2. **View Spectrum**: The 4-band spectrum will be loaded and displayed
3. **Spectral Lines**: Select groups of spectral lines to overlay on the spectrum
4. **Labels**: Enable the "Show line labels" option to display line identifications

## 📊 Data Structure

### FITS Spectra
- Location: `spectra/galah/dr4/spectra/hermes/com/{YYMMDD}/`
- File: `{sobject_id}{CCD}.fits`
- Bands:
  - CCD 1: Blue (~4713 Å)
  - CCD 2: Green (~5648 Å)  
  - CCD 3: Red (~6478 Å)
  - CCD 4: IR (~7585 Å)

### FITS Metadata
- TEFF_R: Effective temperature
- LOGG_R: log(g) - surface gravity
- FE_H_R: Metallicity [Fe/H]
- A_FE_R: Abundance [α/Fe]
- SNR_AA: Signal-to-noise ratio in Ångströms
- RV: Radial velocity
- E_RV: Error in radial velocity

## 📚 References

- [GALAH DR4 Survey](https://www.galah-survey.org/)
- [Gaia-ESO Spectroscopic Survey](http://www.gaia-eso.eu/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Astropy FITS](https://docs.astropy.org/en/stable/io/fits/)

## 🛠️ Development

### Project Structure
```
spectraviewer/
├── spectraviewer.py          # Main application
├── requirements.txt          # Python dependencies
├── class.txt                 # Spectral classification catalog
├── spectra/                  # Data (included with samples)
│   └── galah/
│       └── dr4/
│           └── spectra/      # FITS spectrum files
├── venv/                     # Virtual environment
└── README.md                 # This file
```

### Adding New Features

1. Modify `spectraviewer.py`
2. Test locally: `streamlit run spectraviewer.py`
3. Commit and push to GitHub

## 🐛 Troubleshooting

### "File not found" for spectra
- Verify that FITS files exist in `spectra/galah/dr4/spectra/hermes/com/`
- Confirm that the `sobject_id` is correct (15 digits)

### Spectral lines do not appear
- Verify that the line list file exists
- Confirm that the wavelengths of the lines are within the spectral coverage range

### Slow performance
- Resize the plots
- Reduce the number of selected line groups
- Check disk read speed for FITS files

## 📝 License

This project uses data from the GALAH DR4 Survey. Respect the terms of use of the data.

## 👥 Contributions

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For questions, bug reports or suggestions, open an issue in the repository.

---

**Last update**: May 2026  
**Version**: 1.0.0
