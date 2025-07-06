from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from getpass import getpass
from langchain_openai import OpenAIEmbeddings

OPEN_AI_KEY = "MY_OPEN_AI_KEY"


import os 

os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY

embeddings = OpenAIEmbeddings()

directory = "./capstone-design/산학캡스톤/index_store"
vector_index = Chroma(persist_directory=directory, embedding_function=embeddings)

retriever = vector_index.as_retriever(search_type = "similarity",
                                    search_kwargs = {
                                        "k" : 3,
                                    }
                                    )


def generate_response(model, messages, temperature):
    llm = ChatOpenAI(
        temperature=temperature,
        model_name=model,
        openai_api_key=OPEN_AI_KEY
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True)

    llm_response = qa_chain(messages)
    return {"generation_result": llm_response['result'], "source_doc": llm_response['source_documents']}



