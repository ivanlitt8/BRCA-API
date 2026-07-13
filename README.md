# BCRA API Explorer

A simple [Streamlit](https://streamlit.io/) app that queries the public [BCRA](https://www.bcra.gob.ar/) (Central Bank of Argentina) statistics API and displays selected economic indicators over a date range.

## What it does

1. Fetches monetary variables from the BCRA API (category: Principales Variables).
2. Lets you pick a variable from a dropdown.
3. Asks for a start and end date.
4. Converts the series to a sorted DataFrame and shows summary metrics plus a chart (line, area, or bars).
5. Optionally shows the raw table under an expander.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt` (`streamlit`, `requests`)

## Setup and run

```bash
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

## API endpoints used

Uses **Monetary Statistics v4.0** ([OpenAPI catalog](https://www.bcra.gob.ar/archivos/Catalogo/Content/files/json/estadisticas-monetarias-v4.json)):

| Purpose | Endpoint |
| --- | --- |
| List variables | `GET /estadisticas/v4.0/Monetarias` |
| Variable time series | `GET /estadisticas/v4.0/Monetarias/{IdVariable}?Desde={date}&Hasta={date}` |

Base URL: `https://api.bcra.gob.ar/`

Time series values are returned under `results[].detalle` as `{ fecha, valor }` (Spanish field names from the API).

Requests use the `Accept-Language: es-AR` header so variable descriptions come from the API in Spanish. SSL certificate verification is currently disabled (`verify=False`) because of issues with the BCRA API certificate in some environments.

## Project structure

```
BRCA-API/
├── app.py              # Streamlit application
├── requirements.txt    # Python dependencies
└── README.md
```
