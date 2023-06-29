import streamlit as st
import os
import openai
import pdfplumber

# Initialize OpenAI API client
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Function to generate response using OpenAI GPT-4
def generate_response(document_text, query_text):
    prompt = f"Document:\n{document_text}\n\nQuestion: {query_text}\nAnswer:"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
    return response.choices[0].text.strip()

# Page title
st.set_page_config(page_title='🦜🔗 Ask the Doc App')
st.title('🦜🔗 Ask the Doc App')

# File upload
uploaded_file = st.file_uploader('Upload an article', type=['pdf', 'doc', 'docx', 'txt'])
# Query text
query_text = st.text_input('Enter your question:', placeholder='Please provide a short summary.', key='query_text', disabled=uploaded_file is None)

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    submitted = st.form_submit_button('Submit', disabled=uploaded_file is None)
    if submitted:
        with st.spinner('Calculating...'):
            if uploaded_file is not None:
                file_extension = uploaded_file.name.split(".")[-1]
                if file_extension == "txt":
                    document_text = uploaded_file.read().decode()
                elif file_extension == "pdf":
                    document_text = " ".join([page.extract_text() for page in pdfplumber.open(uploaded_file).pages])
                elif file_extension in ["doc", "docx"]:
                    document = Document(uploaded_file)
                    document_text = " ".join([paragraph.text for paragraph in document.paragraphs])
                else:
                    st.error("Unsupported file format. Please upload a PDF, DOC, DOCX, or TXT file.")
                    st.stop()
            else:
                st.error("Please upload a file.")
                st.stop()

            response = generate_response(document_text, query_text)
            result.append(response)

if len(result):
    st.info(result[0])
