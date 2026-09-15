
------------------------------
## Trabajo Práctico: Visualización de Atención y Control de Generación en LLMs 
Objetivos

   1. Comprender cómo los modelos de lenguaje transforman palabras en conceptos continuos.
   2. Visualizar el mecanismo de atención para entender cómo el modelo descifra el contexto.
   3. Experimentar con los hiperparámetros de generación para controlar la creatividad y aleatoriedad del texto.

------------------------------
## Partes del Trabajo Práctico

NOTA:
Para resolver este TP, tenés que abrir un cuaderno de Google Colab e instalar las siguientes librerías al inicio:
!pip install transformers torch bertviz

------------------------------
## Parte 1: De Palabras a Vectores (Embeddings)
En la computación tradicional, las palabras son fichas discretas (tokens). Para un modelo, "perro" y "gato" son tan distintos como "perro" y "computadora". Los Embeddings solucionan esto: mudan las palabras a un espacio de conceptos continuo. 
Cada palabra se convierte en una lista de números (un vector). Si dos palabras comparten significado o contexto, sus vectores estarán cerca en ese espacio conceptual. 
## Ejercicio Práctico 1
Ejecutá el siguiente código para extraer el embedding de una palabra usando un modelo Transformer básico (BERT).

import torchfrom transformers import AutoTokenizer, AutoModel
# Cargamos el tokenizador y el modelotokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")model = AutoModel.from_pretrained("bert-base-uncased")
# Palabra a procesarpalabra = "apple"inputs = tokenizer(palabra, return_tensors="pt")
# Extraemos los embeddingswith torch.no_grad():
    outputs = model(**inputs)
# El vector conceptual de la palabraembedding_vector = outputs.last_hidden_state[0][1] # Ignoramos tokens especiales
print(f"Dimensión del vector de '{palabra}': {embedding_vector.shape}")
print(f"Primeros 5 valores del vector: {embedding_vector[:5].tolist()}")

## Preguntas de control

   1. ¿De cuántas dimensiones (números) es el vector que representa a la palabra "apple"?
   2. Explicá con tus palabras: si calculáramos el vector para "banana" y el vector para "auto", ¿cuál de los dos debería estar numéricamente más cerca de "apple" y por qué?
   3. Podrías haber usado un encoder tipo word2vec? ¿Y uno no semántico? ¿Qué pierdo en el segundo caso?
   
------------------------------
## Parte 2: El mecanismo de atención (¿A dónde mira la palabra?)
Una palabra puede cambiar totalmente de significado según las palabras que tiene al lado. El Mecanismo de Atención permite que cada palabra "mire" a todas las demás en la oración para calcular su peso o similitud. Así, el modelo decide a qué contexto prestarle atención.

* Ejemplo: en "El banco está cerrado los domingos", la palabra banco mira a cerrado y domingos para saber que es una institución financiera, no un asiento de plaza.

## Ejercicio Práctico 2
Vamos a usar BertViz para ver en tiempo real cómo interactúan las palabras dentro de un modelo. Copiá y ejecutá el siguiente bloque:

from bertviz import head_viewfrom transformers import AutoTokenizer, AutoModelForMaskedLM
# Cargamos un modelo para ver sus capas de atenciónmodel_name = "bert-base-uncased"tokenizer = AutoTokenizer.from_pretrained(model_name)model = AutoModelForMaskedLM.from_pretrained(model_name, output_attentions=True)
# Dos oraciones donde "bank" cambia de significadooracion_1 = "I went to the bank to deposit my money."oracion_2 = "The river bank was muddy and full of frogs."
# Elegí una de las dos oraciones para visualizar cambiando la variable:texto_a_evaluar = oracion_1
inputs = tokenizer(texto_a_evaluar, return_tensors='pt')outputs = model(**inputs)attention = outputs.attentionstokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
# Renderizar la herramienta visual
head_view(attention, tokens)

## Actividad de investigación visual

   1. Probá el código con la oracion_1 y luego con la oracion_2.
   2. Pasá el mouse sobre la palabra "bank" en la interfaz visual de BertViz. Observá las líneas de colores (cabezas de atención).
   3. Respondé: ¿A qué palabras específicas se conecta más fuerte "bank" en la primera oración? ¿Y en la segunda? Justificá cómo esto ayuda al modelo a entender el significado correcto.

------------------------------
## Parte 3: Arquitectura Transformer (Encoder vs. Decoder)
El Transformer original tiene dos partes:

* Encoder (Codificador): Lee un texto completo, mira en todas las direcciones (atención bidireccional) y extrae su significado profundo. Es ideal para clasificar texto o analizar sentimientos.
* Decoder (Decodificador): Genera texto palabra por palabra. Solo tiene permitido mirar hacia el pasado (las palabras que ya escribió), ocultando el futuro. 

## Debate de Arquitectura
Los LLMs modernos más famosos (como la familia GPT) son Decoder-only (solo decodificadores).

   1. ¿Por qué creés que para la tarea de generar una respuesta o continuar una historia es fundamental que el modelo use una arquitectura de tipo Decoder en lugar de un Encoder?

------------------------------
## Parte 4: El proceso de generación y la aleatoriedad
Cuando un modelo genera la siguiente palabra, no elige simplemente "la única correcta". El modelo calcula una lista de probabilidades para miles de palabras posibles.
Para evitar que el modelo sea aburrido o repetitivo, usamos hiperparámetros probabilísticos que manipulan esa lista antes de elegir la palabra final:

* Temperatura: Modifica la confianza. Una temperatura baja (0.1) hace que el modelo sea ultra conservador (elige siempre lo más obvio). Una temperatura alta (1.2) aplana las probabilidades, dando oportunidad a palabras raras (mayor creatividad o locura).
* Top-K: Corta la lista de opciones y se queda únicamente con las $K$ palabras más probables. El resto se descarta por completo.
* Top-P (Nucleus Sampling): Suma las probabilidades de las palabras más altas hasta alcanzar un porcentaje $P$ (por ejemplo, 0.90 o 90%). Solo se elige dentro de ese "núcleo".

## Ejercicio Práctico 3
Ejecutá el script para ver cómo impactan estos parámetros en la salida de un modelo de texto.

from transformers import AutoModelForCausalLM, AutoTokenizerimport torch
# Usamos un modelo liviano de generación (GPT-2)model_gpt = AutoModelForCausalLM.from_pretrained("gpt2")tokenizer_gpt = AutoTokenizer.from_pretrained("gpt2")
prompt = "In a deep and dark forest, the wizard found a"inputs = tokenizer_gpt(prompt, return_tensors="pt")
def generar(temperatura, top_k, top_p):
    torch.manual_seed(42) # Fijamos la semilla para comparar justamente
    outputs = model_gpt.generate(
        **inputs,
        max_new_tokens=20,
        do_sample=True,          # Activa el muestreo estocástico
        temperature=temperatura,
        top_k=top_k,
        top_p=top_p
    )
    return tokenizer_gpt.decode(outputs[0], skip_special_tokens=True)
# Pruebas de configuración
print("--- TEST 1: Conservador (Temperatura Baja) ---")
print(generar(temperatura=0.2, top_k=50, top_p=0.95))

print("\n--- TEST 2: Creativo/Caótico (Temperatura Alta) ---")
print(generar(temperatura=1.5, top_k=50, top_p=0.95))

print("\n--- TEST 3: Restringido (Top-K muy bajo) ---")
print(generar(temperatura=0.8, top_k=2, top_p=0.95))

## Preguntas de Análisis

   1. Compará el TEST 1 y el TEST 2. ¿Qué cambios notás en la coherencia y en la elección de las palabras al subir la temperatura?
   2. ¿Qué peligro corremos si configuramos la temperatura en un valor extremadamente alto (ej. 2.5) sin usar filtros como Top-K o Top-P? Explicalo desde el punto de vista probabilístico.

------------------------------
## Criterios de Entrega

* El trabajo debe entregarse en formato de reporte (PDF) o compartiendo el enlace al cuaderno de Google Colab resuelto.
* Las respuestas teóricas deben ser breves, claras y demostrar que se analizaron los gráficos y los textos generados.

------------------------------

### Link del cuaderno de Google Colab donde se realizo el trabajo:
https://colab.research.google.com/drive/1G9-3Mcg3QVxWTf2kMectwuirl0QhZHJy?usp=sharing
