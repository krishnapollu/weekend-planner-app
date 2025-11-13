"""
Curator Agent - Filters and ranks activity options.
This agent evaluates discovered activities and selects the best ones.
"""

from crewai import Agent, Task, LLM
from langchain_openai import ChatOpenAI
import os
import json
from typing import List, Dict


def create_curator_agent() -> Agent:
    """Create the Curator Agent that filters and ranks results"""
    
    # Choose LLM based on available API keys
    if os.getenv('GOOGLE_API_KEY'):
        llm = LLM(model="gemini-2.0-flash")  # LiteLLM uses GEMINI_API_KEY env var
    elif os.getenv('OPENAI_API_KEY'):
        llm = LLM(model="gpt-4-turbo-preview", api_key=os.getenv('OPENAI_API_KEY'))
    else:
        raise ValueError("No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY")
    
    agent = Agent(
        role='Experience Curator',
        goal='Select and rank the best activity options for a balanced itinerary',
        backstory="""You are a discerning curator with excellent taste. You know 
        how to evaluate activities based on quality, ratings, variety, and user 
        preferences. You create balanced experiences that flow well together and 
        match what the user is looking for.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


def create_curator_task(agent: Agent, discovered_activities: List[Dict], parsed_input: dict) -> Task:
    """Create a task for the Curator Agent"""
    
    interests = parsed_input.get('interests', [])
    context = parsed_input.get('context', '')
    location = parsed_input.get('location', 'the requested location')
    
    task = Task(
        description=f"""
        Review the following discovered activities and select the TOP 3-5 best options
        for the user's itinerary.
        
        LOCATION: {location}
        User Interests: {', '.join(interests)}
        Context: {context}
        
        Discovered Activities:
        {json.dumps(discovered_activities, indent=2)}
        
        CRITICAL: Verify ALL selected activities (except movies) are actually located in {location}.
        If any activity appears to be from a different city, DO NOT select it.
        
        Evaluation criteria:
        1. LOCATION ACCURACY - Must be in {location} (except movies)
        2. Match with user interests
        3. Rating/quality (prioritize 4+ stars)
        4. Variety (don't pick all the same type)
        5. Logical flow (activities that work well together)
        6. Weather considerations if available
        
        Return ONLY a JSON object with this structure:
        {{
            "selected": [
                {{
                    "name": "activity name",
                    "type": "activity type",
                    "rating": rating,
                    "details": "description",
                    "reason": "why this was selected"
                }}
            ],
            "curation_notes": "brief explanation of selections"
        }}
        
        Do not include markdown formatting.
        """,
        agent=agent,
        expected_output="JSON object with selected activities and curation notes"
    )
    
    return task


def curate_activities(discovered_activities: List[Dict], parsed_input: dict) -> dict:
    """
    Curate activities using the LLM agent.
    Returns the top selected activities with reasoning.
    """
    if not discovered_activities:
        return {
            "selected": [],
            "curation_notes": "No activities found to curate."
        }
    
    agent = create_curator_agent()
    task = create_curator_task(agent, discovered_activities, parsed_input)
    
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
        # Fallback: simple rating-based curation
        print("⚠️  Curator LLM failed, using fallback curation")
        
        # Sort by rating and take top 5
        sorted_activities = sorted(
            discovered_activities,
            key=lambda x: x.get('rating', 0),
            reverse=True
        )
        
        # Ensure variety - one of each type if possible
        selected = []
        types_seen = set()
        
        for activity in sorted_activities:
            activity_type = activity.get('type')
            if activity_type not in types_seen or len(selected) < 3:
                selected.append(activity)
                types_seen.add(activity_type)
                if len(selected) >= 5:
                    break
        
        return {
            "selected": selected,
            "curation_notes": "Curated based on ratings and variety"
        }
