import asyncio
import json
import uuid
import httpx
from typing import Dict, Any


class A2AClient:
    """Client for interacting with A2A protocol agents"""

    def __init__(self):
        self.agent1_url = "http://localhost:8001"
        self.agent2_url = "http://localhost:8002"

    async def fetch_agent_card(self, base_url: str) -> Dict[str, Any]:
        """Fetch agent card from agent's well-known endpoint"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{base_url}/.well-known/agent.json")
            response.raise_for_status()
            return response.json()

    async def send_task(
        self, agent_url: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a task to an agent"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{agent_url}/tasks/send", json=task_data)
            response.raise_for_status()
            return response.json()

    async def run_agent_workflow(self):
        """Run the complete agent-to-agent workflow"""
        try:
            print("🚀 Starting A2A Multi-Agent Workflow")
            print("=" * 50)

            # Step 1: Fetch agent cards
            print("📋 Fetching agent cards...")
            agent1_card = await self.fetch_agent_card(self.agent1_url)
            agent2_card = await self.fetch_agent_card(self.agent2_url)

            print(f"✅ Agent 1: {agent1_card['name']} - {agent1_card['description']}")
            print(f"✅ Agent 2: {agent2_card['name']} - {agent2_card['description']}")
            print()

            # Step 2: Send task to Agent 1 (LangChain text analysis)
            print("🔍 Sending text analysis task to Agent 1...")
            task_id = str(uuid.uuid4())

            agent1_task = {
                "task_id": task_id,
                "messages": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "content": "Describe the key trends in AI, focusing on recent developments in large language models, retrieval-augmented generation, and multi-agent systems. Discuss their implications for the future of artificial intelligence."
                            }
                        ],
                    }
                ],
                "use_stream": False,
            }

            agent1_response = await self.send_task(self.agent1_url, agent1_task)

            if agent1_response["status"] != "completed":
                print(f"❌ Agent 1 task failed: {agent1_response}")
                return

            # Extract analysis result
            analysis_result = agent1_response["messages"][0]["parts"][0]["content"]
            print(f"✅ Agent 1 Analysis Complete")
            print(f"📝 Analysis Preview: {analysis_result[:200]}...")
            print()

            # Step 3: Send analysis result to Agent 2 for text refinement
            print("✨ Sending analysis to Agent 2 for text refinement...")

            agent2_task = {
                "task_id": str(uuid.uuid4()),
                "messages": [{"role": "user", "parts": [{"content": analysis_result}]}],
            }

            agent2_response = await self.send_task(self.agent2_url, agent2_task)

            if agent2_response["status"] != "completed":
                print(f"❌ Agent 2 task failed: {agent2_response}")
                return

            # Extract and parse refinement output
            refinement_output_json = agent2_response["messages"][0]["parts"][0][
                "content"
            ]
            refinement_output = json.loads(refinement_output_json)

            print("✅ Agent 2 Text Refinement Complete")
            print()
            print("=" * 50)
            print("📊 FINAL RESULTS")
            print("=" * 50)

            print("\n🤖 Agent 1 Analysis:")
            print("-" * 30)
            print(analysis_result)

            print("\n✨ Agent 2 Text Refinement:")
            print("-" * 30)
            print(f"📝 Summary: {refinement_output['summary']}")
            print(f"\n💡 Key Insights:")
            for i, insight in enumerate(refinement_output["key_insights"], 1):
                print(f"  {i}. {insight}")
            print(f"\n📊 {refinement_output['word_count_reduction']}")
            print(f"\n🔧 Cleaned Text:")
            print(refinement_output["cleaned_text"])

            print("\n" + "=" * 50)
            print("✅ Multi-Agent Workflow Completed Successfully!")

        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            import traceback

            traceback.print_exc()


async def main():
    """Main function to run the A2A client"""
    print("🌟 A2A Multi-Agent System Client")
    print("Agent 1 (LangChain): Text Analysis → Agent 2 (PydanticAI): Text Refinement")
    print()

    client = A2AClient()
    await client.run_agent_workflow()


if __name__ == "__main__":
    asyncio.run(main())
