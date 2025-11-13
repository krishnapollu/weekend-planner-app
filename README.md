# 🧭 Weekend Planner Assistant

A multi-agent AI application built with CrewAI that helps you plan personalized weekend activities (restaurants, movies, outdoor trips, and events) using pure LLM reasoning—no external APIs required!

## ✨ Features

- 🤖 **5 Intelligent Agents** working together to create perfect itineraries
- 💬 **Chat-style UI** with real-time agent pipeline visualization
- 🌍 **Any City, Worldwide** - Get location-specific recommendations
- 🎯 **LLM-Powered Discovery** - Uses Google Gemini 2.0 Flash for realistic activity suggestions
- ⚡ **No External APIs** - Pure LLM reasoning based on world knowledge
- 🎨 **Clean, Modern Interface** - Built with Streamlit

## 🏗️ Architecture

This app uses 5 specialized agents orchestrated by CrewAI:

1. **Chat Agent** - Parses user input and extracts location, date, and interests
2. **Planner Agent** - Creates a search strategy based on user preferences
3. **Discovery Agent** - Generates realistic activity recommendations using LLM knowledge
4. **Curator Agent** - Filters and ranks the top 3-5 options with validation
5. **Summarizer Agent** - Creates a friendly, engaging itinerary

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

### Required API Key

- **Google Gemini API**: For LLM reasoning (FREE with generous limits)

Get your free API key:
- [Google AI Studio](https://aistudio.google.com/app/apikey) - Sign in and create an API key

**Note**: This app uses **only LLM reasoning** - no external data APIs required! The Discovery Agent generates realistic recommendations based on the LLM's knowledge of locations worldwide.

### Usage

Launch the Streamlit web interface:

```bash
streamlit run app.py
```

This opens a beautiful chat-style interface in your browser where you can:

- � **Chat naturally** - Type requests like "Plan activities for this weekend in Atlanta"
- 🎯 **Real-time Pipeline** - Watch each agent's status (Chat → Planner → Discovery → Curator → Summarizer)
- ⚡ **Instant Results** - Get personalized itineraries with restaurants, movies, parks, and events
- 🌍 **Any Location** - Works for cities worldwide (Atlanta, Tokyo, Paris, Mumbai, etc.)

**Example Prompts:**
- "Suggest some plans for this weekend in Seattle, include restaurants and outdoor activities"
- "I want to visit Austin this Saturday. Find me good BBQ spots and parks"
- "Plan a fun day in Chicago with museums, dining, and a movie"

## 📁 Project Structure

```
weekend-planner-assistant/
├── agents/
│   ├── __init__.py
│   ├── chat_agent.py       # Parses user input → structured JSON
│   ├── planner_agent.py    # Creates search strategy
│   ├── discovery_agent.py  # Generates activities using LLM reasoning
│   ├── curator_agent.py    # Filters and ranks top options
│   └── summarizer_agent.py # Creates friendly itinerary
├── app.py                  # Streamlit UI with chat interface
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── .gitignore
└── README.md
```

## 🛠️ Tech Stack

- **Framework**: CrewAI 1.4.1
- **LLM**: Google Gemini 2.0 Flash (FREE)
- **UI**: Streamlit 1.51.0
- **Data Source**: Pure LLM reasoning (no external APIs)
- **Language**: Python 3.10+

## 🎯 How It Works

1. **User Input** → Chat Agent extracts location, date, and interests
2. **Planning** → Planner Agent decides which categories to search (restaurants, outdoor, movies, events)
3. **Discovery** → Discovery Agent uses LLM to generate realistic recommendations for the location
4. **Curation** → Curator Agent selects top 3-5 activities with variety and quality
5. **Output** → Summarizer Agent creates a friendly, conversational itinerary

## 🌟 Example Output

**User**: "Suggest plans for this weekend in Atlanta, include restaurants and parks"

**Assistant**: 
> Hey there! Get ready for an awesome weekend in Atlanta! 🎉
> 
> - **Morning: Piedmont Park** 🌳 (Rating: 4.7) - Perfect for a relaxing stroll...
> - **Afternoon: Ponce City Market** 🍔 (Rating: 4.6) - Vibrant food hall with diverse options...
> - **Evening: The Plaza Theatre** 🎬 (Rating: 4.5) - Atlanta's oldest operating cinema...

## 📝 License

MIT License
