# Práctica de Laboratorio 1: Construyendo un Tokenizador BPE desde Cero

**Módulo:** 1 – Introducción y Tokenización

**Duración estimada:** 3 horas

**Modalidad:** Individual

**Lenguaje:** Python 3.x (sin librerías de NLP)

---

# Objetivos

Al finalizar esta práctica serán capaces de:

- Comprender por qué los LLM no trabajan con palabras sino con **tokens**.
- Implementar un algoritmo simplificado de **Byte Pair Encoding (BPE)**.
- Analizar cómo cambia el vocabulario a medida que se realizan fusiones (merges).
- Comparar diferentes tamaños de vocabulario y su impacto sobre la tokenización.

---

# Contexto

Los modelos de lenguaje no almacenan todas las palabras posibles del idioma.

En su lugar construyen un **vocabulario finito** formado por caracteres, sílabas o fragmentos frecuentes.

Por ejemplo:

```
computadora
```

puede terminar convirtiéndose en

```
["comp", "uta", "dora"]
```

o

```
["comput", "adora"]
```

dependiendo del vocabulario aprendido.

El objetivo de esta práctica es construir ese proceso desde cero.

---

# Parte 1 – Preparación del Corpus

Usar dos corpus de entrenamiento.

Corpus A:

```
el perro corre
el perro juega
el gato corre
el gato duerme
el perro duerme
la casa es grande
la casa tiene patio
```

Corpus B:
El archivo en https://gist.github.com/jsdario/6d6c69398cb0c73111e49f1218960f79

Mostrar para cada corpus:

- cantidad de palabras
- vocabulario inicial

---

# Parte 2 – Tokenización Inicial

Representar cada palabra como una secuencia de caracteres.

Agregar un marcador de fin de palabra.

Por ejemplo

```
perro
```

debe almacenarse como

```
p e r r o </w>
```

y

```
gato
```

como

```
g a t o </w>
```

Mostrar el resultado para todas las palabras del corpus A.

---

# Parte 3 – Conteo de Frecuencias

Implementar una función

```
count_pairs(corpus)
```

que devuelva la frecuencia de todos los pares consecutivos.

Ejemplo:

```
p e r r o
```

produce incialmente los pares

```
(p,e)
(e,r)
(r,r)
(r,o)
(o,</w>)
```

La función sobre todo el corpus A debe devolver algo similar a

```
('e','r') -> 5
('r','r') -> 5
('o','</w>') -> 6
...
```

Mostrar los **10 pares más frecuentes** para el corpus A y el B.

---

# Parte 4 – Primera Fusión BPE

Seleccionar el par más frecuente y fusionarlo.

Ejemplo

Si

```
('e','r')
```

es el más frecuente,

entonces

```
p e r r o
```

se transforma en

```
p er r o
```

Actualizar todo el corpus.

Mostrar:

- par fusionado
- corpus antes
- corpus después

---

# Parte 5 – Entrenamiento Completo

Repetir el proceso anterior **50 iteraciones**.

Guardar el historial de fusiones.

Ejemplo:

```
1. ('e','r')
2. ('er','r')
3. ('p','er')
4. ...
```

Al finalizar mostrar:

```
Cantidad inicial de tokens

Cantidad final de tokens

Tamaño del vocabulario
```

---

# Parte 6 - Diferentes iteraciones

Realizar el entrenamiento con distinta cantidad de iteraciones.

Por ejemplo:

- 30 fusiones
- 60 fusiones
- 100 fusiones

Comparar entre sí y con el primer entrenamiento:

- cantidad promedio de tokens por palabra
- tamaño del vocabulario
- tiempo de entrenamiento

Representar los resultados mediante un gráfico.

---

# Parte 7 – Tokenizar Nuevas Palabras

Utilizando los merges aprendidos, tokenizar palabras que no estaban en el corpus.

Por ejemplo

```
perritos
gatitos
casita
casitas
corriendo
```

Mostrar el resultado.

Ejemplo

```
perritos

↓

["perr","it","os"]
```

(No importa si el resultado no es perfecto; debe respetar las reglas aprendidas.)

---

# Preguntas finales

- ¿Por qué BPE reduce el tamaño del vocabulario?
- ¿Qué ventajas tiene respecto a tokenizar por palabras completas?
- ¿Qué problemas aparecen si el vocabulario es demasiado pequeño?
- ¿Qué problemas aparecen si el vocabulario es demasiado grande?
