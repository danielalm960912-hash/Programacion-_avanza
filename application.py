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
        Muestra las columnas numéricas disponibles y pide al usuario
        que elija una para usarla como criterio de ordenamiento.

        Args:
            df: DataFrame ya cargado, del cual se sacan las columnas numéricas.

        Returns:
            El nombre (str) de la columna elegida.
        """
        numeric_columns = df.select_dtypes(include="number").columns

        while True:
            print("Columnas disponibles para ordenar:")
            for col in numeric_columns:
                print(col)

            criteria = input("Escribe el nombre de la columna: ")

            if criteria in numeric_columns:
                return criteria
            else:
                print("Error, opción no válida")

    def run(self):
        """
        Punto de entrada principal: carga el dataset, valida que no
        venga vacío, pide algoritmo y criterio al usuario, ordena los
        datos y muestra los primeros 10 resultados.
        """
        df = self.api.load_dataset()

        if df.empty:
            print("No se pudieron cargar los datos. Terminando el programa.")
            return

        data = df.to_dict("records")

        algorithm = self.select_algorithm()
        criteria = self.select_criteria(df)

        sorted_data = algorithm.sort(data, criteria)

        print(f"\nResultados ordenados por '{criteria}':")
        for row in sorted_data[:10]:
            print(row)


if __name__ == "__main__":
    url = "https://www.datos.gov.co/resource/ji8i-4anb.json"
    app = Application(url)
    app.run()