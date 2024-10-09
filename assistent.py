from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
import json
from tools_ecomart import *

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = 'gpt-4o'

contexto = carrega("dados/ecomart.txt")


def create_thread(vector_store):
    return client.beta.threads.create(
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )


def create_vector_store():
    vector_store = client.beta.vector_stores.create(name='Ecomart Vector Store')

    file_paths = [
        'dados/dados_ecomart.txt',
        'dados/políticas_ecomart.txt',
        'dados/produtos_ecomart.txt'
    ]
    file_streams = [open(path, 'rb') for path in file_paths]

    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    return vector_store


def create_assistant(vector_store):
    assistant = client.beta.assistants.create(
        name='Ecomart Assistant',
        instructions=f'''
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            Além disso, acesse os arquivos associados a você e a thread para responder as perguntas.
        ''',
        model=model,
        tools=minhas_tools,
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )
    return assistant

def get_json():
    filename = 'assistentes.json'

    if not os.path.exists(filename):
        vector_store = create_vector_store()
        thread = create_thread(vector_store)
        assistant = create_assistant(vector_store)

        data = {
            'assistant_id': assistant.id,
            'vector_store_id': vector_store.id,
            'thread_id': thread.id
        }

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print('Arquivo "assistentes.json" criado com sucesso.')

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('Arquivo "assistentes.json" não encontrado.')