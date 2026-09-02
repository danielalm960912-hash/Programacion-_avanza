"""
matriz.py

Este archivo contiene la clase Matriz, que representa una matriz
matematica y las operaciones que se pueden realizar con ella.

Responsable principal: Integrante 1
"""


class Matriz:
    """
    Representa una matriz de numeros.

    Atributos:
        datos (list[list[float]]): los valores de la matriz, fila por fila.
        filas (int): numero de filas.
        columnas (int): numero de columnas.
    """

    def __init__(self, datos):
        """
        Constructor de la clase.

        Recibe una lista de listas (por ejemplo [[1, 2], [3, 4]]) y a
        partir de ella calcula automaticamente el numero de filas y
        columnas de la matriz. Esto evita que el usuario tenga que
        indicar las dimensiones por separado y que puedan quedar
        inconsistentes con los datos reales.
        """
        if not datos or not datos[0]:
            raise ValueError("La matriz no puede estar vacia.")

        columnas_primera_fila = len(datos[0])
        for fila in datos:
            if len(fila) != columnas_primera_fila:
                raise ValueError("Todas las filas deben tener el mismo numero de columnas.")

        self.datos = datos
        self.filas = len(datos)
        self.columnas = columnas_primera_fila

    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------

    def mostrar(self):
        """Devuelve un texto con la matriz formateada, lista para imprimir."""
        texto = ""
        for fila in self.datos:
            texto += "  ".join(f"{valor:.2f}" for valor in fila) + "\n"
        return texto

    def misma_dimension(self, otra):
        """Verdadero si esta matriz y 'otra' tienen exactamente las mismas dimensiones."""
        return self.filas == otra.filas and self.columnas == otra.columnas

    # ------------------------------------------------------------
    # Operaciones entre dos matrices
    # ------------------------------------------------------------

    def sumar(self, otra):
        """
        Suma esta matriz con 'otra', elemento a elemento.
        Condicion: ambas matrices deben tener las mismas dimensiones.
        """
        if not self.misma_dimension(otra):
            raise ValueError(
                f"No se pueden sumar matrices de dimensiones distintas "
                f"({self.filas}x{self.columnas} y {otra.filas}x{otra.columnas})."
            )

        resultado = []
        for i in range(self.filas):
            fila_resultado = []
            for j in range(self.columnas):
                fila_resultado.append(self.datos[i][j] + otra.datos[i][j])
            resultado.append(fila_resultado)

        return Matriz(resultado)

    def restar(self, otra):
        """
        Resta 'otra' a esta matriz, elemento a elemento.
        Condicion: ambas matrices deben tener las mismas dimensiones.
        """
        if not self.misma_dimension(otra):
            raise ValueError(
                f"No se pueden restar matrices de dimensiones distintas "
                f"({self.filas}x{self.columnas} y {otra.filas}x{otra.columnas})."
            )

        resultado = []
        for i in range(self.filas):
            fila_resultado = []
            for j in range(self.columnas):
                fila_resultado.append(self.datos[i][j] - otra.datos[i][j])
            resultado.append(fila_resultado)

        return Matriz(resultado)

    def multiplicar(self, otra):
        """
        Multiplica esta matriz (A) por 'otra' (B) usando la multiplicacion
        matricial tradicional: cada elemento del resultado es la suma de
        los productos de una fila de A por una columna de B.

        Condicion: columnas de A debe ser igual a filas de B.
        """
        if self.columnas != otra.filas:
            raise ValueError(
                f"No se pueden multiplicar: columnas de A ({self.columnas}) "
                f"debe ser igual a filas de B ({otra.filas})."
            )

        resultado = []
        for i in range(self.filas):
            fila_resultado = []
            for j in range(otra.columnas):
                suma = 0
                for k in range(self.columnas):
                    suma += self.datos[i][k] * otra.datos[k][j]
                fila_resultado.append(suma)
            resultado.append(fila_resultado)

        return Matriz(resultado)

    def dividir_hadamard(self, otra):
        """
        Division elemento a elemento (producto de Hadamard, version division):
        resultado[i][j] = A[i][j] / B[i][j]

        Condiciones:
            - Ambas matrices deben tener las mismas dimensiones.
            - Ningun elemento de 'otra' puede ser cero.
        """
        if not self.misma_dimension(otra):
            raise ValueError(
                f"No se pueden dividir matrices de dimensiones distintas "
                f"({self.filas}x{self.columnas} y {otra.filas}x{otra.columnas})."
            )

        resultado = []
        for i in range(self.filas):
            fila_resultado = []
            for j in range(self.columnas):
                if otra.datos[i][j] == 0:
                    raise ZeroDivisionError(
                        f"No se puede dividir: el elemento en la posicion "
                        f"({i + 1},{j + 1}) de la segunda matriz es cero."
                    )
                fila_resultado.append(self.datos[i][j] / otra.datos[i][j])
            resultado.append(fila_resultado)

        return Matriz(resultado)

    @staticmethod
    def producto_cruz(vector_a, vector_b):
        """
        Calcula el producto cruz entre dos vectores de 3 componentes.

        Formula:
            A x B = [ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx]

        Es un metodo estatico porque no depende de una instancia especifica
        de Matriz: recibe dos listas simples de 3 numeros y devuelve otra.
        """
        if len(vector_a) != 3 or len(vector_b) != 3:
            raise ValueError("El producto cruz solo esta definido para vectores de 3 componentes.")

        ax, ay, az = vector_a
        bx, by, bz = vector_b

        resultado = [
            ay * bz - az * by,
            az * bx - ax * bz,
            ax * by - ay * bx,
        ]
        return resultado

    # ------------------------------------------------------------
    # Operaciones unarias (sobre una sola matriz)
    # ------------------------------------------------------------

    def transponer(self):
        """
        Devuelve la matriz transpuesta: las filas pasan a ser columnas.
        Una matriz de m x n se convierte en una de n x m.
        """
        resultado = []
        for j in range(self.columnas):
            fila_resultado = []
            for i in range(self.filas):
                fila_resultado.append(self.datos[i][j])
            resultado.append(fila_resultado)

        return Matriz(resultado)

    def determinante(self):
        """
        Calcula el determinante de una matriz cuadrada.

        Se implementa de forma directa para matrices 2x2 y 3x3 (los casos
        pedidos como minimo), y de forma general por expansion de cofactores
        (recursiva) para matrices cuadradas mas grandes, ya que ese metodo
        es facil de explicar: se elige la primera fila y el determinante se
        calcula como la suma de cada elemento multiplicado por el
        determinante de la submatriz que resulta al eliminar su fila y
        columna, con signos alternados.
        """
        if self.filas != self.columnas:
            raise ValueError("El determinante solo se puede calcular para matrices cuadradas.")

        return self._determinante_recursivo(self.datos)

    def _determinante_recursivo(self, matriz):
        """Metodo auxiliar (no se usa directamente desde el menu) para calcular el determinante."""
        n = len(matriz)

        # Caso base: matriz 1x1
        if n == 1:
            return matriz[0][0]

        # Caso base: matriz 2x2 (formula directa)
        if n == 2:
            return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]

        # Caso general: expansion de cofactores sobre la primera fila
        determinante_total = 0
        for columna in range(n):
            submatriz = self._eliminar_fila_columna(matriz, 0, columna)
            signo = (-1) ** columna
            determinante_total += signo * matriz[0][columna] * self._determinante_recursivo(submatriz)

        return determinante_total

    def _eliminar_fila_columna(self, matriz, fila_a_eliminar, columna_a_eliminar):
        """Devuelve una copia de 'matriz' sin la fila y columna indicadas (usado para el determinante y la inversa)."""
        nueva_matriz = []
        for i, fila in enumerate(matriz):
            if i == fila_a_eliminar:
                continue
            nueva_fila = [valor for j, valor in enumerate(fila) if j != columna_a_eliminar]
            nueva_matriz.append(nueva_fila)
        return nueva_matriz

    def inversa(self):
        """
        Calcula la matriz inversa usando el metodo de la matriz adjunta:

            A^-1 = (1 / det(A)) * adj(A)

        donde adj(A) es la transpuesta de la matriz de cofactores.

        Condiciones:
            - La matriz debe ser cuadrada.
            - Su determinante debe ser diferente de cero.
        """
        if self.filas != self.columnas:
            raise ValueError("Solo se puede calcular la inversa de una matriz cuadrada.")

        det = self.determinante()
        if det == 0:
            raise ValueError("La matriz no tiene inversa porque su determinante es cero.")

        n = self.filas

        # Caso especial 1x1, para no complicar el caso general
        if n == 1:
            return Matriz([[1 / self.datos[0][0]]])

        # Matriz de cofactores
        matriz_cofactores = []
        for i in range(n):
            fila_cofactores = []
            for j in range(n):
                submatriz = self._eliminar_fila_columna(self.datos, i, j)
                signo = (-1) ** (i + j)
                fila_cofactores.append(signo * self._determinante_recursivo(submatriz))
            matriz_cofactores.append(fila_cofactores)

        # La adjunta es la transpuesta de la matriz de cofactores
        matriz_adjunta = Matriz(matriz_cofactores).transponer()

        # Cada elemento de la adjunta se divide entre el determinante
        resultado = []
        for i in range(n):
            fila_resultado = []
            for j in range(n):
                fila_resultado.append(matriz_adjunta.datos[i][j] / det)
            resultado.append(fila_resultado)

        return Matriz(resultado)

    # ------------------------------------------------------------
    # Operaciones con escalares
    # ------------------------------------------------------------

    def multiplicar_escalar(self, escalar):
        """Multiplica cada elemento de la matriz por un numero (escalar)."""
        resultado = []
        for fila in self.datos:
            fila_resultado = [valor * escalar for valor in fila]
            resultado.append(fila_resultado)
        return Matriz(resultado)

    def dividir_escalar(self, escalar):
        """Divide cada elemento de la matriz por un numero (escalar). El escalar no puede ser cero."""
        if escalar == 0:
            raise ZeroDivisionError("No se puede dividir la matriz entre cero.")

        resultado = []
        for fila in self.datos:
            fila_resultado = [valor / escalar for valor in fila]
            resultado.append(fila_resultado)
        return Matriz(resultado)
