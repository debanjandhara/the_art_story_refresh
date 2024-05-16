import os
import pandas as pd
import openai

from IPython.display import display

from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.chains import VectorDBQA
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def first_vectorise():

  Merged_Vector_Path = "./data/merged_vector"

  loader = DirectoryLoader(f'./data/faq', glob=f"./faq.txt", loader_cls=TextLoader, loader_kwargs=dict(encoding="utf-8"))
  loaded_txt = loader.load()
  
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len
  )

  docs = text_splitter.split_documents(loaded_txt)
  embeddings = OpenAIEmbeddings()
  docs_db = FAISS.from_documents(docs, embeddings)
  docs_db.save_local(Merged_Vector_Path)


def add_to_vector(xml_id, type):

  Merged_Vector_Path = "./data/merged_vector"

  loader = DirectoryLoader(f'./data/filtered_txts/{type}s', glob=f"./{xml_id}.txt", loader_cls=TextLoader, loader_kwargs=dict(encoding="utf-8"))
  loaded_txt = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
  docs = text_splitter.split_documents(loaded_txt)
  embeddings = OpenAIEmbeddings()
  VectorStore = FAISS.from_documents(docs, embeddings)

  Merged_VectorStore = FAISS.load_local(Merged_Vector_Path, embeddings, allow_dangerous_deserialization=True)
  Merged_VectorStore.merge_from(VectorStore)
  Merged_VectorStore.save_local(Merged_Vector_Path)
  print("Added to Vector : ",f"./data/filtered_txts/{type}s/{xml_id}.txt")



#--------- refresh_vector() Dependencies -----------

# Display Documents in VectorStore
def show_vstore(store):
 vector_df = store_to_df(store)
 vector_df.to_csv("output.csv", index=False)
 display(vector_df)

# Convert VectorStore into df to convenient access
def store_to_df(store):
 v_dict = store.docstore._dict
 data_rows = []
 for k in v_dict.keys():
   doc_name = v_dict[k].metadata['source'].split('/')[-1]
#    page_number = v_dict[k].metadata['page']+1  # Page used only when it is pdf
   content = v_dict[k].page_content
#    data_rows.append({"chunk_id":k, "document":doc_name, "page":page_number, "content":content})
   data_rows.append({"chunk_id":k, "document":doc_name, "content":content})
 vector_df = pd.DataFrame(data_rows)
 return vector_df

# Deleting a document from a vectorstore
def delete_document(store, document):
  vector_df = store_to_df(store)
  chunks_list = vector_df.loc[vector_df['document']==document]['chunk_id'].tolist()
  print("To be Deleted --> ", document)
  if len(chunks_list) == 0:
    return f"{document} does not exists"
  store.delete(chunks_list)
  print("Successfully Deleted --> ", document)

#-----------------------------------------

def refresh_faq_vector():
  Merged_Vector_Path = "./data/merged_vector"
  embeddings = OpenAIEmbeddings()
  Merged_VectorStore = FAISS.load_local(Merged_Vector_Path, embeddings, allow_dangerous_deserialization=True)
  delete_document(Merged_VectorStore, f"data\\faq\\faq.txt")
  delete_document(Merged_VectorStore, f"faq.txt")
  loader = DirectoryLoader(f'./data/faq', glob=f"./faq.txt", loader_cls=TextLoader, loader_kwargs=dict(encoding="utf-8"))
  loaded_txt = loader.load()
  
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len
  )

  docs = text_splitter.split_documents(loaded_txt)
  embeddings = OpenAIEmbeddings()
  VectorStore = FAISS.from_documents(docs, embeddings)

  Merged_VectorStore = FAISS.load_local(Merged_Vector_Path, embeddings, allow_dangerous_deserialization=True)
  Merged_VectorStore.merge_from(VectorStore)
  Merged_VectorStore.save_local(Merged_Vector_Path)
  print("\n\nRefreshed (Del + Add) FAQ to Vector : ",f"data\\faq\\faq.txt","\n")

  Merged_VectorStore.save_local(Merged_Vector_Path)

def refresh_vector(xml_id, type):
  Merged_Vector_Path = "./data/merged_vector"
  embeddings = OpenAIEmbeddings()
  Merged_VectorStore = FAISS.load_local(Merged_Vector_Path, embeddings, allow_dangerous_deserialization=True)
  delete_document(Merged_VectorStore, f"data\\filtered_txts\\{type}s\\{xml_id}.txt")
  delete_document(Merged_VectorStore, f"{xml_id}.txt")
  print("Deleted from VectorStore : ",f"data\\filtered_txts\\{type}s\\{xml_id}.txt")
  add_to_vector(type, xml_id)
  Merged_VectorStore.save_local(Merged_Vector_Path)
