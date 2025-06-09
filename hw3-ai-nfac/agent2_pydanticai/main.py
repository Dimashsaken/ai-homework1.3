import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PydanticAI Agent 2 - Text Refinement")


class RefinementInput(BaseModel):
    original_text: str = Field(description="The original text to refine and summarize")


class RefinementOutput(BaseModel):
    summary: str = Field(description="A concise summary of the main points")
    key_insights: List[str] = Field(
        description="List of key insights extracted from the text"
    )
    cleaned_text: str = Field(
        description="The original text with unnecessary sections removed"
    )
    word_count_reduction: str = Field(
        description="Information about how much the text was reduced"
    )


# A2A Protocol models
class MessagePart(BaseModel):
    content: str


class Message(BaseModel):
    role: str
    parts: List[MessagePart]


class TaskRequest(BaseModel):
    task_id: str
    messages: List[Message]


class TaskResponse(BaseModel):
    task_id: str
    status: str
    messages: List[Message]


# Initialize PydanticAI agent for text refinement
def initialize_pydantic_agent():
    """Initialize the PydanticAI agent for text refinement"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        # Create Google model using the API key through environment variable
        # PydanticAI will automatically use GOOGLE_API_KEY from environment
        model = GoogleModel("gemini-2.0-flash-lite")

        # Create PydanticAI agent
        agent = Agent(
            model=model,
            result_type=RefinementOutput,
            system_prompt="""
            You are a text refinement specialist. Your job is to:
            1. Create a concise summary of the main points (50-100 words)
            2. Extract 3-5 key insights as bullet points
            3. Clean up the text by removing unnecessary verbosity and redundancy
            4. Calculate and report the word count reduction
            
            Focus on preserving the core technical content while making it more digestible.
            Remove meta-commentary about the analysis itself and focus on the actual insights.
            """,
        )

        print("✅ PydanticAI agent initialized successfully")
        return agent

    except Exception as e:
        print(f"❌ Error initializing PydanticAI agent: {e}")
        return None


async def refine_text(agent: Agent, original_text: str) -> RefinementOutput:
    """Refine and summarize the given text using PydanticAI"""
    try:
        original_word_count = len(original_text.split())

        # Use PydanticAI to process the text
        result = await agent.run(
            f"Please refine and summarize this text: {original_text}"
        )

        # Access the structured output from result.output
        refinement_output = result.output

        # Calculate word count for cleaned text
        cleaned_word_count = len(refinement_output.cleaned_text.split())
        reduction_percentage = (
            (original_word_count - cleaned_word_count) / original_word_count
        ) * 100
        
        # Create a new RefinementOutput with updated word count reduction info
        return RefinementOutput(
            summary=refinement_output.summary,
            key_insights=refinement_output.key_insights,
            cleaned_text=refinement_output.cleaned_text,
            word_count_reduction=f"Reduced from {original_word_count} to {cleaned_word_count} words ({reduction_percentage:.1f}% reduction)",
        )

    except Exception as e:
        # Return a fallback response if processing fails
        return RefinementOutput(
            summary="Error processing the text for refinement.",
            key_insights=["Processing failed due to technical issues"],
            cleaned_text=(
                original_text[:500] + "..."
                if len(original_text) > 500
                else original_text
            ),
            word_count_reduction=f"Original text: {len(original_text.split())} words (no reduction applied due to error)",
        )


# Initialize the PydanticAI agent at startup
pydantic_agent = initialize_pydantic_agent()


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Return the agent card for A2A protocol discovery"""
    return {
        "schemaVersion": "1.0",
        "agentId": "agent2-pydanticai",
        "name": "PydanticAI Agent 2 - Text Refinement",
        "description": "Refines and summarizes text using PydanticAI",
        "handler": {"type": "http", "url": "http://localhost:8002/tasks/send"},
        "capabilities": [
            {
                "type": "skill",
                "name": "text-refinement",
                "description": "Refines, summarizes and extracts key insights from text",
            }
        ],
        "auth": {"type": "none"},
    }


@app.post("/tasks/send", response_model=TaskResponse)
async def handle_task(request: TaskRequest):
    """Handle incoming A2A task requests"""
    try:
        # Extract required fields from A2A request
        task_id = request.task_id
        messages = request.messages

        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get the last message
        last_message = messages[-1]
        if last_message.role != "user":
            raise HTTPException(
                status_code=400, detail="Last message must be from user"
            )

        if not last_message.parts:
            raise HTTPException(status_code=400, detail="No message parts found")

        # Extract the text content from the message
        content = last_message.parts[0].content

        if not content.strip():
            raise HTTPException(status_code=400, detail="No content to refine")

        print(
            f"🔍 Processing text refinement request for {len(content.split())} words..."
        )

        # Check if PydanticAI agent is available
        if not pydantic_agent:
            raise HTTPException(
                status_code=500, detail="PydanticAI agent not initialized"
            )  # Refine the text using PydanticAI
        refinement_output = await refine_text(pydantic_agent, content)

        print(f"✅ Text refinement completed successfully")

        # Create A2A response with JSON output
        response_message = Message(
            role="agent",
            parts=[MessagePart(content=refinement_output.model_dump_json())],
        )

        return TaskResponse(
            task_id=task_id,
            status="completed",
            messages=[response_message],
        )

    except Exception as e:
        print(f"❌ Text refinement failed: {str(e)}")
        error_message = Message(
            role="agent",
            parts=[MessagePart(content=f"Text refinement failed: {str(e)}")],
        )

        return TaskResponse(
            task_id=request.task_id,
            status="failed",
            messages=[error_message],
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "pydanticai-agent-2"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
