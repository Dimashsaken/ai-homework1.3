import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LangChain Agent 1")


# Pydantic models for A2A protocol
class MessagePart(BaseModel):
    content: str


class Message(BaseModel):
    role: str
    parts: List[MessagePart]


class TaskRequest(BaseModel):
    task_id: str
    messages: List[Message]
    use_stream: bool = False


class TaskResponse(BaseModel):
    task_id: str
    status: str
    messages: List[Message]


# Initialize LangChain components
def initialize_langchain():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite", temperature=0.7, google_api_key=api_key
    )

    return llm


# Initialize the LangChain LLM at startup
try:
    llm = initialize_langchain()
    print("✅ LangChain initialized successfully")
except Exception as e:
    print(f"❌ Warning: Failed to initialize LangChain: {e}")
    llm = None


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Return the agent card for A2A protocol discovery"""
    return {
        "schemaVersion": "1.0",
        "agentId": "agent1-langchain",
        "name": "LangChain Agent 1",
        "description": "Analyzes text inputs via LangChain LLM",
        "handler": {"type": "http", "url": "http://localhost:8001/tasks/send"},
        "capabilities": [
            {
                "type": "skill",
                "name": "text-analysis",
                "description": "Performs brief text analysis",
            }
        ],
        "auth": {"type": "none"},
    }


@app.post("/tasks/send", response_model=TaskResponse)
async def handle_task(request: TaskRequest):
    """Handle incoming A2A task requests"""
    try:
        if not llm:
            raise HTTPException(
                status_code=500, detail="LangChain not properly initialized"
            )

        # Extract text content from the last user message
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        last_message = request.messages[-1]
        if last_message.role != "user":
            raise HTTPException(
                status_code=400, detail="Last message must be from user"
            )

        # Combine all content parts into a single string
        combined_text = " ".join([part.content for part in last_message.parts])

        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text content to analyze")

        # Create analysis prompt
        analysis_prompt = f"""
        Analyze the following text and provide a comprehensive analysis including:
        1. Key themes and topics
        2. Sentiment and tone
        3. Main insights or conclusions
        4. Potential areas for further investigation
        
        Text to analyze:
        {combined_text}
        
        Analysis:
        """

        print(f"🔍 Processing analysis request for text: {combined_text[:100]}...")

        # Run LangChain analysis
        analysis_result = llm.invoke(analysis_prompt)

        # Extract the content from the response
        if hasattr(analysis_result, "content"):
            analysis_text = analysis_result.content
        elif isinstance(analysis_result, dict) and "text" in analysis_result:
            analysis_text = analysis_result["text"]
        else:
            analysis_text = str(analysis_result)

        print(f"✅ Analysis completed successfully")

        # Create response
        response_message = Message(
            role="agent", parts=[MessagePart(content=analysis_text)]
        )

        return TaskResponse(
            task_id=request.task_id, status="completed", messages=[response_message]
        )

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        error_message = Message(
            role="agent", parts=[MessagePart(content=f"Analysis failed: {str(e)}")]
        )

        return TaskResponse(
            task_id=request.task_id, status="failed", messages=[error_message]
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if llm else "unhealthy"
    return {
        "status": status,
        "agent": "langchain-agent-1",
        "llm_initialized": llm is not None,
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting LangChain Agent 1 on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
