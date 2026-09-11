import pandas as pd
import requests


class DatasetAPI:
    def __init__(self, url):
        self.url = url
        self.df = None

    def fetch_data(self): # Obtener datos
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()
            self.df = pd.DataFrame(data)
        except requests.exceptions.RequestException as e:
            print(f"Error al consumir la API: {e}")
            self.df = pd.DataFrame()  # evita que truene más abajo si falla
    

    def clean_data(self): # Limpiar datos
        numeric_columns = [
        "cobertura_neta", "cobertura_bruta", "desercion",
        "aprobacion", "reprobacion", "repitencia"
        ]
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

    def load_dataset(self): # Cargar datos
        self.fetch_data()
        self.clean_data()
        return self.df


if __name__ == "__main__":
    link = "https://www.datos.gov.co/resource/ji8i-4anb.json"
    api = DatasetAPI(link)
    df = api.load_dataset()
    print(df.dtypes)