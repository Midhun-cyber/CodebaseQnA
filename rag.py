import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_DB_PATH = "vector_store"


@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


@st.cache_resource(show_spinner=False)
def get_vector_store():
    embeddings = get_embeddings()

    return FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def search_repository(question, threshold=1.6):

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(question, k=5)

    relevant_chunks = []

    for doc, score in results:
        if score < threshold:
            relevant_chunks.append(doc)

    return relevant_chunks