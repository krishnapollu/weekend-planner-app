"""
Planner Agent - Decides which activity categories to search for.
This agent takes parsed user input and creates a search strategy.
"""

from crewai import Agent, Task, LLM
from langchain_openai import ChatOpenAI
import os
import json


def create_planner_agent() -> Agent:
    """Create the Planner Agent that decides what to search for"""
    
    # Choose LLM based on available API keys
    if os.getenv('GOOGLE_API_KEY'):
        llm = LLM(model="gemini-2.0-flash")  # LiteLLM uses GEMINI_API_KEY env var
    elif os.getenv('OPENAI_API_KEY'):
        llm = LLM(model="gpt-4-turbo-preview", api_key=os.getenv('OPENAI_API_KEY'))
    else:
        raise ValueError("No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY")
    
    agent = Agent(
        role='Activity Planning Strategist',
        goal='Determine the best activity categories to search based on user preferences',
        backstory="""You are an experienced event planner who knows how to create 
        balanced, enjoyable itineraries. You understand which activities complement 
        each other and how to sequence them for the best experience. You consider 
        timing, location, and user preferences when planning.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


def create_planner_task(agent: Agent, parsed_input: dict) -> Task:
    """Create a task for the Planner Agent"""
    
    task = Task(
        description=f"""
        Based on the user's structured request, create a search strategy for activities.
        
        User Request:
        - Date: {parsed_input.get('date', 'not specified')}
        - Location: {parsed_input.get('location', 'not specified')}
        - Interests: {', '.join(parsed_input.get('interests', []))}
        - Context: {parsed_input.get('context', 'none')}
        
        Analyze this information and decide which activity categories should be searched.
        Available categories:
        - restaurants: For dining experiences
        - movies: For film entertainment
        - events: For local events, concerts, festivals
        - outdoor: For parks, trails, outdoor activities
        
        Consider:
        1. What categories match the user's stated interests?
        2. What categories would create a balanced day/evening?
        3. What makes sense for the time of day/week mentioned?
        4. Should we prioritize certain categories?
        
        Return ONLY a valid JSON object with this structure:
        {{
            "categories": ["category1", "category2", ...],
            "priority": "which category to emphasize (optional)",
            "reasoning": "brief explanation of strategy"
        }}
        
        Do not include markdown formatting or additional text.
        """,
        agent=agent,
        expected_output="A JSON object with categories, priority, and reasoning"
    )
    
    return task


def plan_search_strategy(parsed_input: dict) -> dict:
    """
    Convenience function to create a search strategy.
    Can be used standalone without running the full crew.
    """
    agent = create_planner_agent()
    task = create_planner_task(agent, parsed_input)
    
    # Execute task
    result = agent.execute_task(task)
    
    # Try to parse JSON from result
    try:
        result_str = str(result)
        if '```json' in result_str:
            result_str = result_str.split('```json')[1].split('```')[0].strip()
        elif '```' in result_str:
            result_str = result_str.split('```')[1].split('```')[0].strip()
        
        parsed = json.loads(result_str)
        return parsed
    except json.JSONDecodeError:
        # Fallback: use interests from input
        interests = parsed_input.get('interests', [])
        categories = []
        
        # Map interests to categories
        if any(i in ['dinner', 'restaurant', 'food'] for i in interests):
            categories.append('restaurants')
        if any(i in ['movie', 'film', 'cinema'] for i in interests):
            categories.append('movies')
        if any(i in ['event', 'concert', 'festival'] for i in interests):
            categories.append('events')
        if any(i in ['outdoor', 'park', 'nature', 'hiking'] for i in interests):
            categories.append('outdoor')
        
        # Default if nothing matched
        if not categories:
            categories = ['restaurants', 'outdoor']
        
        return {
            "categories": categories,
            "priority": categories[0] if categories else "restaurants",
            "reasoning": "Fallback strategy based on stated interests"
        }
