# pip install langchain langchain-openai

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Configura tu clave de API (asegúrate de tenerla en tus variables de entorno)
# os.environ["OPENAI_API_KEY"] = "tu-clave-api"

# 2. Instancia el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 3. Crea una plantilla de prompt (ChatPromptTemplate)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Sos un asistente útil que responde de manera breve y directa."),
    ("user", "Explicame qué es {tema} en una sola frase.")
])

# 4. Construye la cadena (Chain) uniendo el prompt, el modelo y un analizador de texto
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# 5. Ejecuta la cadena usando .invoke()
respuesta = chain.invoke({"tema": "LangChain"})

print(respuesta)


# ejejmplo de RAG (Retrieval-Augmented Generation) con LangChain y FAISS
# pip install langchain langchain-openai faiss-cpu

import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS

# 1. Configura tu API Key si no la tienes en tus variables de entorno
# os.environ["OPENAI_API_KEY"] = "tu-clave-api"

# 2. Tu base de conocimientos (pueden ser manuales, políticas, contratos, etc.)
documento_privado = """
La materia Introducción a los LLMs y al desarrollo de aplicaciones asociadas fue creada en 2026. 
Su objetivo principal es presentar a los alumnos los conocimientos necesarios para el desarrollo de aplicaciones mediante el uso de inteligencia artificial generativa. 
La materia es cuatrimestral con 4 horas de clases por semana frente a los alumnos y el profesor a cargo es el Dr. Pablo Factorovich.
Este documento es interno de la UNQ.
"""

# 3. Crear Embeddings y la Base de Datos Vectorial en memoria
# Los embeddings convierten el texto en vectores matemáticos que capturan su significado.
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Creamos una base de datos vectorial local (FAISS) usando nuestro texto de ejemplo
vector_store = FAISS.from_texts([documento_privado], embeddings)

# Convertimos la base de datos en un "Recuperador" (Retriever)
retriever = vector_store.as_retriever(search_kwargs={"k": 1})

# 4. Diseñar el Prompt para RAG
# Es fundamental indicarle al modelo que use el contexto proporcionado.
template = """Respondé la pregunta basándote estrictamente en el siguiente contexto:
{contexto}

Pregunta: {pregunta}
Respuesta:"""

prompt = ChatPromptTemplate.from_template(template)

# 5. Instanciar el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 6. Construir la Cadena LCEL Avanzada
# Usamos 'RunnablePassthrough' para que la pregunta del usuario pase directo al prompt
# mientras que el retriever busca el contexto relevante de forma automática.
rag_chain = (
    {"contexto": retriever, "pregunta": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 7. Probar el sistema con una pregunta que GPT no conoce por defecto
pregunta_usuario = "¿Quién dicta \"Introducción a los LLMs y al desarrollo de aplicaciones asociadas\" y cuál es su carga horaria semanal?"
respuesta = rag_chain.invoke(pregunta_usuario)

print(f"Pregunta: {pregunta_usuario}\n")
print(f"Respuesta del Sistema RAG:\n{respuesta}")


#pip install langchain-community

import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory

# 1. Base de datos vectorial (Mismo contexto del ejemplo anterior)
documento_privado = """
La materia Introducción a los LLMs y al desarrollo de aplicaciones asociadas fue creada en 2026. 
Su objetivo principal es presentar a los alumnos los conocimientos necesarios para el desarrollo de aplicaciones mediante el uso de inteligencia artificial generativa. 
La materia es cuatrimestral con 4 horas de clases por semana frente a los alumnos y el profesor a cargo es el Dr. Pablo Factorovich.
Este documento es interno de la UNQ
"""

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_texts([documento_privado], embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 1})

# 2. Instanciar el modelo de lenguaje
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. Inicializar la memoria (Historial del chat)
demo_ephemeral_chat_history = ChatMessageHistory()

# --- PASO 4: Prompt y Cadena para REFORMULAR la pregunta usando el historial ---
# Esto evita que pronombres como "él" o "eso" rompan la búsqueda en la base de datos.
contextualize_q_system_prompt = (
    "Dado un historial de chat y la última pregunta del usuario "
    "que podría hacer referencia al contexto en el historial, "
    "reformulá una pregunta independiente que se pueda entender "
    "sin el historial de chat. NO respondas la pregunta, solo reformulala."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])

# Si no hay historial, pasa la pregunta directo; si hay, la reformula con el LLM
contextualize_q_chain = RunnableBranch(
    (lambda x: not x.get("chat_history"), lambda x: x["input"]),
    contextualize_q_prompt | llm | StrOutputParser()
)

# --- PASO 5: Prompt y Cadena Principal de RAG ---
qa_system_prompt = (
    "Sos un asistente para tareas de respuesta a preguntas. "
    "Usá los siguientes fragmentos de contexto recuperados para responder "
    "la pregunta. Si no sabés la respuesta, decilo.\n\n"
    "Contexto:\n{context}\n\n"
)
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])

# Creamos la cadena final combinando los pasos de manera secuencial
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    RunnablePassthrough.assign(
        # Paso A: Reformulamos la pregunta basándonos en el historial
        rephrased_input=contextualize_q_chain
    )
    | {
        # Paso B: Usamos la pregunta reformulada para buscar en la BD vectorial
        "context": lambda x: retriever | format_docs,
        "chat_history": lambda x: x["chat_history"],
        "input": lambda x: x["rephrased_input"]
    }
    | qa_prompt
    | llm
    | StrOutputParser()
)

# --- PASO 6: Simulación de una conversación continua ---

# Mensaje 1: Pregunta inicial
input_1 = "¿Cuál es el objetivo de la materia Introducción a los LLMs y al desarrollo de aplicaciones asociadas?"
historial = demo_ephemeral_chat_history.messages

print(f"User: {input_1}")
respuesta_1 = rag_chain.invoke({"input": input_1, "chat_history": historial})
print(f"AI: {respuesta_1}\n" + "-"*40)

# Guardamos el turno en la memoria
demo_ephemeral_chat_history.add_user_message(input_1)
demo_ephemeral_chat_history.add_ai_message(respuesta_1)

# Mensaje 2: Pregunta con pronombre y dependencia de contexto ("él", "su")
input_2 = "¿Quién está a cargo de la mismo y cuánta carga semanal tiene?"
historial = demo_ephemeral_chat_history.messages

print(f"User: {input_2}")
respuesta_2 = rag_chain.invoke({"input": input_2, "chat_history": historial})
print(f"AI: {respuesta_2}")






# pip install langgraph langchain-community langchain-openai
# Configurar os.environ["TAVILY_API_KEY"] para la búsqueda web (obtener una clave gratuita en la web de Tavily)

import os
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# 1. Configurar Herramienta 1: Nuestro Recuperador RAG Local
documento_privado = "El código de acceso de emergencia para los servidores de la UNQ es AZ-99X-2026."
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_texts([documento_privado], embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 1})

@tool
def buscar_en_documentos_internos(query: str) -> str:
    """Buscá en los documentos internos de la UNQ sobre la materia Introducción a los LLMs y al desarrollo de aplicaciones asociadas."""
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

# 2. Configurar Herramienta 2: Búsqueda Web (Tavily)
# Asegurate de tener os.environ["TAVILY_API_KEY"] configurado
from langchain_community.tools.tavily_search import TavilySearchResults
buscar_en_internet = TavilySearchResults(max_results=2)

# Agrupamos las herramientas que el agente tendrá a su disposición
tools = [buscar_en_documentos_internos, buscar_en_internet]

# 3. Definir el Estado del Grafo
class AgentState(TypedDict):
    # 'add_messages' hace que los nuevos mensajes se añadan automáticamente al historial existente
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 4. Definir los Nodos del Grafo
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

def chatbot(state: AgentState):
    """Nodo que ejecuta el modelo de lenguaje para decidir el siguiente paso."""
    return {"messages": [model.invoke(state["messages"])]}

# 5. Construir el Grafo de LangGraph
workflow = StateGraph(AgentState)

# Añadimos los nodos: el chatbot y el ejecutor de herramientas prebuilt de LangGraph
workflow.add_node("chatbot", chatbot)
workflow.add_node("action", ToolNode(tools))

# Definimos las conexiones (Aristas/Edges)
workflow.add_edge(START, "chatbot")

# Usamos 'tools_condition' para decidir condicionalmente:
# Si el LLM decidió usar una herramienta -> va al nodo 'action' y luego regresa a 'chatbot'
# Si el LLM decidió que ya tiene la respuesta final -> va al nodo END
workflow.add_conditional_edges(
    "chatbot",
    tools_condition,
    {"tools": "action", END: END}
)
workflow.add_edge("action", "chatbot")

# Inicializamos la memoria nativa de LangGraph para recordar hilos de chat enteros
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# --- 6. Simulación de Conversación con Decisiones Autónomas ---

# Definimos un identificador único para esta sesión de chat
config = {"configurable": {"thread_id": "usuario_123"}}

# Turno 1: Requiere información interna privada
print("--- TURNO 1 ---")
inputs = {"messages": [HumanMessage(content="¿Cuál es el código de emergencia de la UNQ?")]}
for output in app.stream(inputs, config, stream_mode="values"):
    last_message = output["messages"][-1]
print(f"AI: {last_message.content}\n")

# Turno 2: Requiere consultar Internet (Algo que el LLM no sabe por su fecha de corte o datos internos)
print("--- TURNO 2 ---")
inputs = {"messages": [HumanMessage(content="¿Quién ganó el último mundial de fútbol?")]}
for output in app.stream(inputs, config, stream_mode="values"):
    last_message = output["messages"][-1]
print(f"AI: {last_message.content}\n")

# Turno 3: Uso de la memoria implícita en el Grafo
print("--- TURNO 3 ---")
inputs = {"messages": [HumanMessage(content="¿Podés recordarme cuál fue el código que te pedí en mi primera pregunta?")]}
for output in app.stream(inputs, config, stream_mode="values"):
    last_message = output["messages"][-1]
print(f"AI: {last_message.content}")

