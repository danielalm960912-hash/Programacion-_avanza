from abc import ABC, abstractmethod


class SortingAlgorithm(ABC):
    """
    Clase base abstracta para todos los algoritmos de ordenamiento.
    Define el contrato que toda subclase debe cumplir: un método
    sort() que reciba una lista de filas (diccionarios) y el nombre
    de la columna por la cual ordenar.
    """

    @abstractmethod
    def sort(self, data: list, criteria: str) -> list:
        """Ordena data según el valor de data[i][criteria] y lo devuelve."""
        pass


class BubbleSort(SortingAlgorithm):
    """Ordenamiento burbuja: compara pares adyacentes y los intercambia si están desordenados."""

    def sort(self, data: list, criteria: str) -> list:
        for i in range(len(data)):
            for j in range(len(data) - i - 1):
                if data[j][criteria] > data[j + 1][criteria]:
                    data[j], data[j + 1] = data[j + 1], data[j]
        return data


class SelectionSort(SortingAlgorithm):
    """Ordenamiento por selección: en cada vuelta busca el mínimo restante y lo coloca en su posición."""

    def sort(self, data: list, criteria: str) -> list:
        for i in range(len(data)):
            min_index = i
            for j in range(i + 1, len(data)):
                if data[j][criteria] < data[min_index][criteria]:
                    min_index = j
            data[i], data[min_index] = data[min_index], data[i]
        return data


class InsertionSort(SortingAlgorithm):
    """Ordenamiento por inserción: toma cada elemento y lo inserta en su posición correcta entre los ya ordenados."""

    def sort(self, data: list, criteria: str) -> list:
        for i in range(1, len(data)):
            key = data[i]
            j = i - 1
            while j >= 0 and data[j][criteria] > key[criteria]:
                data[j + 1] = data[j]
                j -= 1
            data[j + 1] = key
        return data


class MergeSort(SortingAlgorithm):
    """Ordenamiento por mezcla: divide la lista recursivamente y mezcla las mitades ya ordenadas."""

    def sort(self, data: list, criteria: str) -> list:
        if len(data) <= 1:
            return data

        mid = len(data) // 2
        left = self.sort(data[:mid], criteria)
        right = self.sort(data[mid:], criteria)

        return self._merge(left, right, criteria)

    def _merge(self, left, right, criteria: str):
        """Combina dos listas ya ordenadas (left y right) en una sola lista ordenada."""
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i][criteria] <= right[j][criteria]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


class QuickSort(SortingAlgorithm):
    """Ordenamiento rápido: elige un pivote y separa el resto en menores y mayores, de forma recursiva."""

    def sort(self, data: list, criteria: str) -> list:
        if len(data) <= 1:
            return data

        pivot = data[0]
        less = [x for x in data[1:] if x[criteria] <= pivot[criteria]]
        greater = [x for x in data[1:] if x[criteria] > pivot[criteria]]

        return self.sort(less, criteria) + [pivot] + self.sort(greater, criteria)


class HeapSort(SortingAlgorithm):
    """Ordenamiento por montículo (heap): construye un max-heap y extrae repetidamente el mayor elemento."""

    def sort(self, data: list, criteria: str) -> list:
        n = len(data)

        for i in range(n // 2 - 1, -1, -1):
            self._heapify(data, n, i, criteria)

        for i in range(n - 1, 0, -1):
            data[0], data[i] = data[i], data[0]
            self._heapify(data, i, 0, criteria)

        return data

    def _heapify(self, data, n, i, criteria):
        """Reorganiza el sub-árbol con raíz en i para que cumpla la propiedad de max-heap."""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and data[left][criteria] > data[largest][criteria]:
            largest = left

        if right < n and data[right][criteria] > data[largest][criteria]:
            largest = right

        if largest != i:
            data[i], data[largest] = data[largest], data[i]
            self._heapify(data, n, largest, criteria)


class CountingSort(SortingAlgorithm):
    """
    Ordenamiento por conteo: cuenta cuántas veces aparece cada valor y usa
    ese conteo para calcular directamente la posición final de cada fila.
    Los valores se escalan x100 para trabajar los decimales como enteros.
    """

    def sort(self, data: list, criteria: str) -> list:
        if len(data) == 0:
            return data

        values = [row[criteria] for row in data]
        max_val = int(max(values) * 100)
        min_val = int(min(values) * 100)
        range_size = max_val - min_val + 1

        count = [0] * range_size
        output = [None] * len(data)

        for row in data:
            index = int(row[criteria] * 100) - min_val
            count[index] += 1

        for i in range(1, range_size):
            count[i] += count[i - 1]

        for row in reversed(data):
            index = int(row[criteria] * 100) - min_val
            output[count[index] - 1] = row
            count[index] -= 1

        return output


class RadixSort(SortingAlgorithm):
    """
    Ordenamiento radix: ordena dígito por dígito (unidades, decenas, ...)
    usando counting sort como paso interno. También escala x100 para
    trabajar los decimales como enteros.
    """

    def sort(self, data, criteria):
        if len(data) == 0:
            return data

        scaled = [int(row[criteria] * 100) for row in data]
        max_val = max(scaled)

        combined = list(zip(data, scaled))

        exp = 1
        while max_val // exp > 0:
            combined = self._counting_sort_by_digit(combined, exp)
            exp *= 10

        return [row for row, _ in combined]

    def _counting_sort_by_digit(self, combined, exp):
        """Ordena combined según el dígito en la posición exp (1, 10, 100, ...)."""
        n = len(combined)
        output = [None] * n
        count = [0] * 10

        for row, scaled in combined:
            digit = (scaled // exp) % 10
            count[digit] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        for row, scaled in reversed(combined):
            digit = (scaled // exp) % 10
            output[count[digit] - 1] = (row, scaled)
            count[digit] -= 1

        return output


class BucketSort(SortingAlgorithm):
    """
    Ordenamiento por cubetas: distribuye las filas en cubetas según su
    valor, ordena cada cubeta por separado (con inserción) y las concatena.
    """

    def sort(self, data, criteria):
        if len(data) == 0:
            return data

        values = [row[criteria] for row in data]
        min_val = min(values)
        max_val = max(values)

        if min_val == max_val:
            return data

        num_buckets = len(data)
        buckets = [[] for _ in range(num_buckets)]

        for row in data:
            index = int((row[criteria] - min_val) / (max_val - min_val) * (num_buckets - 1))
            buckets[index].append(row)

        result = []

        for bucket in buckets:
            result.extend(self._insertion_sort(bucket, criteria))

        return result

    def _insertion_sort(self, data, criteria):
        """Ordenamiento por inserción, usado internamente para ordenar cada cubeta."""
        for i in range(1, len(data)):
            key = data[i]
            j = i - 1
            while j >= 0 and data[j][criteria] > key[criteria]:
                data[j + 1] = data[j]
                j -= 1
            data[j + 1] = key
        return data
    
    
    #Pruebas
    
    # if __name__ == "__main__":
    
#     url = "https://www.datos.gov.co/resource/ji8i-4anb.json"
#     api = DatasetAPI(url)
#     df = api.load_dataset()
#     real_data = df.to_dict("records")
    
    
#     sample_data = [
#         {"departamento": "A", "desercion": 5.2},
#         {"departamento": "B", "desercion": 1.8},
#         {"departamento": "C", "desercion": 3.4},
#     ]



    # bubble = BubbleSort()
    # result = bubble.sort(sample_data, "desercion")
    # print(result)
    
    # bubble = BubbleSort()
    # resultado = bubble.sort(real_data, "desercion")
    # print(resultado[:5])
    
    # selection = SelectionSort()
    # result2 = selection.sort(sample_data, "desercion")
    # print(result2)
    
    # insertion = InsertionSort()
    # result3 = insertion.sort(sample_data, "desercion")
    # print(result3)

    # merge = MergeSort()
    # result4 = merge.sort(sample_data, "desercion")
    # print(result4)

    # quick = QuickSort()
    # result5 = quick.sort(sample_data, "desercion")
    # print(result5)
    
    # real_data = df.to_dict("records")
    # quick = QuickSort()
    # result5 = quick.sort(real_data, "cobertura_neta")
    # print(result5[:5])
    
    # heap = HeapSort()
    # result6 = heap.sort(sample_data, "desercion")
    # print(result6)
    
    # counting = CountingSort()
    # result7 = counting.sort(sample_data, "desercion")
    # print(result7)
    
    # radix = RadixSort()
    # result8 = radix.sort(sample_data, "desercion")
    # print(result8)
    
    # bucket = BucketSort()
    # result9 = bucket.sort(sample_data, "desercion")
    # print(result9)