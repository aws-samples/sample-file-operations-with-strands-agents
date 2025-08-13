"""
Copyright 2025 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

# Import required libraries for the Streamlit web application
import streamlit as st
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from strands import Agent
from strands_tools import use_aws, current_time
from file_organizer import file_organizer

# Agent initialization with caching for performance
# This function creates and caches the Agent to avoid recreating it on every request. The agent is configured with Claude 3.5 Haiku model and three tools for AWS operations, time queries, and file organization.
# This model can be replaced with model of your choice as long as you have access
@st.cache_resource
def get_agent():
    return Agent(model="anthropic.claude-3-5-haiku-20241022-v1:0", tools=[use_aws, current_time, file_organizer])

# Query execution with output capture
# This function executes user queries through the agent while capturing any stdout/stderr output. It ensures clean result handling by redirecting system outputs to buffers and returning only the agent's response.
def execute_query(agent, query):
    """Execute query and capture all output"""
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        result = agent(query)
    
    return str(result)

def main():
    # UI styling and layout configuration
    # This section applies custom CSS to improve the visual appearance and usability of the Streamlit interface. It reduces spacing between elements, ensures proper text visibility in text areas, and creates a more compact layout for better user experience.
    st.markdown("""
    <style>
    .stMarkdown p { margin-bottom: 0.3rem; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { margin-bottom: 0.5rem; }
    div.stButton > button { margin-top: 0.2rem; margin-bottom: 0.2rem; }
    .app-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; }
    /* Reduce font size in column containers */
    [data-testid="column"] .stMarkdown h3 { font-size: 1.1rem; }
    [data-testid="column"] .stMarkdown { font-size: 0.95rem; }
    /* Improve text area visibility - multiple selectors for better coverage */
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; }
    textarea[disabled] { color: #000000 !important; background-color: #ffffff !important; }
    .stTextArea > div > div > textarea { color: #000000 !important; }
    [data-testid="stTextArea"] textarea { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Application header and agent initialization
    # This section displays the main application title and description, then initializes the Strands Agents. It also sets up session state management to persist user queries across Streamlit reruns.
    st.markdown("<div class='app-title'>🔧 AWS and File Management Assistant powered by Strands Agents</div>", unsafe_allow_html=True)
    
    st.markdown("Manage AWS resources and organize files using natural language queries.")
    
    agent = get_agent()
    
    # Initialize session state for query
    if 'query' not in st.session_state:
        st.session_state.query = ""
    
    # AWS region selection dropdown
    # This dropdown allows users to select their preferred AWS region for resource queries. It provides access to 8 major AWS regions and defaults to us-east-1 for consistent user experience.
    region = st.selectbox(
        "🌍 Select AWS Region:",
        [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2", 
            "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"
        ],
        index=0
    )
    
    # Sidebar navigation with tips and quick actions
    # This sidebar provides user guidance, example queries, and quick action buttons for common operations. It helps users understand how to interact with the application and provides shortcuts for frequently used AWS operations.
    with st.sidebar:
        st.header("ℹ️ Helpful Tips")
        st.markdown("- Ensure AWS credentials are configured<br>- Verify Bedrock model access in selected region<br>- Use absolute paths for files<br>- Be specific in your queries", unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("💡 Example Queries")
        st.markdown("**S3:** List buckets starting with 'S'<br>**EC2:** Show instances in us-west-2<br>**Lambda:** What are your top functions?<br>**Cost:** Show my AWS bill summary<br>**Files:** Organize C:\\Users\\YourName\\TestFolder<br>**Time:** What is the current time?", unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("🚀 Quick Actions")
        
        # Quick action buttons for common AWS operations
        # These buttons provide one-click access to frequently used AWS queries like listing S3 buckets, EC2 instances, Lambda functions, and cost summaries. Each button sets a predefined query and triggers a rerun to execute it immediately.
        if st.button("🪣 All S3 Buckets", use_container_width=True):
            st.session_state.query = "List all my S3 buckets"
            st.rerun()
        if st.button("🪣 Buckets Starting with S", use_container_width=True):
            st.session_state.query = "List all buckets that start with S"
            st.rerun()
        if st.button("💻 All EC2 Instances", use_container_width=True):
            st.session_state.query = f"Show all EC2 instances in {region}"
            st.rerun()
        if st.button(f"💻 Running in {region}", use_container_width=True):
            st.session_state.query = f"How many instances are running in {region}?"
            st.rerun()
        if st.button("⚡ All Lambda Functions", use_container_width=True):
            st.session_state.query = f"List all Lambda functions in {region}"
            st.rerun()
        if st.button("⚡ Top Lambda Functions", use_container_width=True):
            st.session_state.query = f"What are your top Lambda functions in {region}?"
            st.rerun()
        if st.button("💰 Cost Summary", use_container_width=True):
            st.session_state.query = "Show my AWS cost summary"
            st.rerun()
        if st.button("🕐 Current Time", use_container_width=True):
            st.session_state.query = "What is the current time?"
            st.rerun()
    
    st.info(f"🌍 Selected Region: {region}")
    
    # Main content layout with two-column design
    # This section creates a side-by-side layout with AWS operations on the left and file organization on the right. The equal column widths provide balanced space for both functionalities.
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # AWS operations interface
        # This section provides the main interface for AWS resource queries with a text input field and execute button. It displays supported AWS services and handles query validation before execution.
        with st.container(border=True):
            st.markdown("### ☁️ AWS Operations")
            st.markdown("**Query your AWS resources:**<br>🪣 S3 buckets and storage<br>💻 EC2 instances and compute<br>⚡ Lambda functions and serverless", unsafe_allow_html=True)
            query = st.text_input("Ask your AWS question:", placeholder="List all buckets that start with S", value=st.session_state.query)
            
            if st.button("🚀 Execute AWS Query", type="primary"):
                if query:
                    st.session_state.query = query
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a query first")
    
    with col_right:
        # File organization interface
        # This section handles local file organization with a path input field and organize button. It explains how files will be categorized and provides examples of the sorting behavior users can expect.
        with st.container(border=True):
            st.markdown("### 📁 File Organization")
            st.markdown("**Files will be sorted into folders by type:**<br>📸 Images: .jpg, .png, .gif → Images/<br>📄 PDFs: .pdf → PDFs/<br>📝 Docs: .docx, .txt → Documents/", unsafe_allow_html=True)
            folder_path = st.text_input(
                "Enter folder path to organize:", 
                placeholder="C:\\Users\\YourName\\TestFolder",
                help="Enter the full path to the folder you want to organize"
            )
            
            if st.button("🚀 Organize This Folder", type="primary"):
                if folder_path:
                    st.session_state.query = f"Organize files in {folder_path}"
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a folder path first")

    # Session state synchronization
    # This ensures the session state stays synchronized with manual text input changes. It maintains query persistence across Streamlit reruns and prepares for query execution.
    if query != st.session_state.query:
        st.session_state.query = query
    
    # Query execution and results display
    # This section handles the actual execution of user queries and displays the results. It shows the current query being processed and provides visual feedback during execution.
    if st.session_state.query:
        st.markdown("---")
        st.info(f"🎯 Query: {st.session_state.query}")
        
        # Security filtering and query execution
        # This section implements security measures by blocking tool enumeration requests that could expose internal system information. For legitimate queries, it executes them through the agent with proper error handling and user feedback.
        query_lower = st.session_state.query.lower()
        tool_keywords = [
            'list tools', 'show tools', 'what tools', 'available tools', 'tool list',
            'tools available', 'display tools', 'get tools', 'all tools', 'tools list',
            'which tools', 'tools you have', 'your tools', 'help tools', 'tool help'
        ]
        
        if any(keyword in query_lower for keyword in tool_keywords):
            st.warning("🔒 I apologize, but I cannot provide a list of available tools for security reasons.")
            st.markdown("""
            **Instead, I can help you with these types of requests:**
            - "List S3 buckets"
            - "List EC2 instances in us-west-2"
            - "Show Lambda functions"
            - "Organize files in C:\\Users\\YourName\\TestFolder"
            - "What is the current time?"
            """)
        else:
            with st.spinner("Processing your AWS query..."):
                try:
                    result = execute_query(agent, st.session_state.query)
                    st.success("✅ Operation Complete")
                    st.markdown(f"**Result:**\n\n```\n{result}\n```")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()