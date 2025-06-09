# Multi-Agent A2A Protocol Implementation

A demonstration of Agent-to-Agent (A2A) communication protocol using two different AI frameworks: **LangChain** and **PydanticAI**.

## 🎯 Project Overview

This project implements a multi-agent system where two AI agents communicate with each other through a standardized A2A protocol to perform complementary text processing tasks:

- **Agent 1 (LangChain)**: Performs comprehensive text analysis
- **Agent 2 (PydanticAI)**: Refines and summarizes the analysis output

## 🏗️ Architecture

```
┌─────────────┐    A2A Protocol    ┌─────────────┐    A2A Protocol    ┌─────────────┐
│   Client    │ ──────────────────► │   Agent 1   │ ──────────────────► │   Agent 2   │
│             │                    │ (LangChain) │                    │(PydanticAI) │
│ Orchestrator│ ◄────────────────── │Text Analysis│ ◄────────────────── │Text Refiner │
└─────────────┘                    └─────────────┘                    └─────────────┘
     8000                               8001                               8002
```

### Communication Flow

1. **Discovery**: Client fetches agent capabilities via `/.well-known/agent.json`
2. **Analysis**: Client sends text to Agent 1 for comprehensive analysis
3. **Refinement**: Agent 1's output is automatically sent to Agent 2 for refinement
4. **Results**: Client receives both original analysis and refined summary

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google API Key (for Gemini model access)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd hw3-ai-nfac
   ```

2. **Set up environment variables:**
   ```bash
   # Create .env file in both agent directories
   echo "GOOGLE_API_KEY=your_google_api_key_here" > agent1_langchain/.env
   echo "GOOGLE_API_KEY=your_google_api_key_here" > agent2_pydanticai/.env
   ```

3. **Install dependencies for Agent 1:**
   ```bash
   cd agent1_langchain
   pip install -r requirements.txt
   cd ..
   ```

4. **Install dependencies for Agent 2:**
   ```bash
   cd agent2_pydanticai
   pip install -r requirements.txt
   cd ..
   ```

5. **Install client dependencies:**
   ```bash
   pip install -r client_requirements.txt
   ```

### Running the System

1. **Start Agent 1 (Terminal 1):**
   ```bash
   cd agent1_langchain
   python main.py
   ```
   → Agent 1 runs on `http://localhost:8001`

2. **Start Agent 2 (Terminal 2):**
   ```bash
   cd agent2_pydanticai
   python main.py
   ```
   → Agent 2 runs on `http://localhost:8002`

3. **Run the client (Terminal 3):**
   ```bash
   python client.py
   ```

## 📋 Agent Specifications

### Agent 1 - LangChain Text Analyzer

**Port**: 8001  
**Framework**: LangChain + Google Gemini  
**Capability**: `text-analysis`

**Function**: Performs comprehensive text analysis including:
- Key themes and topics identification
- Sentiment and tone analysis
- Main insights extraction
- Areas for further investigation

**Endpoints**:
- `GET /.well-known/agent.json` - Agent discovery
- `POST /tasks/send` - Task execution
- `GET /health` - Health check

### Agent 2 - PydanticAI Text Refiner

**Port**: 8002  
**Framework**: PydanticAI + Google Gemini  
**Capability**: `text-refinement`

**Function**: Refines and structures text analysis:
- Creates concise summaries (50-100 words)
- Extracts 3-5 key insights
- Removes verbosity and redundancy
- Calculates word count reduction

**Endpoints**:
- `GET /.well-known/agent.json` - Agent discovery
- `POST /tasks/send` - Task execution
- `GET /health` - Health check

## 🔄 A2A Protocol Implementation

### Agent Discovery
```json
{
  "schemaVersion": "1.0",
  "agentId": "agent1-langchain",
  "name": "LangChain Agent 1",
  "description": "Analyzes text inputs via LangChain LLM",
  "handler": {
    "type": "http",
    "url": "http://localhost:8001/tasks/send"
  },
  "capabilities": [
    {
      "type": "skill",
      "name": "text-analysis",
      "description": "Performs brief text analysis"
    }
  ]
}
```

### Task Request Format
```json
{
  "task_id": "uuid-string",
  "messages": [
    {
      "role": "user",
      "parts": [
        {
          "content": "Text to be processed..."
        }
      ]
    }
  ],
  "use_stream": false
}
```

### Task Response Format
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "messages": [
    {
      "role": "agent",
      "parts": [
        {
          "content": "Processed result..."
        }
      ]
    }
  ]
}
```

## 📊 Sample Workflow

### Input
```
"Describe the key trends in AI, focusing on recent developments in large language models, retrieval-augmented generation, and multi-agent systems."
```

### Agent 1 Output (Analysis)
```
Comprehensive analysis covering:
- Current AI trends and developments
- Technical details about LLMs, RAG, and multi-agent systems
- Future implications and predictions
- Detailed technical explanations
```

### Agent 2 Output (Refined)
```json
{
  "summary": "Concise 75-word summary of key AI trends...",
  "key_insights": [
    "LLMs are becoming more efficient and specialized",
    "RAG systems improve factual accuracy",
    "Multi-agent systems enable complex task decomposition"
  ],
  "cleaned_text": "Streamlined version without redundancy...",
  "word_count_reduction": "Reduced from 450 to 200 words (55.6% reduction)"
}
```

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| Agent 1 Framework | LangChain |
| Agent 2 Framework | PydanticAI |
| LLM Provider | Google Gemini 2.0 Flash Lite |
| Web Framework | FastAPI |
| HTTP Client | httpx |
| Data Validation | Pydantic |
| Environment | Python 3.8+ |

## 🔍 Testing and Validation

### Health Checks
```bash
# Check Agent 1
curl http://localhost:8001/health

# Check Agent 2
curl http://localhost:8002/health
```

### Manual Agent Testing
```bash
# Test Agent 1 directly
curl -X POST http://localhost:8001/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-123",
    "messages": [
      {
        "role": "user",
        "parts": [{"content": "Analyze this text..."}]
      }
    ]
  }'
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: GOOGLE_API_KEY environment variable is required
   ```
   **Solution**: Ensure `.env` files are created with valid Google API key

2. **Port Already in Use**
   ```
   Error: [Errno 98] Address already in use
   ```
   **Solution**: Kill existing processes or change port numbers

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'langchain'
   ```
   **Solution**: Install requirements in each agent directory

### Logs and Debugging

- Agent logs show request processing status
- Use health endpoints to verify agent status
- Check client output for detailed workflow progress

## 📝 Development Notes

### Code Structure
```
hw3-ai-nfac/
├── agent1_langchain/
│   ├── main.py              # LangChain agent implementation
│   ├── requirements.txt     # Dependencies
│   └── .well-known/
│       └── agent.json       # Agent discovery metadata
├── agent2_pydanticai/
│   ├── main.py              # PydanticAI agent implementation
│   ├── requirements.txt     # Dependencies
│   └── .well-known/
│       └── agent.json       # Agent discovery metadata
├── client.py                # A2A orchestration client
├── client_requirements.txt  # Client dependencies
└── README.md               # This file
```

### Extension Points

- Add more agent capabilities
- Implement streaming responses
- Add authentication mechanisms
- Create more complex multi-agent workflows
- Add database integration for task persistence

## 📄 License

This project is part of an educational assignment demonstrating A2A protocol implementation.

---

**🎓 Assignment**: nFactorial AI Homework 1.3 - Multi-Agent Systems  
**🔗 Protocol**: Agent-to-Agent (A2A) Communication Standard 