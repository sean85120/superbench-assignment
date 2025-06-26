import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI

from backend.src.utils.vector_db import VectorDBManager

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ResponseTemplates:
    """Centralized response templates for the AI agent"""

    def __init__(self, booking_url: str):
        self.booking_url = booking_url

    @property
    def system_prompt(self) -> str:
        """System prompt for RAG-based responses"""
        return """You are a helpful AI assistant for BikeHero bicycle maintenance services.

IMPORTANT RULES:
1. ONLY answer questions about BikeHero's bicycle maintenance services and pricing
2. If the user asks about anything else (cars, other companies, general topics), respond with "Transfer to human agent"
3. If you don't have specific pricing information for their question, respond with "Transfer to human agent"
4. If the question is too complex or requires personal consultation, respond with "Transfer to human agent"
5. If the user wants to book services, respond with "Transfer to human agent"

When you need to transfer to human agent, always provide these options:
1. Provide your name, phone number, and email for follow-up
2. Book directly through our website at https://bikehero.sg/goifnmnf

PLEASE NOTE: If the user provides their contact information, display the contact information to them and respond with "Thank you for providing your contact information. Please wait for our team to contact you."

Be polite and professional. Add line breaks for better readability.
"""

    @property
    def relevance_classifier_prompt(self) -> str:
        """Prompt for classifying message relevance"""
        return "You are a classifier. Determine if the user's message is related to BikeHero services, bike services in general, OR if they are providing contact information for booking services. Consider the chat history context when making your decision. If the user is providing their name, phone number, email, or other contact details for booking, classify as relevant. Respond with only 'YES' or 'NO'."

    def get_off_topic_response(self) -> Dict[str, Any]:
        """Response for off-topic messages"""
        return {
            "response": "I'm here to help with BikeHero's bicycle maintenance services. Could you please ask me about our bike maintenance packages, pricing, or other BikeHero-related services?",
            "metadata_info": {"requires_human": False, "topic": "off_topic"},
        }

    def get_human_agent_transfer_response(self) -> Dict[str, Any]:
        """Response when transferring to human agent"""
        return {
            "response": f"I apologize, but I don't have enough information to fully answer your question.\n\nTo better assist you, you can:\n\n1. **Provide your contact information** - Please share your name, phone number, and email so we can contact you directly\n\n2. **Book directly online** - Visit our booking system at {self.booking_url} to schedule your service\n\nHow would you prefer to proceed?",
            "metadata_info": {
                "requires_human": True,
                "topic": "bikehero_services",
            },
        }

    def get_vector_search_error_response(self, error: str) -> Dict[str, Any]:
        """Response when vector search fails"""
        return {
            "response": f"I apologize, but I'm having trouble accessing the pricing information right now.\n\nTo better assist you, you can:\n\n1. Provide your contact information - Please share your name, phone number, and email so we can contact you directly\n\n2. Book directly online - Visit our booking system at {self.booking_url} to schedule your service\n\nHow would you prefer to proceed?",
            "metadata_info": {
                "requires_human": True,
                "error": error,
                "topic": "bikehero_services",
            },
        }

    def get_general_error_response(self, error: str) -> Dict[str, Any]:
        """Response for general errors"""
        return {
            "response": f"Transfer to human agent\n\nTo better assist you, you can:\n\n1. **Provide your contact information** - Please share your name, phone number, and email so we can contact you directly\n\n2. **Book directly online** - Visit our booking system at {self.booking_url} to schedule your service",
            "metadata_info": {"requires_human": True, "error": error},
        }

    def get_success_response(self, content: str) -> Dict[str, Any]:
        """Response for successful AI-generated responses"""
        return {
            "response": content,
            "metadata_info": {
                "requires_human": False,
                "topic": "bikehero_services",
            },
        }


class AIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.chat_model = ChatOpenAI(
            model_name="gpt-4.1-mini",
            temperature=0.7,
            api_key=OPENAI_API_KEY,
        )
        self.vector_db = VectorDBManager()
        self.booking_url = "https://bikehero.sg/goifnmnf"
        self.response_templates = ResponseTemplates(self.booking_url)

        # Initialize the vector store with default pricing data
        self.vector_db.initialize_vectorstore()

    def set_pricing_context(self, pricing_data: Dict[str, Any]):
        """Set the pricing context for the RAG system"""
        self.vector_db.update_pricing_data(pricing_data)

    async def process_message(
        self, message: str, chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response using RAG with chat history"""
        try:
            # Prepare chat history for context
            chat_context = ""
            if chat_history:
                chat_context = "\n\nChat History:\n"
                for entry in chat_history[-5:]:  # Last 5 messages for context
                    role = entry.get("role", "user")
                    content = entry.get("content", "")
                    chat_context += f"{role.title()}: {content}\n"

            # First, check if the question is related to BikeHero or bike services with chat history context
            relevance_check_prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content=self.response_templates.relevance_classifier_prompt
                    ),
                    HumanMessage(
                        content=f"{chat_context}\n\nCurrent Message: {message}"
                    ),
                ]
            )

            relevance_response = await self.chat_model.ainvoke(
                relevance_check_prompt.format_messages()
            )
            is_relevant = "yes" in relevance_response.content.lower()

            if not is_relevant:
                return self.response_templates.get_off_topic_response()

            # For relevant questions, retrieve context and generate response
            try:
                relevant_context = self.vector_db.search_relevant_context(message)
                context_text = "\n\n".join(relevant_context)

                # Create the chat prompt with retrieved context and chat history
                prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(content=self.response_templates.system_prompt),
                        HumanMessage(
                            content=f"Pricing Information:\n{context_text}\n\n{chat_context}\n\nChat History:\n{chat_history}\n\nUser Question: {message}"
                        ),
                    ]
                )

                # Generate response
                response = await self.chat_model.ainvoke(prompt.format_messages())

                # Check if the response indicates need for human agent
                if "transfer to human agent" in response.content.lower():
                    return self.response_templates.get_human_agent_transfer_response()

                return self.response_templates.get_success_response(response.content)

            except Exception as e:
                # If vector search fails, fall back to human agent
                return self.response_templates.get_vector_search_error_response(str(e))

        except Exception as e:
            return self.response_templates.get_general_error_response(str(e))


if __name__ == "__main__":
    import asyncio

    agent = AIAgent()

    # Example with chat history
    chat_history = [
        {"role": "user", "content": "Hi, I need bike maintenance"},
        {
            "role": "assistant",
            "content": "Hello! I'd be happy to help you with BikeHero's bicycle maintenance services. What specific service are you looking for?",
        },
    ]

    print(
        asyncio.run(
            agent.process_message(
                "What is the price of the Essential package? What is the price of the Annual package?",
                chat_history=chat_history,
            )
        )
    )
