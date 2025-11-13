# CrewAI Decorators vs Current Approach

## Why Use CrewAI Decorators?

### Current Approach (What We Have)
```python
# Separate factory functions in each agent file
def create_chat_agent() -> Agent:
    agent_config = config.get_agent_config('chat_agent')
    return Agent(role=..., goal=..., backstory=...)

def create_chat_task(agent: Agent, user_input: str) -> Task:
    return Task(description=..., agent=agent, ...)

def parse_user_input(user_input: str) -> dict:
    agent = create_chat_agent()
    task = create_chat_task(agent, user_input)
    result = agent.execute_task(task)
    # Manual JSON parsing and error handling
    return parsed_result
```

**Problems:**
- Lots of boilerplate code (5 files × 3 functions each = 15 functions!)
- Manual agent.execute_task() calls
- Manual JSON parsing and error handling
- Hard to see the overall crew structure
- No automatic context passing between tasks

---

### Decorator Approach (What We Could Have)
```python
class WeekendPlannerCrew:
    
    @agent
    def chat_agent(self) -> Agent:
        """Just return an Agent - decorator handles registration"""
        return Agent(role="...", goal="...", backstory="...")
    
    @task
    def parse_task(self) -> Task:
        """Tasks automatically use context from previous tasks"""
        return Task(
            description="Parse {user_input}",  # Auto-filled from crew.kickoff()
            agent=self.chat_agent()
        )
    
    @crew
    def crew(self) -> Crew:
        """All agents and tasks automatically wired together"""
        return Crew(
            agents=[self.chat_agent(), ...],
            tasks=[self.parse_task(), ...],
            process='sequential'  # Or 'hierarchical'
        )

# Usage - ONE function call
result = WeekendPlannerCrew().crew().kickoff(inputs={'user_input': query})
```

**Benefits:**
- ✅ **90% less boilerplate** - No factory functions, no manual execution
- ✅ **Automatic context passing** - Tasks get previous task outputs automatically
- ✅ **Clear structure** - All agents/tasks in ONE class
- ✅ **Better error handling** - CrewAI handles failures and retries
- ✅ **Built-in memory** - Agents can remember previous interactions
- ✅ **Process management** - Sequential vs Hierarchical vs Consensus modes

---

## Key Decorators

### 1. `@agent`
Marks a method as an agent definition. CrewAI automatically registers it.

```python
@agent
def research_agent(self) -> Agent:
    return Agent(
        role="Researcher",
        goal="Find information",
        tools=[search_tool, scraper_tool],  # Can add tools!
        llm=self.llm
    )
```

### 2. `@task`
Marks a method as a task. Automatically connects to agents and manages context.

```python
@task
def research_task(self) -> Task:
    return Task(
        description="Research {topic}",  # Variables from kickoff()
        agent=self.research_agent(),
        context=[self.previous_task()],  # Task dependencies
        output_json=True,  # Auto-parse JSON
        output_pydantic=MyModel  # Or use Pydantic models!
    )
```

### 3. `@crew`
Creates the crew. Automatically wires all @agent and @task methods.

```python
@crew
def my_crew(self) -> Crew:
    return Crew(
        agents=self.agents,  # Auto-collected from @agent methods
        tasks=self.tasks,    # Auto-collected from @task methods
        process='hierarchical',  # Manager-worker pattern
        manager_llm=self.llm
    )
```

### 4. `@tool` (Bonus!)
Define custom tools for agents.

```python
@tool("Search restaurants")
def search_restaurants(location: str, cuisine: str) -> dict:
    """Search for restaurants in a location"""
    # Your API call here
    return results
```

---

## Advanced Features We're Missing

### 1. Context Passing
**Current:** Manual JSON serialization between agents
**Decorator:** Automatic context flow

```python
@task
def task2(self) -> Task:
    return Task(
        context=[self.task1()],  # Gets task1 output automatically
        agent=self.agent2()
    )
```

### 2. Process Management
**Current:** Sequential only (hardcoded in app.py)
**Decorator:** Multiple process types

```python
@crew
def crew(self) -> Crew:
    return Crew(
        process='hierarchical',  # Manager coordinates agents
        # OR process='consensus'  # Agents vote on decisions
    )
```

### 3. Memory
**Current:** No memory between conversations
**Decorator:** Built-in memory systems

```python
@agent
def chat_agent(self) -> Agent:
    return Agent(
        memory=True,  # Remember previous conversations
        verbose=True
    )
```

### 4. Output Formats
**Current:** Manual JSON parsing with try/except
**Decorator:** Automatic parsing

```python
@task
def parse_task(self) -> Task:
    return Task(
        output_json=True,  # Auto-parse JSON
        # OR output_pydantic=MyModel  # Validate with Pydantic
        # OR output_file='result.txt'  # Save to file
    )
```

### 5. Tools Integration
**Current:** No tools, just LLM reasoning
**Decorator:** Easy tool integration

```python
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

@agent
def discovery_agent(self) -> Agent:
    return Agent(
        tools=[
            SerperDevTool(),  # Google search
            ScrapeWebsiteTool(),  # Web scraping
            self.my_custom_tool()  # Custom tools
        ]
    )
```

---

## Migration Path

### Option 1: Full Refactor (Recommended)
- Create `crew.py` with decorator-based class
- Keep existing agent files for reference
- Update `app.py` to use: `WeekendPlannerCrew().crew().kickoff()`
- **Time:** ~2 hours
- **Benefit:** Cleaner code, easier to enhance

### Option 2: Hybrid Approach
- Keep current agent files
- Add decorator wrapper class
- Gradually migrate tasks
- **Time:** ~1 hour
- **Benefit:** Safer, incremental migration

### Option 3: Keep Current (Not Recommended)
- No changes
- **Time:** 0 hours
- **Drawback:** Harder to add advanced features later

---

## Recommendation

**Use decorators!** Here's why:

1. **Much less code** - 1 class vs 5 files with 15 functions
2. **Better for enhancements** - Adding weather agent, tools, memory is trivial
3. **Industry standard** - Most CrewAI examples use decorators
4. **Future-proof** - New CrewAI features target decorator API

**Next Steps:**
1. Create `crew.py` with decorator-based WeekendPlannerCrew class
2. Test it works with current config files
3. Update `app.py` to use new crew class
4. Archive old agent files as reference
5. Celebrate cleaner code! 🎉

---

## Example Enhancements That Become Easy

### Adding a Weather Agent
```python
@agent
def weather_agent(self) -> Agent:
    return Agent(
        role="Weather Advisor",
        tools=[weather_api_tool()],  # Real API call
        llm=self.llm
    )

@task
def weather_task(self) -> Task:
    return Task(
        description="Check weather for {location} on {date}",
        agent=self.weather_agent(),
        context=[self.parse_task()]
    )
```

Just add to crew's task list - done! No need to modify app.py.

### Adding Memory
```python
@agent
def chat_agent(self) -> Agent:
    return Agent(
        memory=True,  # ONE LINE!
        llm=self.llm
    )
```

Now agent remembers previous conversations automatically.

### Hierarchical Process
```python
@crew
def crew(self) -> Crew:
    return Crew(
        process='hierarchical',  # Manager coordinates work
        manager_llm=self.llm
    )
```

Agents now work in parallel with a manager coordinating!
