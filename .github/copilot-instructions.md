You are an expert Python engineer using the CrewAI framework. Build a multi-agent AI app called "AI Planner Assistant" that helps users plan activities (restaurants, movies, outdoor trips, and events) for a given date, time, and location.

Requirements:
- Framework: CrewAI
- Language: Python 3.10+
- Data: Use real API calls (Google Places API, Eventbrite API, TMDb API, or free open APIs) for discovery.
- Output: A friendly text itinerary printed to console.
- Agents: 5 agents coordinated by one Crew.

Define the following agents:

1. Chat Agent
   - Extracts structured info (date, time, location, interests) from user text input.
   - Output JSON like: {"date": "Saturday", "location": "Austin", "interests": ["dinner", "outdoor"]}

2. Planner Agent
   - Takes parsed info and decides which categories to search for (restaurants, movies, events, outdoor spots).

3. Discovery Agent
   - Uses real APIs to fetch 3-5 results per category for the given location and date.
   - Each result: {"name": "Zilker Park", "type": "outdoor", "rating": 4.7, "details": "Scenic park with trails."}

4. Curator Agent
   - Filters and ranks top 3 options overall based on interest match, rating, and variety.

5. Summarizer Agent
   - Generates a natural language itinerary combining curated results (friendly tone).

Define a single orchestrator script that wires all agents together into a Crew pipeline:
- Input: Free-text user query
- Output: Printed text itinerary.

Example main flow:

from crewai import Agent, Task, Crew
from agents.chat_agent import chat_task
from agents.planner_agent import planner_task
from agents.discovery_agent import discovery_task
from agents.curator_agent import curator_task
from agents.summarizer_agent import summarizer_task

crew = Crew(agents=[
    Agent(role="Chat", task=chat_task),
    Agent(role="Planner", task=planner_task),
    Agent(role="Discovery", task=discovery_task),
    Agent(role="Curator", task=curator_task),
    Agent(role="Summarizer", task=summarizer_task),
])

if __name__ == "__main__":
    user_input = "Plan something fun for me this Saturday in Austin, maybe outdoors and dinner."
    final_plan = crew.run(input=user_input)
    print(final_plan)

Keep each agent in its own file under /agents directory and define its logic using CrewAI Tasks.
Use OpenAI or Gemini API calls within Discovery Agent for reasoning if needed.
All agents should exchange structured JSON.
Focus on clean modular design, no placeholders, and minimal dependencies (crewai, requests, python-dotenv).
Goal: Produce a working end-to-end itinerary generator using real data sources with CrewAI orchestration.
