"""
Weekend Planner Crew - CrewAI decorator-based implementation
Clean, maintainable multi-agent system for activity planning
"""

from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew
import os
import sys
import json
import ssl
import httpx
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Gemini API key for LiteLLM
if os.getenv('GOOGLE_API_KEY'):
    os.environ['GEMINI_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Disable SSL verification for Windows certificate issues
os.environ['SSL_VERIFY'] = 'False'
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['HTTPX_VERIFY_SSL'] = 'false'
ssl._create_default_https_context = ssl._create_unverified_context

# Monkey-patch httpx to disable SSL verification globally
original_client_init = httpx.Client.__init__

def patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_client_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_client_init

# Add parent directory to path
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from config.config_loader import config


@CrewBase
class WeekendPlannerCrew:
    """
    Weekend Planner multi-agent system.
    Uses 5 specialized agents to create personalized weekend itineraries.
    """
    
    def __init__(self, step_callback=None):
        """Initialize LLM for all agents
        
        Args:
            step_callback: Optional callback function(agent_name: str, status: str) 
                          Called when agent starts/completes. status: 'active' or 'completed'
        """
        if os.getenv('GOOGLE_API_KEY'):
            self.llm = LLM(model="gemini-2.0-flash")
        elif os.getenv('OPENAI_API_KEY'):
            self.llm = LLM(model="gpt-4-turbo-preview", api_key=os.getenv('OPENAI_API_KEY'))
        else:
            raise ValueError("No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY")
        self.step_callback = step_callback
    
    # ========================
    # AGENTS
    # ========================
    
    @agent
    def chat_agent(self) -> Agent:
        """Chat Interface Specialist - Extracts structured info from user input"""
        agent_config = config.get_agent_config('chat_agent')
        return Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=self.llm,
            verbose=agent_config.get('verbose', True),
            allow_delegation=agent_config.get('allow_delegation', False)
        )
    
    @agent
    def planner_agent(self) -> Agent:
        """Activity Planning Strategist - Decides which categories to search"""
        agent_config = config.get_agent_config('planner_agent')
        return Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=self.llm,
            verbose=agent_config.get('verbose', True),
            allow_delegation=agent_config.get('allow_delegation', False)
        )
    
    @agent
    def discovery_agent(self) -> Agent:
        """Local Activity Expert - Generates realistic recommendations"""
        agent_config = config.get_agent_config('discovery_agent')
        return Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=self.llm,
            verbose=agent_config.get('verbose', True),
            allow_delegation=agent_config.get('allow_delegation', False)
        )
    
    @agent
    def curator_agent(self) -> Agent:
        """Experience Curator - Filters and ranks best options"""
        agent_config = config.get_agent_config('curator_agent')
        return Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=self.llm,
            verbose=agent_config.get('verbose', True),
            allow_delegation=agent_config.get('allow_delegation', False)
        )
    
    @agent
    def summarizer_agent(self) -> Agent:
        """Itinerary Writer - Creates friendly, engaging summaries"""
        agent_config = config.get_agent_config('summarizer_agent')
        return Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=self.llm,
            verbose=agent_config.get('verbose', True),
            allow_delegation=agent_config.get('allow_delegation', False)
        )
    
    # ========================
    # TASKS
    # ========================
    
    @task
    def parse_task(self) -> Task:
        """Parse and structure user input"""
        description = config.get_task_description('chat_task', user_input='{user_input}')
        expected_output = config.get_task_expected_output('chat_task')
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.chat_agent()
        )
    
    @task
    def planning_task(self) -> Task:
        """Create search strategy based on parsed input"""
        # This task will receive parsed_input from previous task via context
        description = """
        Based on the parsed user input from the previous task, create a search strategy.
        
        Analyze the extracted information and decide which activity categories should be searched.
        Available categories:
        - restaurants: For dining experiences
        - movies: For film entertainment
        - events: For local events, concerts, festivals
        - outdoor: For parks, trails, outdoor activities
        
        Consider:
        1. What categories match the user's stated interests?
        2. What categories would create a balanced day/evening?
        3. What makes sense for the time of day/week mentioned?
        
        Return ONLY a valid JSON object with this structure:
        {
            "categories": ["category1", "category2", ...],
            "priority": "which category to emphasize",
            "reasoning": "brief explanation of strategy"
        }
        """
        expected_output = config.get_task_expected_output('planner_task')
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.planner_agent(),
            context=[self.parse_task()]  # Gets output from parse_task
        )
    
    @task
    def discovery_task(self) -> Task:
        """Discover activities using LLM reasoning"""
        description = """
        Based on the parsed input and search strategy from previous tasks, 
        recommend realistic activities using your knowledge.
        
        For each category in the search strategy, suggest 3-5 REAL places/activities:
        - RESTAURANTS: Popular local restaurants with real names
        - MOVIES: Current or recent movies (2024-2025)
        - OUTDOOR: Parks, trails, landmarks
        - EVENTS: Seasonal events, festivals
        
        For EACH activity provide:
        - name: Real, specific name
        - type: One of [restaurant, movie, outdoor, event]
        - rating: Realistic rating 3.5-5.0 stars
        - details: Brief description
        
        CRITICAL: Ensure all recommendations are appropriate for the location mentioned.
        
        Return ONLY a valid JSON array of activity objects.
        """
        expected_output = config.get_task_expected_output('discovery_task')
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.discovery_agent(),
            context=[self.parse_task(), self.planning_task()]
        )
    
    @task
    def curation_task(self) -> Task:
        """Curate top activities from discovered options"""
        description = """
        Review the discovered activities and select the TOP 3-5 best options.
        
        Evaluation criteria:
        1. Location accuracy (except movies)
        2. Match with user interests
        3. Rating/quality (prioritize 4+ stars)
        4. Variety (mix of types)
        5. Logical flow
        
        Return ONLY a JSON object with this structure:
        {
            "selected": [
                {
                    "name": "activity name",
                    "type": "activity type",
                    "rating": rating,
                    "details": "description",
                    "reason": "why selected"
                }
            ],
            "curation_notes": "brief explanation"
        }
        """
        expected_output = config.get_task_expected_output('curator_task')
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.curator_agent(),
            context=[self.parse_task(), self.discovery_task()]
        )
    
    @task
    def summarization_task(self) -> Task:
        """Generate friendly, engaging itinerary"""
        description = """
        Create a friendly, engaging itinerary based on the curated activities.
        
        Write a natural, conversational summary that includes:
        1. A welcoming introduction
        2. Each activity with:
           - Name and type (use emojis!)
           - Rating if available
           - Brief description
           - Why it's a great choice
        3. A friendly closing with tips
        
        Tone: Warm, enthusiastic, helpful
        Length: 200-300 words
        Format: Use bullet points or numbered list
        
        Do NOT return JSON. Return friendly text ready to present to the user.
        """
        expected_output = config.get_task_expected_output('summarizer_task')
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.summarizer_agent(),
            context=[self.parse_task(), self.curation_task()]
        )
    
    # ========================
    # CREW
    # ========================
    
    @crew
    def crew(self) -> Crew:
        """
        Creates the Weekend Planner crew with all agents and tasks.
        Tasks execute sequentially with automatic context passing.
        """
        return Crew(
            agents=self.agents,  # Auto-collected from @agent decorators
            tasks=self.tasks,    # Auto-collected from @task decorators
            verbose=True,
            process='sequential'  # Tasks run in order
        )


# ========================
# CONVENIENCE FUNCTIONS
# ========================

def plan_weekend(user_input: str, status_callback=None) -> str:
    """
    Generate a weekend itinerary from user input.
    
    Args:
        user_input: Natural language query from user
        status_callback: Optional callback(agent_name, status) for UI updates
    
    Returns:
        Friendly itinerary text
    """
    try:
        planner = WeekendPlannerCrew()
        
        # Optional: Hook into crew execution for status updates
        if status_callback:
            # This is a placeholder - CrewAI doesn't have built-in callbacks yet
            # We'll handle status updates in app.py using the old pattern
            pass
        
        result = planner.crew().kickoff(inputs={'user_input': user_input})
        return str(result)
    
    except Exception as e:
        return f"❌ Error generating itinerary: {str(e)}\n\nPlease try again with a different query."


# For backward compatibility with old import style
def parse_user_input(user_input: str) -> Dict[str, Any]:
    """Parse user input (backward compatibility wrapper)"""
    planner = WeekendPlannerCrew()
    result = planner.parse_task().execute_sync()
    
    try:
        # Try to parse JSON from result
        result_str = str(result)
        if '```json' in result_str:
            result_str = result_str.split('```json')[1].split('```')[0].strip()
        elif '```' in result_str:
            result_str = result_str.split('```')[1].split('```')[0].strip()
        return json.loads(result_str)
    except:
        return {
            "date": "not specified",
            "location": "not specified",
            "interests": ["general"],
            "context": user_input
        }


if __name__ == "__main__":
    # Test the crew
    test_query = "Plan something fun for this Saturday in Seattle, include restaurants and outdoor activities"
    print("\n" + "="*60)
    print("TESTING WEEKEND PLANNER CREW")
    print("="*60)
    print(f"\nQuery: {test_query}\n")
    
    itinerary = plan_weekend(test_query)
    
    print("\n" + "="*60)
    print("GENERATED ITINERARY")
    print("="*60)
    print(itinerary)
