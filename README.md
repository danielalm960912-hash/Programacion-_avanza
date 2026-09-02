# Calculadora de Matrices

## Descripción

Aplicación de consola desarrollada en Python que permite crear matrices
(de forma manual o aleatoria) y realizar operaciones de álgebra lineal
sobre ellas, mostrando los resultados de forma clara y controlando los
errores que puedan surgir durante su uso.

## Objetivo

Aplicar los conceptos de Programación Orientada a Objetos (clases,
objetos, atributos, métodos, constructor y encapsulación) junto con
estructuras de datos, control de flujo, validaciones y manejo de
excepciones, en el contexto de un proyecto académico de álgebra lineal.

## Tecnologías utilizadas

- Python 3

## Librerías

- `random`: librería estándar de Python, usada para generar los valores
  de las matrices aleatorias.

No se utilizan librerías externas (no se requiere `pip install` de nada
adicional); todas las operaciones matemáticas están implementadas
manualmente para poder explicarlas durante la sustentación.

## Funcionalidades

- Sumar matrices
- Restar matrices
- Multiplicar matrices
- Dividir matrices (producto de Hadamard, elemento a elemento)
- Producto cruz entre dos vectores de 3 componentes
- Calcular la matriz transpuesta
- Calcular el determinante (2x2, 3x3 y superiores)
- Calcular la matriz inversa
- Multiplicar una matriz por un escalar
- Dividir una matriz por un escalar
- Generar una matriz aleatoria
- Crear matrices de forma manual, indicando filas, columnas y valores
- Validación de dimensiones, división entre cero y entrada de datos
- Manejo de errores sin que el programa se cierre inesperadamente

## Estructura del proyecto

```
calculadora_matrices/
│
├── main.py          # Punto de entrada del programa
├── matriz.py         # Clase Matriz: representa una matriz y sus operaciones
├── calculadora.py     # Clase CalculadoraMatrices: menú, entrada de datos y validaciones
├── test_matriz.py     # Pruebas básicas de la clase Matriz
├── README.md
└── requirements.txt
```

## Cómo ejecutar el programa

1. Asegúrese de tener Python 3 instalado.
2. Ubíquese en la carpeta del proyecto desde la terminal.
3. Ejecute:

```
python main.py
```

4. Use el menú numérico para seleccionar la operación deseada.
5. Para ejecutar las pruebas:

```
python test_matriz.py
```

## Ejemplos de uso

**Sumar dos matrices 2x2:**

```
Seleccione una opcion: 1
Como desea obtener la matriz A?
1. Ingresarla manualmente
2. Generarla aleatoriamente
Seleccione una opcion: 1
Ingrese numero de filas: 2
Ingrese numero de columnas: 2
Fila 1: 1 2
Fila 2: 3 4
...
Resultado:
6.00  8.00
10.00  12.00
```

**Intentar sumar matrices de dimensiones distintas:**

```
Error: No se pueden sumar matrices de dimensiones distintas (2x2 y 1x3).
```

## Integrantes del proyecto

- Integrante 1: clase `Matriz` (suma, resta, multiplicación, Hadamard,
  producto cruz, transpuesta, determinante, inversa, operaciones con
  escalares).
- Integrante 2: clase `CalculadoraMatrices` (menú, entrada de datos,
  generación manual y aleatoria, validaciones, manejo de errores,
  pruebas y README).

Ambos integrantes participaron en el proyecto y realizaron commits
propios en el repositorio de GitHub.
