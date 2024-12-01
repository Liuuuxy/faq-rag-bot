import os
import json
import logging
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Langchain Imports
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

# Load environment variables
load_dotenv(".env")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class InteractionLog(BaseModel):
    user_query: str
    response: str
    matched_question: Optional[str] = None
    helpful: Optional[bool] = None


class ChatService:
    def __init__(self, faq_file: str = "faq_data.json"):
        # Configure Google API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logging.error("GOOGLE_API_KEY is not set.")
            raise ValueError("GOOGLE_API_KEY is required")

        # Langchain configurations
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004"
        )

        system_prompt = (
            """
                You are an AI assistant designed to answer questions based on specific context provided from the Highrise FAQ. Your role is to help users by giving clear, friendly, and concise answers using only the retrieved context provided to you. Follow these rules strictly:

                1. Answer Based Only on the Provided Context:
                - If a specific answer to the question is in the context, use that information directly.
                - If the context provides multiple possible answers, prompt the user for clarification by listing the available options.
                - If no relevant information is available, say: "I'm not sure about that, but you can find more information at the Highrise FAQ: https://support.highrise.game/en/".

                2. Be Concise and Friendly:
                - Always end the response with a friendly phrase, such as "Let me know if you need more help!".

                3. Ask for Clarification if Needed:
                - If the user's question is unclear, respond with: "Could you please clarify what you mean? I can assist with topics related to " and also list the available options.
                """
            "\n\n"
            "{context}"
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        # Chat history tracking
        self.sessions: Dict[str, List[tuple]] = {}
        vector_store = self.get_vector_store(faq_file)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 6}
        )

        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    def parse_json_to_documents(self, json_data):
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

    def get_vector_store(self, file_path: str):
        """
        Load JSON, create embeddings, and set up retrieval chain
        """
        try:
            if not os.path.exists(file_path):
                logging.error(f"FAQ file not found: {file_path}")
                return None

            # Load JSON file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except json.JSONDecodeError as json_err:
                logging.error(f"JSON parsing error: {json_err}")
                return None

            # Convert JSON to documents
            documents = self.parse_json_to_documents(json_data)

            print(f"Parsed {len(documents)} documents from {file_path}")

            if not documents:
                print("No documents were parsed from the JSON file")
                return None

            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=150
            )
            docs = text_splitter.split_documents(documents)
            print((f"Split {len(docs)} documents."))

            vector_store = Chroma.from_documents(
                documents=docs, embedding=self.embeddings
            )
            return vector_store

        except Exception as e:
            logging.error(f"Error loading database: {e}")
            return None

    def generate_response(self, message: str) -> Dict[str, Any]:
        """
        Generate a contextual response using Langchain's conversational chain
        """
        chain = self.rag_chain.pick("answer")
        for chunk in chain.stream({"input": message}):
            yield chunk
        # print(result)
        # response = {
        #     "role": "assistant",
        #     "content": result["answer"],
        # }

        # return response

    def log_interaction(
        self,
        user_query: str,
        response: Any,
        helpful: Optional[bool] = None,
    ):
        """
        Log interaction details to a file
        """
        if not isinstance(response, str):
            # Convert response to string if it is a dictionary or other type
            response = json.dumps(response)

        log_entry = InteractionLog(
            user_query=user_query,
            response=response,
            helpful=helpful,
        )

        try:
            with open("interaction_logs.json", "a") as log_file:
                log_file.write(log_entry.model_dump_json() + "\n")
        except IOError as e:
            logging.error(f"Failed to log interaction: {e}")


# FastAPI App Setup
app = FastAPI()
chat_service = ChatService()


@app.post("/api/chat")
async def handle_chat(request: ChatRequest):
    """
    Handle chat requests with contextual response generation
    """
    try:
        messages = request.messages
        # Generate contextual response
        response = StreamingResponse(
            chat_service.generate_response(messages[-1].content)
        )
        response.headers["x-vercel-ai-data-stream"] = "v1"
        print(response)
        # Log interaction
        # chat_service.log_interaction(user_query=messages[-1].content, response=response)
        # print("json", JSONResponse(content=response))
        # return JSONResponse(content=response)
        return response

    except Exception as e:
        logging.error(f"Chat processing error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# Uncomment for local testing if needed
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
