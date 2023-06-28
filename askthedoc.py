import streamlit as st
import pytesseract
import pdfplumber
from docx import Document
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

def generate_response(uploaded_file, openai_api_key, query_text):
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension == "txt":
            documents = [uploaded_file.read().decode()]
        elif file_extension == "pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                documents = [page.extract_text() for page in pdf.pages]
        elif file_extension in ["doc", "docx"]:
            doc = Document(uploaded_file)
            documents = [paragraph.text for paragraph in doc.paragraphs]
        else:
            st.error("Unsupported file format. Please upload a PDF, DOC, DOCX, or TXT file.")
            return

        # Split documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.create_documents(documents)
        
        # Select embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # Create a vectorstore from documents
        db = Chroma.from_documents(texts, embeddings)
        
        # Create retriever interface
        retriever = db.as_retriever()
        
        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key=openai_api_key), chain_type='stuff', retriever=retriever)
        
        return qa.run(query_text, n_results=4)[:1]  # Limit to 1 result

# Page title
st.set_page_config(page_title='🦜🔗 Ask the Doc App')
st.title('🦜🔗 Ask the Doc App')

# File upload
uploaded_file = st.file_uploader('Upload an article', type=['pdf', 'doc', 'docx', 'txt'])
# Query text
query_text = st.text_input('Enter your question:', placeholder='Please provide a short summary.', disabled=uploaded_file is None)

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    openai_api_key = st.text_input('OpenAI API Key', type='password', disabled=uploaded_file is None)
    submitted = st.form_submit_button('Submit', disabled=uploaded_file is None)
    if submitted and openai_api_key.startswith('sk-'):
        with st.spinner('Calculating...'):
            response = generate_response(uploaded_file, openai_api_key, query_text)
            if response:
                result.append(response[0])

if len(result):
    st.info(result[0])
