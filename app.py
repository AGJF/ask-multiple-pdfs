import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from openai import RateLimitError, AuthenticationError
# Imported to catch specific OpenAI API failures (quota exceeded,
# bad key) so we can show a helpful message instead of an unhandled
# exception crashing the Streamlit app.
from docx import Document
# to read text from .docx file


def get_document_text(uploaded_files):
    # RAG STAGE: LOAD
    # Loops through all uploaded files (which may be a mix of PDF, DOCX,
    # TXT, and MD), identifies each file's type by its extension, and
    # routes it to the matching extractor function. Unsupported file
    # types are skipped (with a warning naming the file) rather than
    # aborting the whole batch, so the rest of the upload still gets
    # processed. Returns all extracted text concatenated together.
    text = ""
    extractors = {
        "pdf": get_pdf_text,
        "docx": get_docx_text,
        "txt": get_txt_text,
        "md": get_md_text
    }
    for file in uploaded_files:
        file_type = identify_file_type(file.name)
        if file_type not in extractors:
            st.warning(f"'{file.name}' is not processed due to not supported file type. Kindly upload a pdf, docx, txt or md")
            continue
        text += extractors[file_type](file)
    return text

def identify_file_type(filename):
    root, ext = os.path.splitext(filename)
    return ext.removeprefix(".")

def get_txt_text(file):
    # get the raw data from file 
    # without moving the file pointer with .getvalue()
    # decode the raw data into readable text with .decode()
    text = file.getvalue().decode("utf-8")
    return text

def get_md_text(file):
    # get the raw data from file 
    # without moving the file pointer with .getvalue()
    # decode the raw data into readable text with .decode()
    # although get_txt_text and get_md_text is identical but separate 
    # into 2 function for future development
    text = file.getvalue().decode("utf-8")
    return text

def get_docx_text(file):
    # import Document from docx and read text into a list
    # join list with "\n" because RecursiveCharacterTextSplitter split text
    # based on "\n", "\n\n" and " "
    # limitation: if file has table, the table wont be captured by doc.paragraphs
    doc = Document(file)
    text = [para.text for para in doc.paragraphs]
    return "\n".join(text)

def get_pdf_text(file):
    # for each page of pdf file extract the text and concatenate the text
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    # RAG STAGE: CHUNK
    # Splits the raw text into overlapping chunks so each piece is small
    # enough to embed meaningfully, while overlap preserves context that
    # would otherwise be lost at chunk boundaries.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    # RAG STAGE: EMBED + STORE
    # Converts each chunk into a vector embedding and stores them in a
    # FAISS index for fast similarity search later. Uses OpenAI's
    # embedding model — must match the model used at query time.
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    # Alternative: swap in a local/open-source embedding model instead of
    # OpenAI's, to avoid API costs (not currently used).
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    # RAG STAGE: RETRIEVE + GENERATE
    # Wires the vectorstore up as a retriever and hands it to an LLM chain.
    # ConversationBufferMemory keeps prior turns so follow-up questions
    # have context from earlier in the chat.
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})
    # Alternative: swap in a free-tier HuggingFace-hosted LLM instead of
    # OpenAI's ChatGPT model (not currently used).
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    # RAG STAGE: RETRIEVE/GENERATE + UI
    # Guard clause: don't attempt a query if no documents have been
    # processed into a conversation chain yet.
    if st.session_state.conversation is None:
        st.warning("Document Yet to Process, Process The Attached Document First.")
        return
    
    # Runs the RetrievalQA chain (retrieve relevant chunks, then generate
    # an answer) and updates the chat history in session state.
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    # Chat history alternates user/bot messages, so even indices are the
    # user's turns and odd indices are the bot's replies.
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    
    # Guard clause: fail fast with a clear message if no API key is set,
    # rather than letting a cryptic OpenAI auth error surface later.
    if not os.getenv("OPENAI_API_KEY"):
        st.error("No API KEY! Kindly Head to OpenAI Wbsite to Get an API For The Application to Work.")
        return
    st.write(css, unsafe_allow_html=True)

    # Session state persists the conversation chain and chat history
    # across Streamlit reruns (Streamlit reruns the whole script on
    # every interaction, so this is how state survives).
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        # accepting 4 types of file
        document_docs = st.file_uploader(
            "Upload your files here (Supported file types: .pdf, .docx, .md, .txt) and click on 'Process'", 
            accept_multiple_files=True,
            type = ["pdf", "docx", "md", "txt"]
            )
        if st.button("Process"):
            # Guard clause: nothing to process if the user hasn't
            # uploaded any files.
            if not document_docs:
                st.warning("No PDF Files Uploaded, Unable To Process Any Data")
                return
            with st.spinner("Processing"):
                # Full pipeline: LOAD -> CHUNK -> EMBED/STORE -> build
                # the retrieval+generation chain, in that order.
                raw_text = get_document_text(document_docs)
                text_chunks = get_text_chunks(raw_text)
                try:
                    vectorstore = get_vectorstore(text_chunks)
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                except RateLimitError:
                    # Catches OpenAI quota/billing errors during embedding or chat
                    # completion calls, so the user gets an actionable message
                    # instead of the app crashing.
                    st.session_state.conversation = None
                    st.warning("API Credit Not Enough, Go Top Up Your Credit")
                    return
                except AuthenticationError:
                    # Catches invalid/expired API keys at the point they're actually
                    # used (embedding + LLM calls), which is more reliable than only
                    # checking os.getenv at startup — a key can look "present" but
                    # still be invalid.
                    st.session_state.conversation = None
                    st.warning("Invalid API Key, Please Check Your API Key")
                    return



if __name__ == '__main__':
    main()
