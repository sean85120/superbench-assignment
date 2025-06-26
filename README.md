# AI Agent Service

A full-stack application with a FastAPI backend and React frontend for an AI-powered bike maintenance assistant.

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

## Environment Variables
Provide the following environment variables in a .env file in the root directory of the project.
```
OPENAI_API_KEY=your_openai_api_key
```

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd superbench_assignment
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Stopping the Application
```bash
docker-compose down
```

## Development Setup

### Backend (Python/FastAPI)
```bash
cd backend
poetry install
poetry run python main.py
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `POST /chat/` - Send a message to the AI agent
- `GET /chat/history/` - Get chat history
- `POST /agent/pricing/` - Update pricing context
- `GET /` - Health check

## Docker Services

- **backend**: FastAPI application running on port 8000
- **frontend**: React application running on port 3000

## Technical Overview - Backend Strategy

### Architecture Overview
The backend is built using **FastAPI** with a modular architecture designed for scalability and maintainability. The system implements a **Retrieval-Augmented Generation (RAG)** pattern to provide context-aware responses for bike maintenance services.

### Core Components

#### 1. **AI Agent Engine** (`src/utils/ai_agent.py`)
- **LLM Integration**: Uses OpenAI's GPT-4.1-mini model via LangChain for natural language processing
- **RAG Implementation**: Combines vector search with LLM generation for context-aware responses
- **Relevance Filtering**: Classifies user queries to ensure responses are bike service-related
- **Fallback Strategy**: Gracefully handles edge cases by routing to human agents when needed

#### 2. **Vector Database Management** (`src/utils/vector_db.py`)
- **Embedding Engine**: Uses OpenAI embeddings for semantic search
- **ChromaDB Integration**: Persistent vector store for pricing and service information
- **Dynamic Updates**: Supports real-time pricing data updates without service restart
- **Context Retrieval**: Semantic search with configurable result count (default: 3 most relevant chunks)

#### 3. **Data Layer** (`src/models/models.py`)
- **SQLAlchemy ORM**: Async database operations with SQLite backend
- **Entity Models**:
  - `Agent`: Represents AI agents with metadata
  - `ChatHistory`: Stores conversation history with metadata
  - `Task`: Task management system (extensible)
- **JSON Metadata**: Flexible storage for additional context and pricing information

### System Prompt Chain of Thoughts

The AI agent uses a carefully crafted system prompt that implements a **chain of thoughts** approach to ensure consistent, context-aware responses:

#### **Thought Process Flow**

1. **Identity Establishment**
   ```
   "You are a helpful AI assistant for BikeHero's bicycle maintenance services."
   ```
   - Sets the agent's role and domain expertise
   - Establishes the scope of knowledge and authority

2. **Boundary Definition**
   ```
   "IMPORTANT RULES:
   1. ONLY answer questions about BikeHero's bicycle maintenance services and pricing
   2. If the user asks about anything else (cars, other companies, general topics), respond with 'Transfer to human agent'
   3. If you don't have specific pricing information for their question, respond with 'Transfer to human agent'
   4. If the question is too complex or requires personal consultation, respond with 'Transfer to human agent'
   5. If the user wants to book services, respond with 'Transfer to human agent'"
   ```
   - Defines clear boundaries for the AI's capabilities
   - Establishes fallback conditions for human intervention
   - Prevents scope creep and off-topic responses

3. **Action Framework**
   ```
   "When you need to transfer to human agent, always provide these options:
   1. Provide your name, phone number, and email for follow-up
   2. Book directly through our website at https://bikehero.sg/goifnmnf"
   ```
   - Provides structured escalation paths
   - Ensures consistent user experience during handoffs
   - Maintains business continuity

4. **Contact Handling Protocol**
   ```
   "PLEASE NOTE: If the user provides their contact information, display the contact information to them and respond with 'Thank you for providing your contact information. Please wait for our team to contact you.'"
   ```
   - Implements contact information validation
   - Provides immediate feedback for user actions
   - Sets expectations for follow-up

5. **Presentation Guidelines**
   ```
   "Be polite and professional. Add line breaks for better readability."
   ```
   - Ensures consistent tone and formatting
   - Improves user experience through better readability

#### **Chain of Thoughts Execution**

When processing a user query, the LLM follows this reasoning chain:

1. **Input Analysis**: Parse the user's question and extract key intent
2. **Relevance Check**: Determine if the query falls within BikeHero's scope
3. **Information Retrieval**: Search vector database for relevant pricing/service context
4. **Response Generation**: Combine retrieved context with system prompt guidelines
5. **Escalation Decision**: Determine if human agent transfer is needed
6. **Output Formatting**: Apply presentation guidelines for readability

This structured approach ensures the AI agent maintains consistency, stays within scope, and provides appropriate escalation paths when needed.

### Key Technical Features

#### **RAG Pipeline**
1. **Query Classification**: Determines if user input is bike service-related
2. **Vector Search**: Retrieves relevant pricing/service context from ChromaDB
3. **Context Injection**: Combines retrieved context with chat history
4. **Response Generation**: LLM generates responses using system prompts and context
5. **Fallback Handling**: Routes complex queries to human agents

#### **Data Persistence Strategy**
- **SQLite Database**: Lightweight, file-based storage for development/production
- **Vector Store**: ChromaDB for semantic search with persistent storage
- **Chat History**: Complete conversation tracking with metadata
- **Agent Management**: Extensible system for multiple AI agents

#### **Performance Optimizations**
- **Async Database Operations**: Non-blocking database queries
- **Vector Search Caching**: Persistent ChromaDB for fast semantic search
- **Context Window Management**: Limits chat history to last 5 messages
- **Error Handling**: Graceful degradation with human agent fallback

#### **Security & Configuration**
- **Environment Variables**: Secure API key management via `.env`
- **CORS Configuration**: Configurable cross-origin policies
- **Input Validation**: Pydantic schemas for request/response validation
- **Logging**: Structured logging with Loguru for debugging and monitoring

### Technology Stack
- **Framework**: FastAPI (Python 3.12+)
- **LLM**: OpenAI GPT-4.1-mini via LangChain
- **Vector Database**: ChromaDB with OpenAI embeddings
- **Database**: SQLite with SQLAlchemy async ORM
- **Dependency Management**: Poetry
- **Containerization**: Docker with multi-stage builds
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## To Do Work

### Task Model Integration with Human Agent Transfer

#### **Objective**
Implement automatic task creation when the LLM transfers to human agent, enabling seamless contact information capture and follow-up workflows.

#### **Implementation Plan**

##### 1. **Enhanced Contact Information Extraction**
- Implement LLM-powered contact information extraction from user messages
- Parse name, phone number, and email addresses intelligently
- Handle partial or missing contact information gracefully
- Return structured data for task creation

##### 2. **Task Creation Workflow**
- Automatically create Task records when LLM detects human agent transfer need
- Capture full context including original message, extracted contact info, and chat history
- Link tasks to specific agents for proper assignment and tracking
- Include comprehensive task descriptions with all relevant customer information

##### 3. **Enhanced Chat Response Processing**
- Modify existing chat endpoint to detect when AI agent transfers to human
- Integrate contact extraction and task creation seamlessly into the response flow
- Update response metadata with task information and contact details
- Maintain existing chat history while adding task creation capabilities

##### 4. **Task Management API Endpoints**
- Create new endpoints for retrieving pending tasks for human agents
- Implement task status update functionality (pending, in_progress, completed, failed)
- Add proper error handling and validation for task operations
- Provide filtering and sorting capabilities for task management

##### 5. **Notification System Integration**
- Implement email notification system for human agent alerts
- Add SMS notification capabilities for urgent inquiries
- Create structured notification content with all relevant customer information
- Support configurable notification channels and preferences

#### **Workflow Integration**

1. **User provides contact information** → LLM detects transfer need
2. **Contact info extraction** → Parse name, phone, email from message
3. **Task creation** → Create Task record with full context
4. **Notification dispatch** → Alert human agent via email/SMS
5. **Status tracking** → Monitor task progress through completion
6. **Follow-up coordination** → Human agent contacts customer

#### **Benefits**

- **Seamless Handoff**: Automatic task creation when AI transfers to human
- **Contact Capture**: Intelligent extraction of contact information
- **Context Preservation**: Full chat history and context passed to human agent
- **Notification System**: Immediate alerts for human agents
- **Status Tracking**: Monitor task progress and completion
- **Scalable Workflow**: Extensible system for multiple agents and task types

#### **Next Steps**

1. Implement contact information extraction logic
2. Create task management API endpoints
3. Integrate notification system (email/SMS)
4. Add task status tracking and updates
5. Create human agent dashboard for task management
6. Implement task completion workflows
7. Add analytics and reporting for task performance
