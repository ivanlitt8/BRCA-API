import requests

def obtener_principales_variables():
    url = "https://api.bcra.gob.ar/estadisticas/v1/principalesvariables"
    headers = {"Accept-Language": "es-AR"}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()["results"]
        for variable in data:
            print(f'ID: {variable["idVariable"]}, Descripción: {variable["descripcion"]}')
    else:
        print("Error al obtener las variables")

def obtener_datos_variable(id_variable, desde, hasta):
    url = f"https://api.bcra.gob.ar/estadisticas/v1/datosvariable/{id_variable}/{desde}/{hasta}"
    headers = {"Accept-Language": "es-AR"}
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()["results"]
        for dato in data:
            print(f'Fecha: {dato["fecha"]}, Valor: {dato["valor"]}')
    elif response.status_code == 404:
        print("No se encontraron datos para el rango de fechas seleccionadas.")
    else:
        print("Error al obtener los datos")

# Ejemplo de uso
if __name__ == "__main__":
    print("Principales variables disponibles:")
    obtener_principales_variables()
    id_variable = int(input("Ingrese el ID de la variable que desea consultar: "))
    desde = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
    hasta = input("Ingrese la fecha de fin (YYYY-MM-DD): ")
    obtener_datos_variable(id_variable, desde, hasta)
