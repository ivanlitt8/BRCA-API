import streamlit as st
import pandas as pd
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://api.bcra.gob.ar/estadisticas/v4.0"
HEADERS = {"Accept-Language": "es-AR"}
DATA_LIMIT = 1000


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_main_variables():
    response = requests.get(
        f"{BASE_URL}/Monetarias",
        headers=HEADERS,
        params={"Categoria": "Principales Variables", "Limit": DATA_LIMIT},
        verify=False,
        timeout=30,
    )
    if response.status_code == 200:
        return response.json().get("results") or []
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_variable_data(variable_id, start_date, end_date):
    response = requests.get(
        f"{BASE_URL}/Monetarias/{variable_id}",
        headers=HEADERS,
        params={
            "Desde": start_date.isoformat(),
            "Hasta": end_date.isoformat(),
            "Limit": DATA_LIMIT,
        },
        verify=False,
        timeout=30,
    )
    if response.status_code != 200:
        return None, None

    payload = response.json()
    results = payload.get("results") or []
    metadata = payload.get("metadata") or {}
    details = results[0].get("detalle") or [] if results else []
    return details, metadata


def details_to_dataframe(details):
    df = pd.DataFrame(details)
    if df.empty:
        return df

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["fecha", "valor"]).sort_values("fecha").reset_index(drop=True)
    return df


def format_number(value):
    """Format numbers without scientific notation, with thousands separators."""
    if value is None or pd.isna(value):
        return "-"

    number = float(value)
    if abs(number - round(number)) < 1e-9:
        return f"{number:,.0f}"

    return f"{number:,.4f}".rstrip("0").rstrip(".")


def main():
    st.title("BCRA Data Explorer")

    main_variables = fetch_main_variables()
    if not main_variables:
        st.error("Failed to fetch variables.")
        return

    options = {
        f"{v['idVariable']} - {v['descripcion']}": v for v in main_variables
    }
    label = st.selectbox("Select a variable:", list(options.keys()))
    variable = options[label]

    start_col, end_col = st.columns(2)
    with start_col:
        start_date = st.date_input("From:", value=datetime(2024, 8, 8))
    with end_col:
        end_date = st.date_input("To:", value=datetime.today())

    if start_date > end_date:
        st.error("The start date cannot be after the end date.")
        return

    details, metadata = fetch_variable_data(variable["idVariable"], start_date, end_date)
    if details is None:
        st.error("Failed to fetch data.")
        return

    df = details_to_dataframe(details)
    if df.empty:
        st.warning("No data available for the selected date range.")
        return

    resultset = (metadata or {}).get("resultset") or {}
    total = resultset.get("count")
    if total and total > len(df):
        st.warning(
            f"The API returned {len(df)} of {total} points (limit {DATA_LIMIT}). "
            "Shorten the date range to see the full series."
        )

    unit = variable.get("unidadExpresion") or "Value"
    periodicity = variable.get("periodicidad") or "-"

    st.caption(
        f"{variable.get('descripcion')} · Unit: {unit} · Periodicity: {periodicity}"
    )

    first = df.iloc[0]
    last = df.iloc[-1]
    change = last["valor"] - first["valor"]
    change_pct = (change / first["valor"] * 100) if first["valor"] else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Latest value", format_number(last["valor"]))
    m2.metric(
        "Period change",
        format_number(change),
        None if change_pct is None else f"{change_pct:+.2f}%",
    )
    m3.metric("Minimum", format_number(df["valor"].min()))
    m4.metric("Maximum", format_number(df["valor"].max()))

    chart_df = df.set_index("fecha")[["valor"]].rename(columns={"valor": unit})

    default_chart = "Bar" if len(df) <= 30 else "Line"
    chart_type = st.radio(
        "Chart type",
        ["Line", "Area", "Bar"],
        index=["Line", "Area", "Bar"].index(default_chart),
        horizontal=True,
    )

    if chart_type == "Line":
        st.line_chart(chart_df, use_container_width=True)
    elif chart_type == "Area":
        st.area_chart(chart_df, use_container_width=True)
    else:
        st.bar_chart(chart_df, use_container_width=True)

    with st.expander("View data table"):
        table = df.copy()
        table = table.rename(columns={"fecha": "date", "valor": "value"})
        table["date"] = table["date"].dt.strftime("%Y-%m-%d")
        table["value"] = table["value"].map(format_number)
        st.dataframe(table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
