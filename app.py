"""
Weekend Planner Assistant - Streamlit UI (Refined Design)
Compact, professional chat-style interface with real-time agent pipeline updates.
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import ssl
from dotenv import load_dotenv
import json
from io import StringIO
import sys
import time
import httpx
import threading

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
    padding: 0.5rem 1rem !important;
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

/* Header Area - Centered, Light color - COMPACT */
.app-header {
    text-align: center;
    padding: 0.5rem 0;
    margin-bottom: 0.5rem;
}
.app-header h1 {
    font-size: 1.5rem;
    margin: 0;
    color: #f3f4f6 !important;
}

/* Chat Messages Area - Full width in column, optimized height */
.chat-messages {
    width: 100%;
    max-width: 100%;
    height: calc(100vh - 200px);
    margin: 0 auto 0.5rem auto;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    background: #2a2a2a !important;
}

/* Chat Bubbles - Dynamic width */
.chat-bubble {
    padding: 0.5rem 0.75rem;
    border-radius: 12px;
    margin-bottom: 0.6rem;
    display: inline-block;
    max-width: 85%;
    word-wrap: break-word;
    white-space: normal;
    line-height: 1.4;
    font-size: 0.85rem;
}
.user-bubble {
    background-color: #2563eb !important;
    color: white !important;
    float: right;
    clear: both;
    white-space: pre-wrap;
    max-width: 60% !important;
    width: auto !important;
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

/* Format list items in chat bubbles - CRITICAL for bullet rendering */
.chat-bubble ul {
    margin: 8px 0 !important;
    padding-left: 20px !important;
    list-style-type: disc !important;
    list-style-position: outside !important;
    display: block !important;
}
.chat-bubble ol {
    margin: 8px 0 !important;
    padding-left: 20px !important;
    list-style-type: decimal !important;
    list-style-position: outside !important;
    display: block !important;
}
.chat-bubble li {
    margin: 3px 0 !important;
    line-height: 1.4 !important;
    display: list-item !important;
    font-size: 0.85rem;
}
.chat-bubble p {
    margin: 4px 0;
    line-height: 1.4;
    font-size: 0.85rem;
}
.chat-bubble div {
    margin: 2px 0;
    font-size: 0.85rem;
}
.chat-bubble b, .chat-bubble strong {
    font-weight: 600;
    color: inherit;
}

/* Input Area Styling */
.stTextInput {
    height: auto !important;
    min-height: 48px !important;
}

.stTextInput > div {
    height: auto !important;
    min-height: 48px !important;
}

.stTextInput input {
    background-color: #2a2a2a !important;
    color: #f3f4f6 !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 24px !important;
    height: 48px !important;
    font-size: 0.9rem !important;
    padding-left: 18px !important;
    padding-right: 18px !important;
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
    margin-top: 0.25rem !important;
}

/* Send button styling - circular, aligned with input */
/* Remove the element-container wrapper around button */
[data-testid="column"]:has(.stButton) .element-container {
    height: 48px !important;
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
    font-size: 1rem !important;
    padding: 0 !important;
    margin: 0 !important;
    min-width: 38px !important;
    height: 38px !important;
    width: 38px !important;
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

/* Optimize font sizes for compact layout */
html {
    font-size: 95%;
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

/* Spinner/Status Messages - Compact styling, positioned higher */
.stSpinner > div {
    text-align: center;
    padding: 0 !important;
    margin: 0 !important;
    margin-top: -0.5rem !important;
}
.stSpinner > div > div {
    font-size: 0.85rem !important;
    line-height: 1.2 !important;
}

/* Prevent spinner container from adding extra height */
[data-testid="stSpinner"] {
    min-height: auto !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Position spinner area more compactly */
.element-container:has([data-testid="stSpinner"]) {
    margin-top: -0.25rem !important;
    margin-bottom: 0 !important;
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
if 'last_status_update' not in st.session_state:
    st.session_state.last_status_update = time.time()

# Render chat interface - COMPLETELY REBUILT for proper HTML rendering
def render_chat():
    import re
    
    def markdown_to_html(text):
        """
        Convert markdown to HTML.
        Key insight: Streamlit's markdown with unsafe_allow_html=True will render HTML,
        but we must ensure the HTML is valid and complete.
        """
        # Convert **bold** first (before line processing)
        text = re.sub(r'\*\*([^\*]+?)\*\*', r'<b>\1</b>', text)
        
        lines = text.split('\n')
        html_lines = []
        in_ul = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # Empty line
                if in_ul:
                    html_lines.append('</ul>')
                    in_ul = False
                html_lines.append('<br/>')
                continue
            
            # Check for bullet: * or - followed by space
            if re.match(r'^[\*\-]\s', stripped):
                if not in_ul:
                    html_lines.append('<ul style="margin:8px 0;padding-left:20px;list-style-type:disc;">')
                    in_ul = True
                # Remove bullet marker
                item_text = re.sub(r'^[\*\-]\s+', '', stripped)
                html_lines.append(f'<li style="margin:4px 0;">{item_text}</li>')
            else:
                # Regular text
                if in_ul:
                    html_lines.append('</ul>')
                    in_ul = False
                html_lines.append(f'<div style="margin:4px 0;">{stripped}</div>')
        
        if in_ul:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    # Build complete HTML as single string
    html_output = '<div class="chat-messages">'
    
    for msg in st.session_state.messages:
        role = msg['role']
        content = msg['content']
        bubble_class = 'user-bubble' if role == 'user' else 'agent-bubble'
        
        if role == 'assistant':
            # Convert markdown to HTML
            processed_content = markdown_to_html(content)
        else:
            # User message - simple line break conversion
            processed_content = content.replace('\n', '<br/>')
        
        html_output += f'''
<div class="chat-container">
    <div class="chat-bubble {bubble_class}">
        {processed_content}
    </div>
</div>
'''
    
    html_output += '</div>'
    
    # Render as single HTML block
    st.markdown(html_output, unsafe_allow_html=True)

# Header area (top-left, light color)
st.markdown('<div class="app-header"><h1>🗓️ Weekend Planner App</h1></div>', unsafe_allow_html=True)

# Agent Status Bar (shows pipeline progress)
def render_agent_status_sidebar():
    """Render vertical status panel for agent pipeline on the right side"""
    agents = [
        {'name': 'Chat', 'icon': '💬', 'label': 'Parse'},
        {'name': 'Planner', 'icon': '📋', 'label': 'Plan'},
        {'name': 'Discovery', 'icon': '🔍', 'label': 'Discover'},
        {'name': 'Curator', 'icon': '✨', 'label': 'Curate'},
        {'name': 'Summarizer', 'icon': '📝', 'label': 'Write'}
    ]
    
    with st.container():
        st.markdown('<p style="font-size:1rem;font-weight:600;color:#f3f4f6;margin-bottom:0.5rem;">Agent Pipeline</p>', unsafe_allow_html=True)
        
        # Add CSS for pulsing animation
        st.markdown(
            """
            <style>
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.05); }
            }
            .pulse-active {
                animation: pulse 1s ease-in-out infinite;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        for agent in agents:
            status = st.session_state.pipeline_status.get(agent['name'], 'pending')
            
            # Determine styling based on status
            if status == 'completed':
                bg_color = '#10b981'
                label_style = 'color: #10b981; font-weight: bold;'
                animation_class = ''
            elif status == 'active':
                bg_color = '#3b82f6'
                label_style = 'color: #3b82f6; font-weight: bold;'
                animation_class = 'pulse-active'
            else:  # pending
                bg_color = '#4b5563'
                label_style = 'color: #9ca3af;'
                animation_class = ''
            
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem 0.5rem;margin:0.25rem 0;border-radius:8px;background:rgba(255,255,255,0.02);" class="{animation_class}">'
                f'<div style="width:32px;height:32px;border-radius:50%;background:{bg_color};display:flex;align-items:center;justify-content:center;font-size:1rem;">{agent["icon"]}</div>'
                f'<span style="{label_style};font-size:0.9rem;">{agent["label"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

# Main layout with sidebar for agent status
col_status, col_main = st.columns([0.15, 0.85])

with col_status:
    # Agent status sidebar (dynamically updated during processing)
    status_placeholder = st.empty()
    with status_placeholder.container():
        render_agent_status_sidebar()

with col_main:
    # Chat area (scrollable messages)
    render_chat()
    
    # Input area (centered, with button inside)
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

# Execute agent pipeline
if st.session_state.processing and st.session_state.current_query:
    
    def update_pipeline_display():
        """Refresh the pipeline sidebar display"""
        with status_placeholder.container():
            render_agent_status_sidebar()
    
    try:
        # Chat Agent
        st.session_state.pipeline_status['Chat'] = 'active'
        update_pipeline_display()
        parsed_input = parse_user_input(st.session_state.current_query)
        st.session_state.pipeline_status['Chat'] = 'completed'
        update_pipeline_display()
        
        # Planner Agent
        st.session_state.pipeline_status['Planner'] = 'active'
        update_pipeline_display()
        search_strategy = plan_search_strategy(parsed_input)
        st.session_state.pipeline_status['Planner'] = 'completed'
        update_pipeline_display()
        
        # Discovery Agent
        st.session_state.pipeline_status['Discovery'] = 'active'
        update_pipeline_display()
        activities = discover_activities(parsed_input, search_strategy)
        st.session_state.pipeline_status['Discovery'] = 'completed'
        update_pipeline_display()
        
        # Curator Agent
        st.session_state.pipeline_status['Curator'] = 'active'
        update_pipeline_display()
        curated = curate_activities(activities, parsed_input)
        st.session_state.pipeline_status['Curator'] = 'completed'
        update_pipeline_display()
        
        # Summarizer Agent
        st.session_state.pipeline_status['Summarizer'] = 'active'
        update_pipeline_display()
        itinerary = generate_itinerary(curated, parsed_input)
        st.session_state.pipeline_status['Summarizer'] = 'completed'
        update_pipeline_display()
        
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
