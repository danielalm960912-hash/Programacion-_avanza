import pandas as pd
from api_pandas import DatasetAPI
from sorting_algorithm import BubbleSort, SelectionSort, InsertionSort, MergeSort, QuickSort, HeapSort, CountingSort, RadixSort, BucketSort



class Application:
    """
    Orquesta la aplicación: conecta con DatasetAPI, deja al usuario
    elegir un algoritmo de ordenamiento y una columna (criterio), y
    muestra el resultado ordenado.
    """

    def __init__(self, url):
        """Guarda la URL del dataset y arma el diccionario de algoritmos disponibles."""
        self.url = url
        self.api = DatasetAPI(url)

        self.algorithms = {
            '1': ('Bubble Sort', BubbleSort()),
            '2': ('Selection Sort', SelectionSort()),
            '3': ('Insertion Sort', InsertionSort()),
            '4': ('Merge Sort', MergeSort()),
            '5': ('Quick Sort', QuickSort()),
            '6': ('Heap Sort', HeapSort()),
            '7': ('Counting Sort', CountingSort()),
            '8': ('Radix Sort', RadixSort()),
            '9': ('Bucket Sort', BucketSort()),
        }

    def select_algorithm(self):
        """
        Muestra el menú de algoritmos y pide al usuario que elija uno.
        Repite la pregunta si la opción no es válida, hasta obtener
        una elección correcta.

        Returns:
            La instancia del algoritmo elegido (objeto SortingAlgorithm).
        """
        while True:
            print("Elige un algoritmo:")
            for key, (name, algorithm) in self.algorithms.items():
                print(f"{key}. {name}")

            choice = input("Opción: ")

            if choice in self.algorithms:
                return self.algorithms[choice][1]
            else:
                print("Error, opción no válida")
                
    def select_criteria(self, df):
        """
        Muestra las columnas numéricas disponibles con un número y pide
        al usuario que elija una para usarla como criterio de ordenamiento.

        Args:
            df: DataFrame ya cargado, del cual se sacan las columnas numéricas.

        Returns:
            El nombre (str) de la columna elegida.
        """
        numeric_columns = df.select_dtypes(include="number").columns
        options = {str(i): col for i, col in enumerate(numeric_columns, start=1)}

        while True:
            print("Elige la columna para ordenar:")
            for key, col in options.items():
                print(f"{key}. {col}")

            choice = input("Opción: ")

            if choice in options:
                return options[choice]
            else:
                print("Error, opción no válida")

    def show_dataframe(self, df, title, columns, rows=10):
        """Muestra las primeras filas de un DataFrame, solo con las columnas indicadas."""
        print(f"\n{title}")
        print(df[columns].head(rows).to_string(index=False, max_colwidth=20))
        print()

    def ask_yes_no(self, message):
        """Pregunta s/n y repite hasta recibir una respuesta válida."""
        while True:
            answer = input(message).strip().lower()
            if answer in ("s", "n"):
                return answer == "s"
            print("Error, responde 's' o 'n'")



    def run(self):
        """
        Carga el dataset una sola vez y repite el ciclo de ordenamiento
        hasta que el usuario decida terminar.
        """
        df = self.api.load_dataset()

        # Si falla la carga, no se cierra: pregunta si quiere reintentar
        while df.empty:
            print("No se pudieron cargar los datos.")
            if not self.ask_yes_no("¿Deseas intentarlo de nuevo? (s/n): "):
                print("Programa finalizado.")
                return
            df = self.api.load_dataset()

        while True:
            # CAMBIO 1: ver los datos ANTES de elegir algoritmo y criterio
            preview_columns = ["ano", "departamento"] + list(df.select_dtypes(include="number").columns)
            self.show_dataframe(df, "Vista previa de los datos originales:", preview_columns, rows=5)

            algorithm = self.select_algorithm()
            criteria = self.select_criteria(df)

            # Counting y Radix solo funcionan con números enteros
            if isinstance(algorithm, (CountingSort, RadixSort)):
                values = df[criteria].dropna()
                if not (values % 1 == 0).all():
                    print(f"\n{type(algorithm).__name__} solo funciona con números enteros y la columna '{criteria}' tiene decimales.")
                    print("Elige otro algoritmo u otra columna.\n")
                    continue         
            
            
            
            # Quitar filas sin valor en el criterio (evita errores con NaN)
            data = df.dropna(subset=[criteria]).to_dict("records")

            # Si un algoritmo falla, se muestra el error pero el programa sigue
            try:
                sorted_data = algorithm.sort(data, criteria)
            except Exception as e:
                print(f"Ocurrió un error al ordenar: {e}")
            else:
                # CAMBIO 1: ver los datos DESPUÉS de ordenar,
                # con la columna del criterio de primera para comprobarlo fácil
                sorted_df = pd.DataFrame(sorted_data)
                self.show_dataframe(sorted_df, f"Datos ordenados por '{criteria}':", preview_columns)

            # CAMBIO 2: solo termina si el usuario lo decide
            if not self.ask_yes_no("¿Deseas ordenar de nuevo? (s/n): "):
                print("Programa finalizado. ¡Hasta pronto!")
                break


if __name__ == "__main__":
    url = "https://www.datos.gov.co/resource/ji8i-4anb.json"
    app = Application(url)
    app.run()

