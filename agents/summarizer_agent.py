"""
Summarizer Agent - Generates natural language itineraries.
This agent creates friendly, readable summaries of the curated activities.
"""

from crewai import Agent, Task, LLM
from langchain_openai import ChatOpenAI
import os
import json
from typing import Dict


def create_summarizer_agent() -> Agent:
    """Create the Summarizer Agent that generates itineraries"""
    
    # Choose LLM based on available API keys
    if os.getenv('GOOGLE_API_KEY'):
        llm = LLM(model="gemini-2.0-flash")  # LiteLLM uses GEMINI_API_KEY env var
    elif os.getenv('OPENAI_API_KEY'):
        llm = LLM(model="gpt-4-turbo-preview", api_key=os.getenv('OPENAI_API_KEY'))
    else:
        raise ValueError("No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY")
    
    agent = Agent(
        role='Itinerary Writer',
        goal='Create engaging, friendly itineraries from curated activities',
        backstory="""You are a talented travel writer who creates exciting, 
        easy-to-follow itineraries. You write in a warm, enthusiastic tone that 
        makes people excited about their plans. You organize information clearly 
        and include all the important details.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


def create_summarizer_task(agent: Agent, curated_data: dict, parsed_input: dict) -> Task:
    """Create a task for the Summarizer Agent"""
    
    location = parsed_input.get('location', 'your area')
    date = parsed_input.get('date', 'your chosen date')
    
    task = Task(
        description=f"""
        Create a friendly, engaging itinerary based on these curated activities.
        
        Location: {location}
        Date: {date}
        
        Curated Activities:
        {json.dumps(curated_data.get('selected', []), indent=2)}
        
        Curation Notes: {curated_data.get('curation_notes', '')}
        
        Write a natural, conversational itinerary that includes:
        1. A welcoming introduction
        2. Each activity with:
           - Name and type (use emojis!)
           - Rating if available
           - Brief description
           - Why it's a great choice
        3. A friendly closing with any final tips
        
        Tone: Warm, enthusiastic, helpful
        Length: 200-300 words
        Format: Use bullet points or numbered list
        
        Do NOT return JSON. Return a friendly text itinerary ready to present to the user.
        """,
        agent=agent,
        expected_output="A friendly, natural language itinerary text (not JSON)"
    )
    
    return task


def generate_itinerary(curated_data: dict, parsed_input: dict) -> str:
    """
    Generate a natural language itinerary from curated activities.
    Returns a friendly text summary.
    """
    # Check if we have activities
    selected = curated_data.get('selected', [])
    print(f"\n📝 Summarizer received {len(selected)} activities")
    print(f"Curated data type: {type(curated_data)}")
    print(f"Selected type: {type(selected)}")
    
    if not selected or len(selected) == 0:
        return """
I couldn't find enough activities to create an itinerary for your request. 
This might be because:
- The location wasn't recognized
- API keys aren't configured
- No activities matched your criteria

Please try again with a different location or check your API configuration.
"""
    
    # Try using the LLM agent first
    try:
        agent = create_summarizer_agent()
        task = create_summarizer_task(agent, curated_data, parsed_input)
        
        # Execute task
        result = agent.execute_task(task)
        return str(result)
    except Exception as e:
        print(f"⚠️  Summarizer LLM failed: {e}, using fallback")
        # Use fallback if agent fails
        return generate_simple_itinerary(curated_data, parsed_input)


def generate_simple_itinerary(curated_data: dict, parsed_input: dict) -> str:
    """
    Fallback function to generate a simple itinerary without LLM.
    """
    location = parsed_input.get('location', 'your area')
    date = parsed_input.get('date', 'your chosen date')
    selected = curated_data.get('selected', [])
    
    if not selected:
        return "No activities found. Please try a different location or criteria."
    
    # Build simple text itinerary
    lines = [
        f"🎉 Your Weekend Plan for {date} in {location}",
        "=" * 50,
        ""
    ]
    
    for i, activity in enumerate(selected, 1):
        emoji_map = {
            'restaurant': '🍽️',
            'outdoor': '🌳',
            'movie': '🎬',
            'event': '🎫',
            'weather': '🌤️'
        }
        emoji = emoji_map.get(activity.get('type', ''), '📍')
        
        lines.append(f"{i}. {emoji} {activity.get('name', 'Unknown')}")
        
        rating = activity.get('rating', 0)
        if rating and rating > 0:
            stars = '⭐' * int(rating)
            lines.append(f"   Rating: {stars} ({rating}/5)")
        
        details = activity.get('details', '')
        if details:
            # Truncate long details
            if len(details) > 150:
                details = details[:150] + "..."
            lines.append(f"   {details}")
        
        lines.append("")
    
    notes = curated_data.get('curation_notes', '')
    if notes:
        lines.append(f"💡 Tip: {notes}")
    
    lines.append("\nHave a great time! 🎊")
    
    return "\n".join(lines)
