import os
from typing import Any, Dict, List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from loguru import logger


class VectorDBManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def create_documents_from_pricing_data(
        self, pricing_data: Dict[str, Any]
    ) -> List[Document]:
        """Convert pricing data into documents for vector storage, preserving section context"""
        documents = []

        # Create separate documents for each logical section
        sections = [
            {
                "title": "Service Packages Overview",
                "content": """Bike Hero offers three tiers for both one-time and annual service plans. All include parts, transport, and labor.

One‑Time Services (completed within 2 days):
- Essential – SGD 59: Basic safety check & tune (brakes, gearing, tires, headset, saddle). Add‑on repairs extra.
- Advanced – SGD 89: Includes Essential + drivetrain cleaning (cassette, chain, derailleurs, chainring). Excludes bottom bracket/hubs.
- Premium – SGD 129: Advanced + full bike wash (frame, wheels, handlebar, saddle, brakes disc/rim). Excludes bottom bracket/hubs.

Annual Packages – Twice‑a‑Year Service + ~20% Savings:
- Essential – SGD 94 (Save SGD 24)
- Advanced – SGD 142 (Save SGD 36)
- Premium – SGD 206 (Save SGD 51)

Annual services include the same scopes as one-time, but performed twice yearly.""",
                "section": "packages",
            },
            {
                "title": "Add-On Services Pricing",
                "content": """Add‑On / Ad‑Hoc Services - These can be added to any package for specific repairs:

Tire & Tube Services:
- Inner-tube replacement (standard): SGD 29
- Inner-tube (cargo/Dutch bike): SGD 39
- Tire replacement: from SGD 50
- Tire + tube: from SGD 60
- Cargo/Dutch bike tire: from SGD 65

Wheel & Drivetrain Services:
- Wheel truing: SGD 40
- Cable & housing (shifter/brake): SGD 29–35
- Chain replacement (1–8 spd): from SGD 40; 9‑spd: SGD 50; 10‑spd: SGD 60; 11‑spd: SGD 70
- Derailleur (front): from SGD 60; (rear): from SGD 70
- Shifter: from SGD 50

Brake Services:
- Brake pads (rim): from SGD 26; (disc): from SGD 35
- Brake bleeding: SGD 45; disk clean: SGD 30
- Brake lever: from SGD 35; Rotor: from SGD 45

Other Services:
- Bike assembly: SGD 100
- Bike packing: SGD 100 (box not included)
- Pedals: SGD 35; Kickstand: SGD 35; Bar tape: SGD 50; Grips: SGD 25""",
                "section": "addons",
            },
            {
                "title": "Service Features & Policies",
                "content": """Service Features & Policies:

Location: Home service across all Singapore, convenient booking, quote → appointment → service at your location (home, carpark, etc.)

Timing: typically 30–90 minutes per bike

Payment: After service, via PayNow or bank transfer; insured by QBE covering liability and product damage

Guarantee: Post-service issues are addressed quickly with follow-up visits. Warranty on parts/service holds.""",
                "section": "policies",
            },
            {
                "title": "Service Recommendations",
                "content": """Choosing recommendations:

- Safety-focused or basic tune → go for Essential
- Want drivetrain clean too → Advanced
- Prefer a deep clean + full wash → Premium
- Regular rider? Annual plans often save ~20%
- Have specific parts or repairs? Add‑ons are modular""",
                "section": "recommendations",
            },
        ]

        # Create documents from each section
        for i, section in enumerate(sections):
            doc = Document(
                page_content=f"{section['title']}\n\n{section['content']}",
                metadata={
                    "source": "bikehero_pricing",
                    "section": section["section"],
                    "section_title": section["title"],
                    "chunk_id": i,
                },
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

        logger.info(f"vector store documents: {documents}")

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
