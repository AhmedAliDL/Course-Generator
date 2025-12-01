import logging
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from model import llm


class QuesAns:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Function to split text into chunks
    def get_text_chunks(self, text):
        """this function segment text of explanation to group of chunks
        ,each chunk with specific chunk_size using len method."""
        try:
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=500,
                chunk_overlap=0,
                length_function=len
            )
            chunks = text_splitter.split_text(text)
            return chunks

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # Function to create a vector store from text chunks using Hugging Face embeddings and FAISS
    def get_vectorstore(self, text_chunks):
        """this function to get embeddings of text using llm(hku) then
         make vectorstore(that`s save embeddings of text with
        its text`s chunk) using FAISS."""
        try:
            embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
            vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
            return vectorstore

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # Function to create a conversation chain using OpenAI Chat API
    def get_conversation_chain(self, vectorstore):
        """this function keep conversion between user and llm
        (question from user and answer from llm) and make
        its retriever is a vectorstore (not the llm database)
        and keep this chat appear to him , by using BufferMemory
         in langchain.
        """
        try:
            memory = ConversationBufferMemory(
                memory_key='chat_history', return_messages=True)
            conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                memory=memory
            )
            return conversation_chain

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None
