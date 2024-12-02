import os
import json
import logging
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from pymongo import MongoClient
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

# Load environment variables
load_dotenv(".env")


def parse_json_to_documents(json_data):
    """
    Convert JSON data into Langchain Documents
    """
    documents = []

    if "collections" in json_data:
        for collection in json_data["collections"]:
            for article in collection.get("articles", []):
                # Combine all text fields
                content = (
                    f"{article.get('question', '')}\n {article.get('answer', '')}\n"
                )

                # Create a Document
                doc = Document(
                    page_content=content,
                    metadata={"source": article.get("url", "unknown")},
                )
                documents.append(doc)

    return documents


def initialize_vector_store(
    faq_file: str,
    connection_string: str,
):
    """
    Initialize the vector store with FAQ data if not already populated.
    """
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        if not os.path.exists(faq_file):
            raise FileNotFoundError(f"FAQ file not found: {faq_file}")

        with open(faq_file, "r", encoding="utf-8") as f:
            faq_data = json.load(f)

        documents = parse_json_to_documents(faq_data)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=150
        )
        docs = text_splitter.split_documents(documents)

        client = MongoClient(connection_string)

        DB_NAME = "langchain_faq_db"
        COLLECTION_NAME = "langchain_faq_vectorstores"
        ATLAS_VECTOR_SEARCH_INDEX_NAME = "langchain-faq-index-vectorstores"

        MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

        vector_store = MongoDBAtlasVectorSearch.from_documents(
            documents=docs,
            collection=MONGODB_COLLECTION,
            embedding=embeddings,
            index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
            relevance_score_fn="cosine",
        )
        vector_store.create_vector_search_index(dimensions=768)
        logging.info(f"Vector store initialized with {len(docs)} documents.")

    except Exception as e:
        logging.error(f"Error during vector store initialization: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    faq_file = "faq_data.json"
    connection_string = os.getenv("MONGODB_ATLAS_CLUSTER_URI")

    if not connection_string:
        raise ValueError("DATABASE_URL environment variable is not set.")

    initialize_vector_store(faq_file, connection_string)
