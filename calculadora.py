"""
calculadora.py

Este archivo contiene la clase CalculadoraMatrices, encargada de:
    - Mostrar el menu.
    - Pedir datos al usuario (matrices, dimensiones, escalares).
    - Validar la entrada del usuario.
    - Llamar a los metodos de la clase Matriz.
    - Mostrar los resultados o los mensajes de error.

Responsable principal: Integrante 2
"""

import random
from matriz import Matriz


class CalculadoraMatrices:
    """
    Administra el menu y la interaccion con el usuario.

    Esta clase no hace calculos matematicos directamente: para eso delega
    en la clase Matriz. Su responsabilidad es la interfaz de consola:
    mostrar opciones, leer datos, validar que lo que escribe el usuario
    tenga sentido, y mostrar resultados o errores de forma clara.
    """

    def __init__(self):
        """Constructor. Guarda si el programa debe seguir corriendo."""
        self.activo = True

    # ------------------------------------------------------------
    # Ciclo principal
    # ------------------------------------------------------------

    def ejecutar(self):
        """Bucle principal: muestra el menu hasta que el usuario elige salir."""
        while self.activo:
            self.mostrar_menu()
            opcion = input("Seleccione una opcion: ").strip()
            print()
            self.procesar_opcion(opcion)
            print()

    def mostrar_menu(self):
        print("=" * 40)
        print("       CALCULADORA DE MATRICES")
        print("=" * 40)
        print("1. Sumar matrices")
        print("2. Restar matrices")
        print("3. Multiplicar matrices")
        print("4. Dividir matrices - Hadamard")
        print("5. Producto cruz")
        print("6. Matriz transpuesta")
        print("7. Determinante")
        print("8. Matriz inversa")
        print("9. Multiplicar matriz por escalar")
        print("10. Dividir matriz por escalar")
        print("11. Generar matriz aleatoria")
        print("12. Salir")

    def procesar_opcion(self, opcion):
        """Ejecuta la operacion correspondiente a la opcion elegida, controlando errores."""
        try:
            if opcion == "1":
                self.operacion_suma()
            elif opcion == "2":
                self.operacion_resta()
            elif opcion == "3":
                self.operacion_multiplicacion()
            elif opcion == "4":
                self.operacion_hadamard()
            elif opcion == "5":
                self.operacion_producto_cruz()
            elif opcion == "6":
                self.operacion_transpuesta()
            elif opcion == "7":
                self.operacion_determinante()
            elif opcion == "8":
                self.operacion_inversa()
            elif opcion == "9":
                self.operacion_multiplicar_escalar()
            elif opcion == "10":
                self.operacion_dividir_escalar()
            elif opcion == "11":
                self.operacion_generar_aleatoria()
            elif opcion == "12":
                print("Gracias por usar la calculadora de matrices. Hasta luego.")
                self.activo = False
            else:
                print("Opcion invalida. Por favor seleccione una opcion del menu (1-12).")
        except ValueError as error:
            print(f"Error: {error}")
        except ZeroDivisionError as error:
            print(f"Error: {error}")

    # ------------------------------------------------------------
    # Entrada de datos (generacion manual y aleatoria)
    # ------------------------------------------------------------

    def leer_entero_positivo(self, mensaje):
        """Pide un numero entero mayor que cero, repitiendo hasta obtener uno valido."""
        while True:
            texto = input(mensaje).strip()
            try:
                valor = int(texto)
            except ValueError:
                print("Debe ingresar un numero entero. Intente de nuevo.")
                continue

            if valor <= 0:
                print("El valor debe ser mayor que cero. Intente de nuevo.")
                continue

            return valor

    def leer_numero(self, mensaje):
        """Pide un numero (entero o decimal), repitiendo hasta obtener uno valido."""
        while True:
            texto = input(mensaje).strip()
            try:
                return float(texto)
            except ValueError:
                print("Debe ingresar un numero valido. Intente de nuevo.")

    def leer_matriz_manual(self, nombre="A"):
        """Pide al usuario filas, columnas y los valores de una matriz, y devuelve un objeto Matriz."""
        print(f"--- Ingreso manual de la matriz {nombre} ---")
        filas = self.leer_entero_positivo("Ingrese numero de filas: ")
        columnas = self.leer_entero_positivo("Ingrese numero de columnas: ")

        print(f"Ingrese los valores de cada fila, separados por espacio ({columnas} valores por fila):")

        datos = []
        for i in range(filas):
            while True:
                texto = input(f"Fila {i + 1}: ").strip()
                valores_texto = texto.split()

                if len(valores_texto) != columnas:
                    print(f"Debe ingresar exactamente {columnas} valores. Intente de nuevo.")
                    continue

                try:
                    fila_numeros = [float(v) for v in valores_texto]
                except ValueError:
                    print("Todos los valores deben ser numeros. Intente de nuevo.")
                    continue

                datos.append(fila_numeros)
                break

        return Matriz(datos)

    def leer_vector_manual(self, nombre="A"):
        """Pide al usuario los 3 componentes de un vector para el producto cruz."""
        while True:
            texto = input(f"Ingrese los 3 componentes del vector {nombre}, separados por espacio: ").strip()
            valores_texto = texto.split()

            if len(valores_texto) != 3:
                print("Debe ingresar exactamente 3 valores. Intente de nuevo.")
                continue

            try:
                return [float(v) for v in valores_texto]
            except ValueError:
                print("Todos los valores deben ser numeros. Intente de nuevo.")

    def generar_matriz_aleatoria(self):
        """
        Pide filas, columnas, minimo y maximo, y genera una matriz con
        valores enteros aleatorios usando la libreria random.
        """
        filas = self.leer_entero_positivo("Ingrese numero de filas: ")
        columnas = self.leer_entero_positivo("Ingrese numero de columnas: ")
        minimo = self.leer_numero("Ingrese el valor minimo: ")
        maximo = self.leer_numero("Ingrese el valor maximo: ")

        if minimo > maximo:
            raise ValueError("El valor minimo no puede ser mayor que el valor maximo.")

        datos = []
        for _ in range(filas):
            fila = [random.randint(int(minimo), int(maximo)) for _ in range(columnas)]
            datos.append(fila)

        return Matriz(datos)

    def elegir_forma_de_matriz(self, nombre="A"):
        """Pregunta al usuario si quiere ingresar la matriz manualmente o generarla al azar."""
        while True:
            print(f"Como desea obtener la matriz {nombre}?")
            print("1. Ingresarla manualmente")
            print("2. Generarla aleatoriamente")
            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                return self.leer_matriz_manual(nombre)
            elif opcion == "2":
                return self.generar_matriz_aleatoria()
            else:
                print("Opcion invalida. Intente de nuevo.\n")

    # ------------------------------------------------------------
    # Operaciones del menu
    # ------------------------------------------------------------

    def operacion_suma(self):
        print("--- Suma de matrices (A + B) ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        matriz_b = self.elegir_forma_de_matriz("B")
        resultado = matriz_a.sumar(matriz_b)
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_resta(self):
        print("--- Resta de matrices (A - B) ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        matriz_b = self.elegir_forma_de_matriz("B")
        resultado = matriz_a.restar(matriz_b)
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_multiplicacion(self):
        print("--- Multiplicacion de matrices (A x B) ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        matriz_b = self.elegir_forma_de_matriz("B")
        resultado = matriz_a.multiplicar(matriz_b)
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_hadamard(self):
        print("--- Division elemento a elemento - Hadamard (A / B) ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        matriz_b = self.elegir_forma_de_matriz("B")
        resultado = matriz_a.dividir_hadamard(matriz_b)
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_producto_cruz(self):
        print("--- Producto cruz entre dos vectores de 3 componentes ---")
        vector_a = self.leer_vector_manual("A")
        vector_b = self.leer_vector_manual("B")
        resultado = Matriz.producto_cruz(vector_a, vector_b)
        print(f"Resultado: {resultado}")

    def operacion_transpuesta(self):
        print("--- Matriz transpuesta ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        resultado = matriz_a.transponer()
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_determinante(self):
        print("--- Determinante ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        resultado = matriz_a.determinante()
        print(f"Determinante: {resultado}")

    def operacion_inversa(self):
        print("--- Matriz inversa ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        resultado = matriz_a.inversa()
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_multiplicar_escalar(self):
        print("--- Multiplicar matriz por escalar ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        escalar = self.leer_numero("Ingrese el escalar: ")
        resultado = matriz_a.multiplicar_escalar(escalar)
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_dividir_escalar(self):
        print("--- Dividir matriz por escalar ---")
        matriz_a = self.elegir_forma_de_matriz("A")
        escalar = self.leer_numero("Ingrese el escalar: ")
        resultado = matriz_a.dividir_escalar(escalar)
        print("Resultado:")
        print(resultado.mostrar())

    def operacion_generar_aleatoria(self):
        print("--- Generar matriz aleatoria ---")
        matriz = self.generar_matriz_aleatoria()
        print("Matriz generada:")
        print(matriz.mostrar())
