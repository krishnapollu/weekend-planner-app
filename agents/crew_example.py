"""
Example of CrewAI decorator-based approach
This shows how @agent, @task, and @crew decorators simplify code
"""

from crewai import Agent, Task, Crew, agent, task, crew
from crewai import LLM
import os
import sys
from pathlib import Path

# Add parent directory to path
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from config.config_loader import config


class WeekendPlannerCrew:
    """
    Weekend Planner crew using CrewAI decorators.
    Much cleaner than manual agent/task creation!
    """
    
    def __init__(self):
        # Setup LLM once for all agents
        if os.getenv('GOOGLE_API_KEY'):
            self.llm = LLM(model="gemini-2.0-flash")
        elif os.getenv('OPENAI_API_KEY'):
            self.llm = LLM(model="gpt-4-turbo-preview")
        else:
            raise ValueError("No LLM API key found")
    
    # ===== AGENTS =====
    
    @agent
    def chat_agent(self) -> Agent:
        """Chat Interface Specialist - Parses user input"""
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
        """Activity Planning Strategist"""
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
        """Local Activity Expert"""
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
        """Experience Curator"""
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
        """Itinerary Writer"""
        agent_config = config.get_agent_config('summarizer_agent')
        return Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            llm=self.llm,
            verbose=agent_config.get('verbose', True),
            allow_delegation=agent_config.get('allow_delegation', False)
        )
    
    # ===== TASKS =====
    
    @task
    def parse_task(self) -> Task:
        """Parse user input to extract structured information"""
        return Task(
            description=config.get_task_description(
                'chat_task',
                user_input="{user_input}"  # Context variable from crew.kickoff()
            ),
            expected_output=config.get_task_expected_output('chat_task'),
            agent=self.chat_agent()
        )
    
    @task
    def planning_task(self) -> Task:
        """Create search strategy based on parsed input"""
        return Task(
            description=config.get_task_description(
                'planner_task',
                date="{date}",
                location="{location}",
                interests="{interests}",
                context="{context}"
            ),
            expected_output=config.get_task_expected_output('planner_task'),
            agent=self.planner_agent(),
            context=[self.parse_task()]  # Depends on parse_task output
        )
    
    @task
    def discovery_task(self) -> Task:
        """Discover activities using LLM reasoning"""
        return Task(
            description=config.get_task_description(
                'discovery_task',
                location="{location}",
                date="{date}",
                interests="{interests}",
                categories="{categories}"
            ),
            expected_output=config.get_task_expected_output('discovery_task'),
            agent=self.discovery_agent(),
            context=[self.planning_task()]  # Depends on planning output
        )
    
    @task
    def curation_task(self) -> Task:
        """Curate top activities"""
        return Task(
            description=config.get_task_description(
                'curator_task',
                location="{location}",
                interests="{interests}",
                context="{context}",
                activities_json="{activities}"  # From discovery
            ),
            expected_output=config.get_task_expected_output('curator_task'),
            agent=self.curator_agent(),
            context=[self.discovery_task()]
        )
    
    @task
    def summarization_task(self) -> Task:
        """Generate friendly itinerary"""
        return Task(
            description=config.get_task_description(
                'summarizer_task',
                location="{location}",
                date="{date}",
                curated_json="{curated_activities}",
                curation_notes="{curation_notes}"
            ),
            expected_output=config.get_task_expected_output('summarizer_task'),
            agent=self.summarizer_agent(),
            context=[self.curation_task()],
            output_file='itinerary.txt'  # Optional: save output
        )
    
    # ===== CREW =====
    
    @crew
    def crew(self) -> Crew:
        """
        Creates the Weekend Planner crew.
        The @crew decorator automatically wires all @agent and @task methods!
        """
        return Crew(
            agents=[
                self.chat_agent(),
                self.planner_agent(),
                self.discovery_agent(),
                self.curator_agent(),
                self.summarizer_agent()
            ],
            tasks=[
                self.parse_task(),
                self.planning_task(),
                self.discovery_task(),
                self.curation_task(),
                self.summarization_task()
            ],
            verbose=True,
            process='sequential'  # Tasks execute in order
        )


# ===== USAGE =====

def plan_weekend(user_input: str) -> str:
    """
    Main function to generate weekend itinerary.
    Much simpler than before!
    """
    planner_crew = WeekendPlannerCrew()
    
    # Kickoff the crew with context
    result = planner_crew.crew().kickoff(
        inputs={'user_input': user_input}
    )
    
    return str(result)


if __name__ == "__main__":
    # Test the crew
    test_query = "Plan something fun for this Saturday in Seattle, include restaurants and parks"
    print(plan_weekend(test_query))
