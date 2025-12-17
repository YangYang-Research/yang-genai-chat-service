# 🧠 Yang GenAI Chat Service

**Yang GenAI Chat Service** is a lightweight, modular backend service designed to power **Generative AI chat experiences**.  
Built on **FastAPI**, it integrates **LangChain**, **AWS Bedrock**, and a flexible plugin system for multi-source reasoning and retrieval.

---

## 🚀 Features

- ⚡ **FastAPI Backend** — Modern, async-first API framework for speed and scalability  
- 🧩 **LangChain Integration** — Manage LLM reasoning, tool use, and memory  
- 🗄️ **PostgreSQL** — Persistent storage for chat history, users, and agent data  
- 🔐 **AWS Secret Manager** — Secure configuration and credential management  
- 🧠 **AWS Bedrock Support** — Integrate with enterprise-grade LLMs (Claude, Titan, etc.)  
- 🧰 **Agent Tool Ecosystem** — Easily extendable set of search and retrieval tools  
- 🔄 **Streaming Responses** — Real-time streaming chat completions via Server-Sent Events (SSE)  
- 🔑 **JWT Authentication** — Secure API access with token-based authentication  
- 👥 **User & Role Management** — Multi-user support with role-based access control  
- 🏷️ **Tagging System** — Organize and categorize conversations and messages  

---

## 🏗️ Architecture Overview

                ┌────────────────────────────┐
                │     Yang GenAI Chat UI     │
                └────────────┬───────────────┘
                             │  REST / WebSocket
                             ▼
                 ┌────────────────────────────┐
                 │  Yang GenAI Chat Service   │
                 │  (FastAPI + LangChain)     │
                 ├────────────────────────────┤
                 │  🧠 LLM Orchestration      │
                 │  🔍 Agent Tools            │
                 │  💾 PostgreSQL Persistence │
                 │  🔐 AWS Secrets Integration│
                 └────────────┬───────────────┘
                             ▼
                 ┌────────────────────────────┐
                 │     AWS Bedrock Models     │
                 │   (Claude, Titan, etc.)    │
                 └────────────────────────────┘


---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/) |
| **Database** | PostgreSQL (async via SQLAlchemy) |
| **Secrets Management** | AWS Secrets Manager |
| **LLM Provider** | AWS Bedrock |
| **Environment** | Python 3.10+ |

---

## 🧩 Agent Tools

The Yang agent uses multiple **retrieval and reasoning tools** to augment its responses.  
These tools can be dynamically enabled or extended via LangChain Tool APIs.

| Tool Name | Description |
|------------|-------------|
| **DuckDuckGo** | Web search without API keys |
| **Arxiv** | Research paper retrieval |
| **Wikipedia** | General knowledge access |
| **GoogleSearch** | Comprehensive web search |
| **GoogleScholar** | Academic publication search |
| **GoogleTrends** | Trending topic data |
| **AskNews** | News-based insights |
| **RedditSearch** | Community discussion data |
| **SearxSearch** | Privacy-preserving metasearch |
| **OpenWeather** | Real-time weather information |
| **DateTime** | Current date and time queries with timezone support |

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database (optional, can be disabled)
- AWS account with Bedrock access
- AWS credentials configured (via AWS CLI or environment variables)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YangYang-Research/yang-genai-chat-service.git
   cd yang-genai-chat-service
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS credentials**
   Follow the instructions in the [Yang-GenAI-Chat-UI](https://github.com/YangYang-Research/yang-genai-chat-ui) repository to configure the AWS credentials. Skip this step if you have already configured the AWS credentials in Yang-GenAI-Chat-UI.

5. **Create AWS Secret Manager**
   Follow the instructions in the [Yang-GenAI-Chat-UI](https://github.com/YangYang-Research/yang-genai-chat-ui) repository to create the AWS Secret Manager. Skip this step if you have already created the AWS Secret Manager in Yang-GenAI-Chat-UI.
   
6. **Configure environment variables**
   
    Copy the `.env.example` file to `.env` and configure the environment variables.
    ```bash
    cp .env.example .env
    ```
    Configure the environment variables.
    ```env
    AWS_REGION=us-east-1
    AWS_SECRET_NAME=yang-genai-chat-secret
    API_AUTH_KEY_NAME=api_auth_key
    APP_JWT_KEY_NAME=app_jwt_key
    DB_USERNAME_KEY=db_username
    DB_PWD_KEY=db_password

    ... other environment variables ...
    ```

7. **Run the application**
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

8. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Health Check: `http://localhost:8000/health`

9. **Administrator Account**
    The administrator account is `administrator` with the email `your-configuration-APP_ADMIN_EMAIL-in-env-file` and the password is the one generated during the database seeding. You can find the password in the logs of the application.

---

## 🔌 API Endpoints

### Authentication
- `POST /v1/authentication/login` - User login and token generation

### Chat
- `POST /v1/chat/agent/completions` - Agent-based chat completions (streaming)
- `POST /v1/chat/llm/completions` - Direct LLM chat completions (streaming)

### Users
- `POST /v1/users` - Create user
- `GET /v1/users` - List users
- `GET /v1/users/{user_id}` - Get user by ID
- `PUT /v1/users/{user_id}` - Update user
- `DELETE /v1/users/{user_id}` - Delete user

### Agents
- `POST /v1/agents` - Create agent
- `GET /v1/agents` - List agents
- `GET /v1/agents/{agent_id}` - Get agent by ID
- `PUT /v1/agents/{agent_id}` - Update agent
- `DELETE /v1/agents/{agent_id}` - Delete agent
- `GET /v1/agents/default` - Get default agent

### LLMs
- `POST /v1/llms` - Create LLM model
- `GET /v1/llms` - List LLM models
- `GET /v1/llms/{llm_id}` - Get LLM by ID
- `PUT /v1/llms/{llm_id}` - Update LLM
- `DELETE /v1/llms/{llm_id}` - Delete LLM
- `GET /v1/llms/enabled` - Get enabled LLM models

### Tools
- `POST /v1/tools` - Create tool
- `GET /v1/tools` - List tools
- `GET /v1/tools/{tool_id}` - Get tool by ID
- `PUT /v1/tools/{tool_id}` - Update tool
- `DELETE /v1/tools/{tool_id}` - Delete tool
- `GET /v1/tools/enabled` - Get enabled tools

### Messages
- `POST /v1/messages` - Create message
- `GET /v1/messages/user/{user_id}` - Get user messages
- `GET /v1/messages/{message_id}` - Get message by ID
- `DELETE /v1/messages/{message_id}` - Delete message

### Roles
- `POST /v1/roles` - Create role
- `GET /v1/roles` - List roles
- `GET /v1/roles/{role_id}` - Get role by ID
- `PUT /v1/roles/{role_id}` - Update role
- `DELETE /v1/roles/{role_id}` - Delete role

### Tags
- `POST /v1/tags` - Create tag
- `GET /v1/tags` - List tags
- `GET /v1/tags/{tag_id}` - Get tag by ID
- `PUT /v1/tags/{tag_id}` - Update tag
- `DELETE /v1/tags/{tag_id}` - Delete tag
- `GET /v1/tags/enabled` - Get enabled tags

### Health
- `GET /health` - Health check endpoint

> **Note:** Most endpoints require authentication via Yang Basic authentication. Include the token in the `x-yang-auth` header: `Basic <your-api-auth-key>`

---

## 🔧 Configuration

### Database Setup

The service uses PostgreSQL with async SQLAlchemy. Database credentials should be stored in AWS Secrets Manager and referenced via `DB_USERNAME_KEY` and `DB_PWD_KEY` environment variables.

### Tool Configuration

Tools are managed through the database and can be enabled/disabled dynamically.

---

## 🚀 Usage Example

### Chat with Agent

```bash
curl -X POST "http://localhost:8000/v1/chat/agent/completions" \
  -H "x-yang-auth: Basic <your-api-auth-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_session_id": "session-123",
    "agent_name": "yang-agent",
    "model_name": "anthropic_claude_sonet_4_5",
    "messages": [
      {
        "role": "user",
        "content": "What is the latest news about AI?"
      }
    ]
  }'
```

### Direct LLM Chat

```bash
curl -X POST "http://localhost:8000/v1/chat/llm/completions" \
  -H "x-yang-auth: Basic <your-api-auth-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_session_id": "session-123",
    "model_name": "anthropic_claude_sonet_4_5",
    "messages": [
      {
        "role": "user",
        "content": "Explain quantum computing in simple terms"
      }
    ]
  }'
```

---

## 📝 License

See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or support, please contact: administrator@yang.app

---

