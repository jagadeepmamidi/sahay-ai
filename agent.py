"""
Sahay AI - Core Agent Module
============================

This module implements the IBM WatsonX-powered RAG agent that answers
user questions about PM-KISAN scheme based on the processed PDF document.

Author: Jagadeep Mamidi
Date: September 2025
"""

import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any

# Environment and configuration
from dotenv import load_dotenv

# IBM WatsonX imports
from ibm_watsonx_orchestrate_adk import agent
from ibm_generative_ai.credentials import Credentials
from ibm_generative_ai.model import GenerativeModel
from ibm_generative_ai.schemas import GenerateParams

# RAG components
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load environment variables from .env file
load_dotenv()


class SahayAIObservability:
    """
    Handles logging and observability for the Sahay AI agent interactions.
    """

    def __init__(self, log_file_path: str = "logs/interactions.jsonl"):
        """
        Initialize the observability system.

        Args:
            log_file_path (str): Path to the JSONL log file
        """
        self.log_file_path = log_file_path
        self._ensure_log_directory_exists()

    def _ensure_log_directory_exists(self):
        """Create the logs directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

    def log_interaction(self, user_query: str, retrieved_context: List[str], 
                       agent_response: str):
        """
        Log a complete agent interaction to JSONL file.

        Args:
            user_query (str): The original user question
            retrieved_context (List[str]): Retrieved document chunks
            agent_response (str): The agent's final response
        """
        try:
            # Create interaction log entry
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_query": user_query,
                "retrieved_context": retrieved_context,
                "agent_response": agent_response
            }

            # Append to JSONL file
            with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        except Exception as e:
            print(f"Warning: Failed to log interaction: {str(e)}")


class SahayRAGEngine:
    """
    Manages the Retrieval-Augmented Generation pipeline for PM-KISAN queries.
    """

    def __init__(self, vector_db_path: str = "data/vector_db"):
        """
        Initialize the RAG engine.

        Args:
            vector_db_path (str): Path to the FAISS vector database
        """
        self.vector_db_path = vector_db_path
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.retrieval_k = 3  # Number of chunks to retrieve

        # Initialize components
        self.embeddings_model = None
        self.vector_database = None
        self.retriever = None

    def initialize_rag_components(self):
        """
        Load the vector database and initialize the retriever.
        """
        try:
            # Load embeddings model
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            # Load the pre-built FAISS vector database
            self.vector_database = FAISS.load_local(
                self.vector_db_path, 
                self.embeddings_model,
                allow_dangerous_deserialization=True  # Required for FAISS loading
            )

            # Create retriever with top-k configuration
            self.retriever = self.vector_database.as_retriever(
                search_kwargs={"k": self.retrieval_k}
            )

            return True

        except Exception as e:
            print(f"Error initializing RAG components: {str(e)}")
            return False

    def retrieve_relevant_context(self, user_query: str) -> List[str]:
        """
        Retrieve relevant document chunks based on user query.

        Args:
            user_query (str): The user's question

        Returns:
            List[str]: List of relevant text chunks
        """
        try:
            if not self.retriever:
                self.initialize_rag_components()

            # Retrieve relevant documents
            retrieved_docs = self.retriever.invoke(user_query)

            # Extract text content from retrieved documents
            context_chunks = [doc.page_content for doc in retrieved_docs]

            return context_chunks

        except Exception as e:
            print(f"Error during retrieval: {str(e)}")
            return []


class SahayWatsonXLLM:
    """
    Manages the IBM WatsonX Granite model for generating responses.
    """

    def __init__(self):
        """Initialize the WatsonX LLM with credentials from environment."""
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.model_id = "ibm/granite-13b-chat-v2"

        # Initialize credentials and model
        self.credentials = None
        self.generative_model = None
        self._setup_watsonx_model()

    def _setup_watsonx_model(self):
        """Setup WatsonX credentials and model."""
        try:
            if not self.api_key or not self.project_id:
                raise ValueError("WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env file")

            # Setup credentials
            self.credentials = Credentials(
                api_key=self.api_key,
                api_endpoint="https://us-south.ml.cloud.ibm.com"
            )

            # Initialize the generative model
            self.generative_model = GenerativeModel(
                model_id=self.model_id,
                credentials=self.credentials,
                project_id=self.project_id
            )

        except Exception as e:
            print(f"Error setting up WatsonX model: {str(e)}")
            raise

    def generate_response(self, user_query: str, context_chunks: List[str]) -> str:
        """
        Generate a response using WatsonX Granite model.

        Args:
            user_query (str): The user's question
            context_chunks (List[str]): Retrieved context from RAG

        Returns:
            str: Generated response from the model
        """
        try:
            # Construct the context from retrieved chunks
            context_text = "\n\n".join(context_chunks)

            # Create the system prompt for Sahay AI
            system_prompt = """You are Sahay AI, a helpful assistant specialized in answering questions about the Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme.

INSTRUCTIONS:
- Answer the user's question based ONLY on the provided context from the official PM-KISAN rules document.
- If the information is not available in the context, respond with: "I'm sorry, the official rules document does not provide information on that topic."
- Keep your answers simple, clear, and in plain language that farmers can easily understand.
- Be accurate and cite specific details from the document when available.
- Be helpful and empathetic in your tone.

CONTEXT FROM PM-KISAN OFFICIAL DOCUMENT:
{context}

USER QUESTION: {question}

SAHAY AI RESPONSE:"""

            # Format the complete prompt
            complete_prompt = system_prompt.format(
                context=context_text,
                question=user_query
            )

            # Configure generation parameters
            generate_params = GenerateParams(
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )

            # Generate response
            response = self.generative_model.generate(
                prompt=complete_prompt,
                params=generate_params
            )

            # Extract the generated text
            generated_text = response.results[0].generated_text.strip()

            return generated_text

        except Exception as e:
            error_message = f"I apologize, but I encountered an error while processing your question: {str(e)}"
            return error_message


# Initialize global components
observability_logger = SahayAIObservability()
rag_engine = SahayRAGEngine()
watsonx_llm = SahayWatsonXLLM()


@agent(
    name="sahay_ai_rag_agent",
    description="Sahay AI agent that helps users understand PM-KISAN scheme benefits and procedures using RAG-powered responses from official government documents."
)
def ask_sahay_ai(user_query: str) -> str:
    """
    Main agent function that orchestrates the complete RAG pipeline.

    This function:
    1. Retrieves relevant context from the vector database
    2. Generates a response using IBM WatsonX Granite model
    3. Logs the interaction for observability

    Args:
        user_query (str): The user's question about PM-KISAN scheme

    Returns:
        str: AI-generated response based on official PM-KISAN documents
    """
    try:
        # Initialize RAG components if needed
        if not rag_engine.retriever:
            initialization_success = rag_engine.initialize_rag_components()
            if not initialization_success:
                return "I'm sorry, there was an issue accessing the PM-KISAN knowledge base. Please try again later."

        # Step 1: Retrieve relevant context using RAG
        retrieved_context = rag_engine.retrieve_relevant_context(user_query)

        if not retrieved_context:
            return "I'm sorry, I couldn't find relevant information in the PM-KISAN documents to answer your question."

        # Step 2: Generate response using WatsonX
        ai_response = watsonx_llm.generate_response(user_query, retrieved_context)

        # Step 3: Log the interaction for observability
        observability_logger.log_interaction(
            user_query=user_query,
            retrieved_context=retrieved_context,
            agent_response=ai_response
        )

        return ai_response

    except Exception as e:
        error_response = f"I apologize, but I encountered an unexpected error: {str(e)}. Please try rephrasing your question."

        # Still log the failed interaction
        observability_logger.log_interaction(
            user_query=user_query,
            retrieved_context=[],
            agent_response=error_response
        )

        return error_response


# Utility function for testing the agent locally
def test_agent_locally():
    """Test function for local development and debugging."""
    test_queries = [
        "What is PM-KISAN scheme?",
        "Who is eligible for PM-KISAN benefits?",
        "How much money do farmers receive under PM-KISAN?",
        "What documents are needed for PM-KISAN application?"
    ]

    print("🧪 Testing Sahay AI Agent Locally")
    print("=" * 40)

    for query in test_queries:
        print(f"\n❓ Question: {query}")
        response = ask_sahay_ai(query)
        print(f"🤖 Sahay AI: {response}")
        print("-" * 40)


if __name__ == "__main__":
    test_agent_locally()
