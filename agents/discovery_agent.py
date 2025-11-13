"""
Discovery Agent - Uses LLM to generate realistic activity recommendations.
No external APIs - pure LLM reasoning based on location and date knowledge.
"""

from crewai import Agent, Task, LLM
import os
import json
from typing import List, Dict


def create_discovery_agent() -> Agent:
    """Create the Discovery Agent that uses LLM reasoning"""
    
    if not os.getenv('GOOGLE_API_KEY'):
        raise ValueError("GOOGLE_API_KEY is required for LLM-based discovery")
    
    llm = LLM(model="gemini-2.0-flash")
    
    agent = Agent(
        role='Local Activity Expert',
        goal='Generate realistic, contextual recommendations for activities based on your extensive knowledge of locations worldwide',
        backstory="""You are a well-traveled local expert with deep knowledge of restaurants, 
        entertainment, outdoor activities, and events across the world. You provide genuine recommendations 
        based on your knowledge of popular spots, current movies, seasonal activities, and local favorites. 
        Your suggestions are always realistic, well-rated, and appropriate for the location and season.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


def create_discovery_task(agent: Agent, search_strategy: dict, parsed_input: dict) -> Task:
    """Create a task for the Discovery Agent"""
    
    location = parsed_input.get('location', 'local area')
    date = parsed_input.get('date', 'this weekend')
    interests = parsed_input.get('interests', [])
    categories = search_strategy.get('categories', [])
    
    task = Task(
        description=f"""
        Based on your knowledge, recommend realistic activities for {location} on {date}.
        
        User interests: {', '.join(interests) if interests else 'general'}
        Categories to search: {', '.join(categories)}
        
        For each category, suggest 3-5 REAL places/activities that actually exist:
        
        - RESTAURANTS: Popular local restaurants with real names (not generic like "Restaurant #1")
        - MOVIES: Current or recent movies showing in theaters (2024-2025)
        - OUTDOOR: Parks, trails, landmarks that exist in {location}
        - EVENTS: Seasonal events, festivals, or activities typical for {location} in {date}
        
        For EACH activity provide:
        - name: Real, specific name (e.g., "Eiffel Tower", "Louvre Museum", "Le Cinq Restaurant")
        - type: One of [restaurant, movie, outdoor, event]
        - rating: Realistic rating 3.5-5.0 stars
        - details: Brief description (cuisine type, movie genre, activity description)
        
        IMPORTANT: Use your knowledge of {location}. Suggest places tourists actually visit or locals actually recommend.
        Do NOT make up generic names. Think about what you know about {location}.
        
        Return ONLY a valid JSON array. Example format:
        [
          {{"name": "Louvre Museum", "type": "outdoor", "rating": 4.8, "details": "World's largest art museum with iconic glass pyramid"}},
          {{"name": "Le Jules Verne", "type": "restaurant", "rating": 4.6, "details": "Michelin-starred French cuisine in the Eiffel Tower"}},
          {{"name": "Dune: Part Two", "type": "movie", "rating": 4.7, "details": "Epic sci-fi sequel continuing Paul Atreides' journey"}}
        ]
        """,
        agent=agent,
        expected_output="JSON array of activity objects with name, type, rating, and details"
    )
    
    return task


def discover_activities(parsed_input: dict, search_strategy: dict) -> List[Dict]:
    """
    Main function to discover activities using LLM reasoning.
    Calls LLM with structured prompt to generate realistic recommendations.
    """
    location = parsed_input.get('location', 'New York')
    date = parsed_input.get('date', 'this weekend')
    interests = parsed_input.get('interests', [])
    categories = search_strategy.get('categories', [])
    
    print(f"\n🔍 Generating activity recommendations for {location}...")
    
    # Initialize LLM
    llm = LLM(model="gemini-2.0-flash")
    
    # Build comprehensive prompt with strict location validation
    prompt = f"""You are a local expert SPECIFICALLY for {location}. Based on your knowledge, recommend realistic activities for {date}.

CRITICAL REQUIREMENT: ALL recommendations MUST be located in or immediately near {location}. 
Do NOT suggest places from other cities like New York, Los Angeles, San Francisco, etc.
Focus ONLY on what exists in {location}.

Categories: {', '.join(categories)}
User interests: {', '.join(interests) if interests else 'general fun'}

Provide 3-5 REAL recommendations per category that actually exist in or near {location}:

RESTAURANTS: Suggest actual popular restaurants, cafes, or dining spots in {location}
MOVIES: List current movies in theaters (2024-2025 releases) - these can be anywhere
OUTDOOR: Recommend real parks, landmarks, trails, or outdoor venues specifically in {location}
EVENTS: Suggest seasonal activities, festivals, or events typical for {location} during {date}

For each activity return JSON with:
- name: Specific real name (NOT "Local Restaurant #1" or generic names)
- type: restaurant/movie/outdoor/event
- rating: 3.5-5.0 stars
- details: Brief description that includes location context

VALIDATION: Before finalizing, verify each restaurant/outdoor/event is actually in {location}.
Remove any suggestions from other cities.

Think about what {location} is actually known for. What would a local in {location} recommend?

Return ONLY a JSON array with NO additional text:
[
  {{"name": "Real Place Name", "type": "restaurant", "rating": 4.5, "details": "Description including location"}},
  ...
]"""

    # Call LLM
    try:
        response = llm.call(messages=[{"role": "user", "content": prompt}])
        
        # Parse response
        response_text = response.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        activities = json.loads(response_text)
        
        print(f"✓ Generated {len(activities)} activity recommendations\n")
        return activities
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {e}")
        print(f"Response was: {response_text[:200]}...")
        # Return minimal fallback
        return [{
            "name": f"Explore {location}",
            "type": "outdoor",
            "rating": 4.5,
            "details": f"Discover the local attractions and activities in {location}"
        }]
    except Exception as e:
        print(f"⚠️  Error generating recommendations: {e}")
        return []


def format_discovery_results(results: List[Dict]) -> str:
    """Format discovery results as JSON string"""
    return json.dumps(results, indent=2)
