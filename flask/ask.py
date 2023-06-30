from flask import Flask, render_template, request
import os
import openai
import pdfplumber

app = Flask(__name__)

# Initialize OpenAI API client
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Chat history list
chat_history = []

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

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    query_text = request.form["query_text"]

    uploaded_file = request.files["document"]
    document_text = ""

    file_extension = uploaded_file.filename.split(".")[-1]
    if file_extension == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                document_text += page.extract_text()
    elif file_extension in ["doc", "docx", "txt"]:
        document_text = uploaded_file.read().decode()

    if document_text:
        response = generate_full_response(document_text, query_text)
        chat_history.append((query_text, response))

    return {"query_text": query_text, "response": response}

if __name__ == "__main__":
    app.run(debug=True)
