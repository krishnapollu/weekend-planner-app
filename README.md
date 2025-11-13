# 🧭 Weekend Planner Assistant

A multi-agent AI application built with CrewAI that helps you plan activities (restaurants, movies, outdoor trips, and events) for any given date, time, and location.

## 🏗️ Architecture

This app uses 5 specialized agents coordinated by CrewAI:

1. **Chat Agent** - Extracts structured info from user input
2. **Planner Agent** - Decides which activity categories to search
3. **Discovery Agent** - Fetches real data from external APIs
4. **Curator Agent** - Filters and ranks the best options
5. **Summarizer Agent** - Creates a friendly itinerary

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- API keys for external services (see below)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd weekend-planner-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Required API Keys

- **OpenAI or Google Gemini**: For LLM reasoning (at least one)
- **Google Places API**: For restaurant and outdoor location data
- **TMDb API**: For movie information
- **Eventbrite API**: For local events (optional)
- **OpenWeather API**: For weather data (optional)

Get free API keys:
- [Google Cloud Console](https://console.cloud.google.com/) - Places API & Gemini
- [TMDb](https://www.themoviedb.org/settings/api)
- [OpenWeather](https://openweathermap.org/api)
- [Eventbrite](https://www.eventbrite.com/platform/api)

### Usage

#### Option 1: Streamlit Web UI (Recommended) 🌐

Launch the interactive web interface:

```bash
# Windows (Command Prompt)
run_ui.bat

# Windows (PowerShell)
.\run_ui.ps1

# Or directly
streamlit run app.py
```

This opens a beautiful, user-friendly interface in your browser where you can:
- 📝 Enter your weekend plans in a text area
- 🤖 Watch the 5 AI agents process your request in real-time
- ✨ View the generated itinerary with beautiful formatting
- 📊 Track each agent's status and output

#### Option 2: Command Line 💻

Run the planner assistant:

```bash
python main.py "Plan something fun for me this Saturday in Austin, maybe outdoors and dinner"
```

The assistant will:
1. Parse your request
2. Search for relevant activities
3. Curate the best options
4. Generate a friendly itinerary

## 📁 Project Structure

```
weekend-planner-assistant/
├── agents/
│   ├── __init__.py
│   ├── chat_agent.py       # User input parser
│   ├── planner_agent.py    # Activity planner
│   ├── discovery_agent.py  # API data fetcher
│   ├── curator_agent.py    # Results filter/ranker
│   └── summarizer_agent.py # Itinerary generator
├── utils/
│   ├── __init__.py
│   └── api_clients.py      # External API integrations
├── main.py                 # Orchestrator
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Tech Stack

- **Framework**: CrewAI
- **LLM**: Gemini 1.5 Flash / GPT-4
- **APIs**: Google Places, TMDb, Eventbrite, OpenWeather
- **Language**: Python 3.10+

## 📝 License

MIT License
