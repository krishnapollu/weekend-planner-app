"""
Weekend Planner Assistant - Streamlit UI (Refined Design)
Compact, professional chat-style interface with real-time agent pipeline updates.
"""

import streamlit as st
import os
import ssl
from dotenv import load_dotenv
import json
from io import StringIO
import sys
import time
import httpx

# Load environment variables FIRST
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

# Import agent functions AFTER SSL setup
from agents.chat_agent import parse_user_input
from agents.planner_agent import plan_search_strategy
from agents.discovery_agent import discover_activities
from agents.curator_agent import curate_activities
from agents.summarizer_agent import generate_itinerary

# Page configuration
st.set_page_config(
    page_title="Weekend Planner Assistant",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean centered layout
st.markdown("""
<style>
/* Fixed Layout - No Page Scroll */
html, body, [data-testid="stAppViewContainer"], .main {
    height: 100vh;
    overflow: hidden;
    background-color: #1e1e1e !important;
}

/* Hide Streamlit default elements */
.block-container {
    padding: 1rem !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] {
    display: none;
}
header[data-testid="stHeader"] {
    display: none;
}
footer {
    display: none;
}
.stDeployButton {
    display: none;
}

/* Critical: Make all Streamlit containers flexible */
.element-container,
[data-testid="stVerticalBlock"] > div,
[data-testid="stHorizontalBlock"] > div {
    width: 100% !important;
    max-width: 100% !important;
}

/* Header Area - Top Left, Light color */
.app-header {
    text-align: left;
    padding: 1rem 0;
    margin-bottom: 1rem;
}
.app-header h1 {
    font-size: 1.8rem;
    margin: 0;
    color: #f3f4f6 !important;
}

/* Chat Messages Area - 80% width, 60% height, centered, lighter than background */
.chat-messages {
    width: 80%;
    max-width: 80%;
    height: 60vh;
    margin: 0 auto 1rem auto;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    background: #2a2a2a !important;
}

/* Chat Bubbles - Dynamic width */
.chat-bubble {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    display: inline-block;
    max-width: 85%;
    word-wrap: break-word;
    white-space: normal;
    line-height: 1.6;
}
.user-bubble {
    background-color: #2563eb !important;
    color: white !important;
    float: right;
    clear: both;
    white-space: pre-wrap;
}
.agent-bubble {
    background-color: #3a3a3a !important;
    color: #f3f4f6 !important;
    border: 1px solid #4a4a4a;
    float: left;
    clear: both;
}
.chat-container {
    overflow: hidden;
    margin-bottom: 0.5rem;
}

/* Format list items in chat bubbles */
.chat-bubble ul, .chat-bubble ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}
.chat-bubble li {
    margin: 0.25rem 0;
}

/* Input Area Styling */
.stTextInput {
    height: auto !important;
    min-height: 56px !important;
}

.stTextInput > div {
    height: auto !important;
    min-height: 56px !important;
}

.stTextInput input {
    background-color: #2a2a2a !important;
    color: #f3f4f6 !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 26px !important;
    height: 56px !important;
    font-size: 0.95rem !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
    box-sizing: border-box !important;
}

.stTextInput input::placeholder {
    color: #6b7280 !important;
}

.stTextInput label {
    display: none !important;
}

/* Add spacing between chat and input */
[data-testid="column"]:has(.stTextInput) {
    margin-top: 1rem !important;
}

/* Send button styling - circular, aligned with input */
/* Remove the element-container wrapper around button */
[data-testid="column"]:has(.stButton) .element-container {
    height: 56px !important;
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stButton {
    display: flex !important;
    align-items: center !important;
    height: 100% !important;
    margin: 0 !important;
}

.stButton > div {
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
}

.stButton button {
    background-color: #2563eb !important;
    border: none !important;
    color: white !important;
    font-size: 1.1rem !important;
    padding: 0 !important;
    margin: 0 !important;
    min-width: 42px !important;
    height: 42px !important;
    width: 42px !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    line-height: 1 !important;
}

.stButton button:hover {
    background-color: #1d4ed8 !important;
}

.stButton button:disabled {
    background-color: #4b5563 !important;
    cursor: not-allowed !important;
    opacity: 0.5 !important;
}

/* Scale down all fonts by 10% */
html {
    font-size: 90%;
}

/* Customize scrollbar */
.chat-messages::-webkit-scrollbar {
    width: 8px;
}
.chat-messages::-webkit-scrollbar-track {
    background: #1e1e1e;
}
.chat-messages::-webkit-scrollbar-thumb {
    background: #4a4a4a;
    border-radius: 4px;
}
.chat-messages::-webkit-scrollbar-thumb:hover {
    background: #5a5a5a;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = {
        'Chat': 'pending',
        'Planner': 'pending',
        'Discovery': 'pending',
        'Curator': 'pending',
        'Summarizer': 'pending'
    }
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'current_query' not in st.session_state:
    st.session_state.current_query = None

# Render chat interface with dynamic bubble widths
def render_chat():
    import re
    
    chat_html = '<div class="chat-messages">'
    
    for message in st.session_state.messages:
        bubble_class = 'user-bubble' if message['role'] == 'user' else 'agent-bubble'
        content = message["content"]
        
        if message['role'] == 'assistant':
            # Convert markdown-style formatting for agent messages
            # Convert **bold** to <strong>
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            
            # Convert bullet points to HTML list
            lines = content.split('\n')
            formatted_lines = []
            in_list = False
            
            for line in lines:
                stripped = line.strip()
                # Check if line starts with * followed by space (bullet point)
                if stripped.startswith('*   ') or stripped.startswith('* '):
                    if not in_list:
                        formatted_lines.append('<ul>')
                        in_list = True
                    # Remove the * and create list item
                    list_content = re.sub(r'^\*\s+', '', stripped)
                    formatted_lines.append(f'<li>{list_content}</li>')
                else:
                    if in_list:
                        formatted_lines.append('</ul>')
                        in_list = False
                    if stripped:  # Only add non-empty lines
                        formatted_lines.append(line)
            
            if in_list:
                formatted_lines.append('</ul>')
            
            content = '<br>'.join(formatted_lines)
        else:
            # For user messages, just replace newlines
            content = content.replace("\n", "<br>")
        
        chat_html += f'''
            <div class="chat-container">
                <div class="chat-bubble {bubble_class}">{content}</div>
            </div>
        '''
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

# Header area (top-left, light color)
st.markdown('<div class="app-header"><h1>🗓️ Weekend Planner App</h1></div>', unsafe_allow_html=True)

# Chat area (scrollable messages, 80% width, 60% height, centered)
render_chat()

# Input area (80% width, centered, with button inside)
# Create centered container using columns
left_spacer, input_area, right_spacer = st.columns([0.1, 0.8, 0.1])

with input_area:
    input_col, button_col = st.columns([20, 1], gap="small")
    with input_col:
        user_input = st.text_input(
            "Message",
            placeholder="Ask me to plan your weekend...",
            key="user_input",
            label_visibility="collapsed",
            max_chars=500
        )
    with button_col:
        st.markdown('<div style="margin-top: 0px;">', unsafe_allow_html=True)
        send_button = st.button("➜", disabled=st.session_state.processing, key="send_btn")
        st.markdown('</div>', unsafe_allow_html=True)

if send_button and user_input.strip():
    st.session_state.messages.append({'role': 'user', 'content': user_input.strip()})
    st.session_state.current_query = user_input.strip()
    st.session_state.processing = True
    st.rerun()

# Process agent pipeline
if st.session_state.processing and st.session_state.current_query:
    try:
        # Chat Agent
        st.session_state.pipeline_status['Chat'] = 'active'
        with st.spinner("🤖 Parsing your request..."):
            parsed_input = parse_user_input(st.session_state.current_query)
        st.session_state.pipeline_status['Chat'] = 'completed'
        
        # Planner Agent
        st.session_state.pipeline_status['Planner'] = 'active'
        with st.spinner("📋 Planning search strategy..."):
            search_strategy = plan_search_strategy(parsed_input)
        st.session_state.pipeline_status['Planner'] = 'completed'
        
        # Discovery Agent
        st.session_state.pipeline_status['Discovery'] = 'active'
        with st.spinner("🔍 Discovering activities..."):
            activities = discover_activities(parsed_input, search_strategy)
        st.session_state.pipeline_status['Discovery'] = 'completed'
        
        # Curator Agent
        st.session_state.pipeline_status['Curator'] = 'active'
        with st.spinner("✨ Curating top recommendations..."):
            curated = curate_activities(activities, parsed_input)
        st.session_state.pipeline_status['Curator'] = 'completed'
        
        # Summarizer Agent
        st.session_state.pipeline_status['Summarizer'] = 'active'
        with st.spinner("📝 Generating itinerary..."):
            itinerary = generate_itinerary(curated, parsed_input)
        st.session_state.pipeline_status['Summarizer'] = 'completed'
        
        # Add assistant response
        st.session_state.messages.append({'role': 'assistant', 'content': itinerary})
        
        # Reset state
        st.session_state.processing = False
        st.session_state.current_query = None
        st.session_state.pipeline_status = {k: 'pending' for k in st.session_state.pipeline_status}
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.session_state.pipeline_status[list(st.session_state.pipeline_status.keys())[0]] = 'error'
        st.session_state.processing = False
        st.session_state.current_query = None
