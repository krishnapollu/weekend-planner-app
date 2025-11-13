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

# Custom CSS for refined design
st.markdown("""
<style>
/* General Layout */
.main {padding: 1rem; max-width: 900px; margin: 0 auto;}
/* Chat Bubbles */
.chat-bubble {padding: 0.8rem; border-radius: 10px; margin-bottom: 0.5rem;}
.user-bubble {background-color: #2563eb; color: white; text-align: right;}
.agent-bubble {background-color: #f3f4f6; color: #111827;}
/* Input Area */
.input-container {margin-top: 1rem;}
.input-container textarea {width: 100%; padding: 0.5rem;}
/* Pipeline */
.pipeline {display: flex; justify-content: space-between; margin-top: 1rem;}
.pipeline-step {flex: 1; text-align: center; padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 5px;}
.pipeline-step.active {background-color: #fef3c7;}
.pipeline-step.completed {background-color: #d1fae5;}
.pipeline-step.error {background-color: #fee2e2;}
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

# Render chat interface
def render_chat():
    for message in st.session_state.messages:
        bubble_class = 'user-bubble' if message['role'] == 'user' else 'agent-bubble'
        st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)

# Render pipeline
def render_pipeline():
    pipeline_html = '<div class="pipeline">'
    for step, status in st.session_state.pipeline_status.items():
        step_class = 'pipeline-step'
        if status == 'active':
            step_class += ' active'
        elif status == 'completed':
            step_class += ' completed'
        elif status == 'error':
            step_class += ' error'
        pipeline_html += f'<div class="{step_class}">{step}</div>'
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)

# Main app layout
st.title("🗓️ Weekend Planner Assistant")
st.caption("Plan your perfect weekend with AI-powered recommendations")

# Pipeline area (show at top)
render_pipeline()

# Chat area
render_chat()

# Input area
with st.container():
    user_input = st.text_area("Your Message", placeholder="Type your request here...", height=100, key="user_input")
    if st.button("Send", disabled=st.session_state.processing):
        if user_input.strip():
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
