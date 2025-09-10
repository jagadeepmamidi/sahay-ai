"""
Sahay AI - Data Ingestion Pipeline
==================================

This script processes the PM-KISAN PDF document and creates a vector database
for the RAG (Retrieval-Augmented Generation) system.

Author: Jagadeep Mamidi
Date: September 2025
"""

import os
import sys
from pathlib import Path

# Third-party imports for document processing and vector storage
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


class SahayDataPipeline:
    """
    A comprehensive data pipeline for processing PM-KISAN PDF documents
    and creating a searchable vector database.
    """

    def __init__(self, pdf_path: str = "data/pm_kisan_rules.pdf", 
                 vector_db_path: str = "data/vector_db"):
        """
        Initialize the data pipeline with file paths.

        Args:
            pdf_path (str): Path to the PM-KISAN PDF document
            vector_db_path (str): Path where vector database will be saved
        """
        self.pdf_path = pdf_path
        self.vector_db_path = vector_db_path
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"

        # Text chunking parameters for optimal retrieval
        self.chunk_size = 1000
        self.chunk_overlap = 150

    def validate_pdf_exists(self) -> bool:
        """
        Check if the source PDF file exists.

        Returns:
            bool: True if PDF exists, False otherwise
        """
        if not os.path.exists(self.pdf_path):
            print(f"❌ Error: PDF file not found at {self.pdf_path}")
            print("Please ensure the PM-KISAN PDF is placed in the data/ directory.")
            return False
        return True

    def load_pdf_document(self):
        """
        Load the PDF document using PyPDFLoader.

        Returns:
            list: List of loaded document pages
        """
        print("📄 Loading PDF document...")
        try:
            pdf_loader = PyPDFLoader(self.pdf_path)
            documents = pdf_loader.load()
            print(f"✅ Successfully loaded {len(documents)} pages from PDF")
            return documents
        except Exception as e:
            print(f"❌ Error loading PDF: {str(e)}")
            raise

    def split_text_into_chunks(self, documents):
        """
        Split the loaded documents into smaller, manageable chunks.

        Args:
            documents: List of loaded document pages

        Returns:
            list: List of text chunks
        """
        print("✂️  Splitting text into chunks...")
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            text_chunks = text_splitter.split_documents(documents)
            print(f"✅ Created {len(text_chunks)} text chunks")

            # Display sample chunk for verification
            if text_chunks:
                print(f"📝 Sample chunk preview: {text_chunks[0].page_content[:200]}...")

            return text_chunks
        except Exception as e:
            print(f"❌ Error splitting text: {str(e)}")
            raise

    def create_embeddings_model(self):
        """
        Initialize the HuggingFace embeddings model.

        Returns:
            HuggingFaceEmbeddings: Configured embeddings model
        """
        print("🧠 Initializing embeddings model...")
        try:
            embeddings_model = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},  # Use CPU for compatibility
                encode_kwargs={'normalize_embeddings': True}
            )
            print(f"✅ Embeddings model '{self.embedding_model_name}' loaded successfully")
            return embeddings_model
        except Exception as e:
            print(f"❌ Error loading embeddings model: {str(e)}")
            raise

    def create_vector_database(self, text_chunks, embeddings_model):
        """
        Create and save the FAISS vector database.

        Args:
            text_chunks: List of text chunks to embed
            embeddings_model: HuggingFace embeddings model
        """
        print("🗄️  Creating vector database...")
        try:
            # Create vector database from text chunks
            vector_database = FAISS.from_documents(
                documents=text_chunks,
                embedding=embeddings_model
            )

            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)

            # Save the vector database locally
            vector_database.save_local(self.vector_db_path)
            print(f"✅ Vector database saved successfully at {self.vector_db_path}")

            # Verify the database was created
            saved_files = os.listdir(self.vector_db_path)
            print(f"📁 Database files created: {saved_files}")

        except Exception as e:
            print(f"❌ Error creating vector database: {str(e)}")
            raise

    def run_complete_pipeline(self):
        """
        Execute the complete data ingestion pipeline.
        """
        print("🚀 Starting Sahay AI Data Ingestion Pipeline")
        print("=" * 50)

        try:
            # Step 1: Validate PDF exists
            if not self.validate_pdf_exists():
                return False

            # Step 2: Load PDF document
            documents = self.load_pdf_document()

            # Step 3: Split into chunks
            text_chunks = self.split_text_into_chunks(documents)

            # Step 4: Initialize embeddings model
            embeddings_model = self.create_embeddings_model()

            # Step 5: Create vector database
            self.create_vector_database(text_chunks, embeddings_model)

            print("\n🎉 Data ingestion pipeline completed successfully!")
            print("The vector database is ready for the Sahay AI agent.")
            return True

        except Exception as e:
            print(f"\n💥 Pipeline failed with error: {str(e)}")
            return False


def main():
    """
    Main function to run the data ingestion pipeline.
    """
    # Initialize and run the pipeline
    pipeline = SahayDataPipeline()
    success = pipeline.run_complete_pipeline()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
