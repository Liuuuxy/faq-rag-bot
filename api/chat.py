import os
import json
import logging
from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Langchain Imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from typing_extensions import List

# Load environment variables
load_dotenv(".env")

LOG_FILE_PATH = "/tmp/interactions.log"


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
    def __init__(self):
        # Configure Google API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logging.error("GOOGLE_API_KEY is not set.")
            raise ValueError("GOOGLE_API_KEY is required")

        self.connection_string = os.getenv("MONGODB_ATLAS_CLUSTER_URI")

        # Langchain configurations
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004"
        )

        DB_NAME = "langchain_faq_db"
        COLLECTION_NAME = "langchain_faq_vectorstores"
        ATLAS_VECTOR_SEARCH_INDEX_NAME = "langchain-faq-index-vectorstores"

        self.vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=self.connection_string,
            namespace=DB_NAME + "." + COLLECTION_NAME,
            embedding=self.embeddings,
            index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
        )
        self.setup_retrieval_chain()

    def setup_retrieval_chain(self):
        """
        Set up the retrieval chain for querying the vector store.
        """
        retriever = self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 6}
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
        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    def generate_response(self, message: str, background_tasks: BackgroundTasks):
        """
        Generate a contextual response using Langchain's conversational chain
        """
        chunks = []
        print(self.rag_chain.invoke({"input": message}))
        chain = self.rag_chain.pick("answer")
        for chunk in chain.stream({"input": message}):
            chunks.append(chunk)
            yield chunk
        background_tasks.add_task(self.log_interaction, message, chunks)

    def log_interaction(self, user_query, chunks: List[str]):
        response = "".join(chunks)

        solved = "I'm not sure about that" not in response

        interaction = {"user_query": user_query, "response": response, "solved": solved}

        try:
            if os.path.exists(LOG_FILE_PATH):
                with open(LOG_FILE_PATH, "r+") as f:
                    data = json.load(f)
                    data.append(interaction)
                    f.seek(0)
                    json.dump(data, f, indent=4)
            else:
                with open(LOG_FILE_PATH, "w") as f:
                    json.dump([interaction], f, indent=4)

        except Exception as e:
            logging.error(f"Error logging interaction: {e}")


# FastAPI App Setup
app = FastAPI()
chat_service = ChatService()


@app.post("/api/chat")
async def handle_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Handle chat requests with contextual response generation
    """
    try:
        messages = request.messages
        user_query = messages[-1].content
        logging.info(f"User query: {user_query}")

        streaming_response = StreamingResponse(
            chat_service.generate_response(user_query, background_tasks)
        )
        streaming_response.headers["x-vercel-ai-data-stream"] = "v1"

        return streaming_response

    except Exception as e:
        logging.error(f"Chat processing error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/logs")
def get_logs():
    if os.path.exists(LOG_FILE_PATH):
        return FileResponse(
            LOG_FILE_PATH, media_type="text/plain", filename="interactions.log"
        )
    else:
        return {"error": "Log file not found"}


# Uncomment for local testing
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
