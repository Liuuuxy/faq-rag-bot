import os
import json
import re
import logging
from psycopg2 import pool
from dotenv import load_dotenv
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv(".env.local")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY is not set or invalid. Exiting.")
    exit(1)

genai.configure(api_key=api_key)

embed_model = "models/text-embedding-004"

# Get the connection string from the environment variable
connection_string = os.getenv("DATABASE_URL")
if not connection_string:
    logging.error(
        "Database connection string is missing. Please set DATABASE_URL in your environment."
    )
    exit(1)

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections in the pool
    10,  # Maximum number of connections in the pool
    connection_string,
)


def preprocess_text(text: str) -> str:
    """
    Preprocesses the input text by lowercasing and removing punctuation.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text.strip()


def generate_embeddings(text):
    """
    Generates embeddings for text using OpenAI's embedding model.
    """
    try:
        result = genai.embed_content(
            model=embed_model, content=text, output_dimensionality=768
        )
        # breakpoint()
        return result["embedding"]
    except Exception as e:
        logging.error(f"Failed to generate embeddings: {e}")
        return []


def insert_into_db(faq_data):
    """
    Inserts FAQ data into the PostgreSQL database, including embeddings.
    """
    try:
        connection = connection_pool.getconn()
        cursor = connection.cursor()

        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS faq_entries (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT NOT NULL,
                embedding vector(768) NOT NULL
            );
            """
        )

        for collection in faq_data.get("collections", []):
            collection_title = collection.get("collection_title", "General")
            for faq in collection.get("articles", []):
                question = faq.get("question", "").strip()
                answer = faq.get("answer", "").strip()

                if not question or not answer:
                    continue

                cursor.execute(
                    """
                    SELECT id FROM faq_entries WHERE question = %s;
                    """,
                    (question,),
                )
                if cursor.fetchone():
                    logging.info(f"Skipping existing question: {question}")
                    continue

                preprocessed_question = preprocess_text(question)

                embedding = generate_embeddings(preprocessed_question)
                if not embedding:
                    logging.warning(
                        f"Failed to generate embedding for question: {question}"
                    )
                    continue

                # Insert into the database
                cursor.execute(
                    """
                    INSERT INTO faq_entries (question, answer, category, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        question,
                        answer,
                        collection_title,
                        embedding,
                    ),
                )

        connection.commit()
        print("Data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            connection_pool.putconn(connection)


if __name__ == "__main__":
    # Load FAQ data from JSON file
    faq_file_path = "faq_data.json"
    with open(faq_file_path, "r") as f:
        faq_data = json.load(f)

    insert_into_db(faq_data)

    print("FAQ data has been preprocessed and inserted into the database.")
