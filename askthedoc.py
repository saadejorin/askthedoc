import streamlit as st
import os
import openai
import pdfplumber

# Initialize OpenAI API client
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Function to split the document into smaller chunks
def split_document(document_text, chunk_size=4096):
    chunks = []
    num_chunks = (len(document_text) - 1) // chunk_size + 1
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk = document_text[start_idx:end_idx]
        chunks.append(chunk)
    return chunks

# Function to generate response for a single chunk
def generate_response(chunk, query_text):
    prompt = f"Document:\n{chunk}\n\nQuestion: {query_text}\nAnswer:"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
    return response.choices[0].text.strip()

# Function to generate response for the entire document
def generate_full_response(document_text, query_text):
    chunks = split_document(document_text)
    responses = []
    for chunk in chunks:
        response = generate_response(chunk, query_text)
        responses.append(response)
    return " ".join(responses)

# Page title
st.set_page_config(page_title='🦜🔗 Ask the Doc App')
st.title('🦜🔗 Ask the Doc App')

# File upload
uploaded_file = st.file_uploader('Upload a document', type=['pdf', 'doc', 'docx', 'txt'])

# Query text
query_text = st.text_input('Enter your question:', placeholder='Please provide a short summary.')

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    submitted = st.form_submit_button('Submit')
    if submitted and uploaded_file is not None and query_text:
        document_text = ""
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension == "pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    document_text += page.extract_text()
        elif file_extension in ["doc", "docx", "txt"]:
            document_text = uploaded_file.read().decode()
        else:
            st.error('Unsupported file format. Please upload a PDF, DOC, DOCX, or TXT file.')
        if document_text:
            with st.spinner('Processing...'):
                response = generate_full_response(document_text, query_text)
                result.append(response)

if len(result) > 0:
    st.info(result[0])
