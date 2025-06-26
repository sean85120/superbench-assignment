import os
from typing import Any, Dict, List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


class VectorDBManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def create_documents_from_pricing_data(
        self, pricing_data: Dict[str, Any]
    ) -> List[Document]:
        """Convert pricing data into documents for vector storage"""
        documents = []

        # Create a comprehensive document from the pricing context
        pricing_text = f"""
        BikeHero Maintenance Packages Pricing Information:
        
        Essential Package:
        - One-time service: SGD 59
        - Annual package (2 services): SGD 94
        - Includes: Tune brakes, gearing, tires, headset, saddle
        
        Advanced Package:
        - One-time service: SGD 89
        - Annual package (2 services): SGD 142
        - Includes: All Essential services + cassette/chain/derailleurs/chainring cleaning (excludes BB & hubs)
        
        Premium Package:
        - One-time service: SGD 129
        - Annual package (2 services): SGD 206
        - Includes: All Advanced services + full wash (frame, wheels, bars, saddle, brakes) (excludes BB & hubs)
        
        Service Information:
        - One-time services: ~2-day turnaround
        - Annual package saves approximately 20% versus two one-time services

        If there are any other questions, please ask the user to provide their contact information or book directly through our website at https://bikehero.sg/goifnmnf
        """

        # Split the text into chunks
        text_chunks = self.text_splitter.split_text(pricing_text)

        # Create documents from chunks
        for i, chunk in enumerate(text_chunks):
            doc = Document(
                page_content=chunk,
                metadata={"source": "bikehero_pricing", "chunk_id": i},
            )
            documents.append(doc)

        return documents

    def initialize_vectorstore(self, pricing_data: Dict[str, Any] = None):
        """Initialize the vector store with pricing data"""
        if pricing_data is None:
            # Use default pricing data
            pricing_data = {
                "packages": {
                    "Essential": {
                        "one_time": 59,
                        "annual": 94,
                        "includes": "Tune brakes, gearing, tires, headset, saddle",
                    },
                    "Advanced": {
                        "one_time": 89,
                        "annual": 142,
                        "includes": "All Essential + cassette/chain/derailleurs/chainring cleaning (excl. BB & hubs)",
                    },
                    "Premium": {
                        "one_time": 129,
                        "annual": 206,
                        "includes": "All Advanced + full wash (frame, wheels, bars, saddle, brakes) (excl. BB & hubs)",
                    },
                },
                "info": {
                    "turnaround": "~2-day turnaround",
                    "annual_savings": "20% versus two one-times",
                },
            }

        documents = self.create_documents_from_pricing_data(pricing_data)

        # Create or load the vector store
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )

        # Persist the vector store
        self.vectorstore.persist()

    def search_relevant_context(self, query: str, k: int = 3) -> List[str]:
        """Search for relevant context based on the query"""
        if self.vectorstore is None:
            raise ValueError(
                "Vector store not initialized. Call initialize_vectorstore() first."
            )

        # Search for relevant documents
        docs = self.vectorstore.similarity_search(query, k=k)

        # Extract the content from the documents
        context = [doc.page_content for doc in docs]
        return context

    def update_pricing_data(self, new_pricing_data: Dict[str, Any]):
        """Update the vector store with new pricing data"""
        self.initialize_vectorstore(new_pricing_data)
