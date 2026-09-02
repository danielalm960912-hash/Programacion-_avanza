"""
main.py

Punto de entrada del programa. Crea un objeto CalculadoraMatrices
y ejecuta el menu principal.
"""

from calculadora import CalculadoraMatrices


def main():
    calculadora = CalculadoraMatrices()
    calculadora.ejecutar()


if __name__ == "__main__":
    main()
