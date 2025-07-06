# -*- coding: utf-8 -*-

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

import jpype
import asposecells
import os

jpype.startJVM()

from asposecells.api import Workbook

os.environ["OPENAI_API_KEY"] = "MY_OPEN_AI_KEY"
	# Open_AI API키
    
    
file_list = [file for file in os.listdir() if file.endswith('.json')]
    # ".json" 확장자를 갖는 파일의 파일명을 file_list에 불러온다.

for file_name in file_list:	
	# 해당 for문은 모든 파일명에 대해 DB에 반영한다.
    print(file_name + "을 DB에 반영하고 있습니다..")
    
    workbook = Workbook(file_name)
    workbook.save(file_name + ".pdf")

jpype.shutdownJVM()

file_list = [file for file in os.listdir() if file.endswith('.pdf')]
	# ".pdf" 확장자를 갖는 파일의 파일명을 file_list에 불러온다.

for file_name in file_list:	
	# 해당 for문은 모든 파일명에 대해 DB에 반영한다.
    print(file_name + "을 DB에 반영하고 있습니다..")
    
    loader = PyPDFLoader(file_name)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200
        )
    pages = loader.load_and_split(text_splitter)
    
    directory = 'index_store'
    vector_index = Chroma.from_documents(
        pages,
        OpenAIEmbeddings(),
        persist_directory = directory
        )
    vector_index.persist()
    
    retriever = vector_index.as_retriever(
        search_type = "similarity",
        search_kwargs = {
            "k" : 3,
            }
        )
    
file_list = [file for file in os.listdir() if file.endswith('.json')]
    # ".json" 확장자를 갖는 파일의 파일명을 file_list에 불러온다.

print(retriever.get_relevant_documents("딸기에 들 수 있는 병충해"))
