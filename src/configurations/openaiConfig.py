
import openai
import os
import time

from src.configurations.logging import logging

class OpenAiConfig():

    def __init__(self):
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def generate_response(self, messages, model):
        for i in range(5):
            try:
                response = openai.ChatCompletion.create(model = model, messages = messages,  max_tokens = 600, temperature = 0)
                return response["choices"][0]["message"]["content"], response['usage']['prompt_tokens'], response['usage']['completion_tokens'], model
            except Exception as e:
                logging.exception("Exception occurred")  
                time.sleep(2)
                continue
        return False



#examples puller
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def find_txt_examples(query, k=5):
    # QUERY = INBOUND MESSAGE

    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Construct the path to the .txt file
    txt_file_path = os.path.join(dir_path, 'sops.txt')
    loader = TextLoader(txt_file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50, length_function = len, is_separator_regex = False)
    docs = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    db = FAISS.from_documents(docs, embeddings)
    docs = db.similarity_search(query, k=k)

    examples = ""

    for index, doc in enumerate(docs):
       examples += f'\n\nSNIPPET {index+1}:\n' + doc.page_content
    return examples

