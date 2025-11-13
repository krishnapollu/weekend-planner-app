"""
Chat Agent - Extracts structured information from user input.
This agent parses natural language requests and outputs structured JSON.
"""

from crewai import Agent, Task, LLM
from langchain_openai import ChatOpenAI
import os
import json


def create_chat_agent() -> Agent:
    """Create the Chat Agent that parses user input"""
    
    # Choose LLM based on available API keys - use CrewAI's LLM class directly
    if os.getenv('GOOGLE_API_KEY'):
        # Use Gemini Pro with explicit provider prefix
        llm = LLM(model="gemini-2.0-flash")
    elif os.getenv('OPENAI_API_KEY'):
        llm = LLM(model="gpt-4-turbo-preview", api_key=os.getenv('OPENAI_API_KEY'))
    else:
        raise ValueError("No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY")
    
    agent = Agent(
        role='Chat Interface Specialist',
        goal='Extract and structure user intent from natural language input',
        backstory="""You are an expert at understanding user requests and extracting 
        key information. You excel at identifying dates, locations, preferences, and 
        interests from casual conversation. You always respond with well-structured JSON.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


def create_chat_task(agent: Agent, user_input: str) -> Task:
    """Create a task for the Chat Agent"""
    
    task = Task(
        description=f"""
        Analyze the following user input and extract structured information:
        
        User Input: "{user_input}"
        
        Extract the following information:
        1. Date/Time: When does the user want to do these activities? (e.g., "Saturday", "this weekend", "tomorrow")
        2. Location: Where is the user looking for activities? (EXACT city name mentioned by user)
        3. Interests: What types of activities is the user interested in? 
           Choose from: dinner, restaurant, outdoor, movie, event, entertainment
        4. Additional context: Any specific preferences mentioned (budget, mood, group size, etc.)
        
        CRITICAL FOR LOCATION:
        - Extract the EXACT city name mentioned by the user
        - Do NOT default to New York or any other city if not mentioned
        - Examples: "Austin" from "Austin, Texas", "Atlanta" from "in Atlanta", "Seattle" from "near Seattle"
        - If truly no location mentioned, use "not specified"
        
        IMPORTANT: Return ONLY a valid JSON object with this exact structure:
        {{
            "date": "extracted date or 'not specified'",
            "location": "EXACT city name from user input or 'not specified'",
            "interests": ["list", "of", "interests"],
            "context": "any additional relevant information"
        }}
        
        Do not include any explanation, markdown formatting, or additional text.
        """,
        agent=agent,
        expected_output="A JSON object with date, location, interests, and context fields"
    )
    
    return task


def parse_user_input(user_input: str) -> dict:
    """
    Convenience function to parse user input and return structured data.
    Can be used standalone without running the full crew.
    """
    agent = create_chat_agent()
    task = create_chat_task(agent, user_input)
    
    # Execute task
    result = agent.execute_task(task)
    
    # Try to parse JSON from result
    try:
        # Clean up the result if it has markdown formatting
        result_str = str(result)
        if '```json' in result_str:
            result_str = result_str.split('```json')[1].split('```')[0].strip()
        elif '```' in result_str:
            result_str = result_str.split('```')[1].split('```')[0].strip()
        
        parsed = json.loads(result_str)
        return parsed
    except json.JSONDecodeError:
        # Fallback parsing
        return {
            "date": "not specified",
            "location": "not specified",
            "interests": ["general"],
            "context": user_input
        }
