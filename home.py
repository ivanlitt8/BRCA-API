import streamlit as st
import requests

# Función para obtener las principales variables
def obtener_principales_variables():
    url = "https://api.bcra.gob.ar/estadisticas/v1/principalesvariables"
    headers = {"Accept-Language": "es-AR"}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return None

# Función para obtener los datos de una variable específica
def obtener_datos_variable(id_variable, desde, hasta):
    url = f"https://api.bcra.gob.ar/estadisticas/v1/datosvariable/{id_variable}/{desde}/{hasta}"
    headers = {"Accept-Language": "es-AR"}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return None

# Función principal de la aplicación Streamlit
def main():
    st.title("Consulta de Datos BCRA")

    # Obtener las principales variables y mostrarlas en un select
    principales_variables = obtener_principales_variables()
    if principales_variables:
        variable_seleccionada = st.selectbox("Seleccione una variable:", [f"{v['idVariable']} - {v['descripcion']}" for v in principales_variables])

        # Dividir el ID de la variable seleccionada
        id_variable = int(variable_seleccionada.split(" - ")[0])

        # Solicitar las fechas de inicio y fin
        desde = st.date_input("Desde:")
        hasta = st.date_input("Hasta:")

        # Obtener los datos de la variable seleccionada y mostrarlos
        datos = obtener_datos_variable(id_variable, desde, hasta)
        if datos:
            st.write("Datos obtenidos:")
            for dato in datos:
                st.write(f"Fecha: {dato['fecha']}, Valor: {dato['valor']}")
        else:
            st.error("Error al obtener los datos.")
    else:
        st.error("Error al obtener las variables.")

if __name__ == "__main__":
    main()
