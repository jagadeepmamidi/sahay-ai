# Generate src/app.py - The Streamlit User Interface
app_content = '''"""
Sahay AI - Streamlit Web Application
====================================

A user-friendly web interface for the Sahay AI agent that helps users
understand PM-KISAN scheme benefits and procedures.

Author: Jagadeep Mamidi
Date: September 2025
"""

import streamlit as st
import time
from datetime import datetime

# Import our custom agent
from agent import ask_sahay_ai


def initialize_streamlit_config():
    """Configure Streamlit page settings and styling."""
    st.set_page_config(
        page_title="Sahay AI - PM-KISAN Assistant",
        page_icon="🙏",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        padding: 1rem 0;
        border-bottom: 2px solid #90EE90;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    
    .bot-message {
        background-color: #F1F8E9;
        border-left: 4px solid #4CAF50;
    }
    
    .info-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-box {
        text-align: center;
        padding: 1rem;
        background-color: #F5F5F5;
        border-radius: 8px;
        min-width: 120px;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
        
    if "app_start_time" not in st.session_state:
        st.session_state.app_start_time = datetime.now()


def display_welcome_section():
    """Display the main header and welcome information."""
    st.markdown("""
    <div class="main-header">
        <h1>🙏 Sahay AI</h1>
        <h3>Your Personal Guide to PM-KISAN Scheme</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message for new users
    if len(st.session_state.chat_messages) == 0:
        st.markdown("""
        <div class="info-box">
        <h4>🌾 Welcome to Sahay AI!</h4>
        <p>I'm here to help you understand the <strong>Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)</strong> scheme. 
        Ask me anything about:</p>
        <ul>
        <li>💰 Benefit amounts and payment schedules</li>
        <li>📋 Eligibility criteria and requirements</li>
        <li>📝 Application procedures and documentation</li>
        <li>🎯 Scheme objectives and coverage</li>
        <li>📊 Monitoring and implementation details</li>
        </ul>
        <p><em>Type your question below to get started!</em></p>
        </div>
        """, unsafe_allow_html=True)


def display_sidebar_info():
    """Display helpful information in the sidebar."""
    with st.sidebar:
        st.markdown("### 📊 Session Statistics")
        
        # Display session stats
        session_duration = datetime.now() - st.session_state.app_start_time
        
        st.markdown(f"""
        - **Total Questions**: {st.session_state.total_queries}
        - **Session Duration**: {str(session_duration).split('.')[0]}
        - **Messages**: {len(st.session_state.chat_messages)}
        """)
        
        st.markdown("---")
        
        st.markdown("### 💡 Sample Questions")
        sample_questions = [
            "What is PM-KISAN scheme?",
            "Who can apply for PM-KISAN benefits?",
            "How much money do farmers get?",
            "What documents are needed?",
            "When was PM-KISAN launched?",
            "How are payments made?",
            "What is the family definition?",
            "Are there any exclusions?"
        ]
        
        for question in sample_questions:
            if st.button(f"❓ {question}", key=f"sample_{question[:20]}"):
                st.session_state.current_question = question
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        ### 🔧 About Sahay AI
        
        **Technology Stack:**
        - 🧠 IBM WatsonX Granite LLM
        - 🔍 RAG with FAISS Vector DB
        - 🤗 HuggingFace Embeddings
        - ⚡ Streamlit Interface
        
        **Data Source:**
        Official PM-KISAN scheme documents from Government of India.
        
        ---
        
        **Built for:** Sahay AI Hackathon  
        **Author:** Jagadeep Mamidi
        """)


def display_chat_history():
    """Display the complete chat history."""
    if st.session_state.chat_messages:
        st.markdown("### 💬 Conversation History")
        
        for i, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Sahay AI:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)


def handle_user_input():
    """Handle user input and generate AI responses."""
    # Check if there's a question from sample questions
    current_question = getattr(st.session_state, 'current_question', None)
    
    # Get user input from chat input or sample question
    if current_question:
        user_question = current_question
        st.session_state.current_question = None  # Clear it
    else:
        user_question = st.chat_input("Ask me anything about PM-KISAN scheme...")
    
    if user_question:
        # Add user message to chat history
        st.session_state.chat_messages.append({
            "role": "user", 
            "content": user_question,
            "timestamp": datetime.now().isoformat()
        })
        
        # Increment query counter
        st.session_state.total_queries += 1
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_question)
        
        # Generate AI response with loading indicator
        with st.chat_message("assistant"):
            with st.spinner("🤔 Sahay AI is thinking..."):
                # Add a small delay for better UX
                time.sleep(0.5)
                
                try:
                    # Get response from our agent
                    ai_response = ask_sahay_ai(user_question)
                    
                    # Display the response
                    st.write(ai_response)
                    
                    # Add AI response to chat history
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    error_message = f"I apologize, but I encountered an error: {str(e)}. Please try again."
                    st.error(error_message)
                    
                    # Add error message to chat history
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": error_message,
                        "timestamp": datetime.now().isoformat()
                    })


def display_quick_actions():
    """Display quick action buttons for common tasks."""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col2:
        if st.button("📊 Show Stats", use_container_width=True):
            st.balloons()
            st.success(f"Total questions asked: {st.session_state.total_queries}")
    
    with col3:
        if st.button("❓ Get Help", use_container_width=True):
            help_message = """
            **How to use Sahay AI:**
            
            1. Type your question about PM-KISAN in the input box
            2. Press Enter or click Send
            3. Wait for Sahay AI to process and respond
            4. Continue the conversation naturally
            
            **Tips for better results:**
            - Be specific about what you want to know
            - Ask one question at a time
            - Use simple, clear language
            """
            st.info(help_message)


def main():
    """Main application function."""
    # Initialize Streamlit configuration
    initialize_streamlit_config()
    
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar information
    display_sidebar_info()
    
    # Display welcome section
    display_welcome_section()
    
    # Display chat history if any
    display_chat_history()
    
    # Handle user input and responses
    handle_user_input()
    
    # Display quick actions
    if len(st.session_state.chat_messages) > 0:
        st.markdown("---")
        display_quick_actions()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em;">
    🙏 Sahay AI - Empowering farmers with knowledge | Built with IBM WatsonX & Streamlit<br>
    For official PM-KISAN information, visit: <a href="https://pmkisan.gov.in" target="_blank">pmkisan.gov.in</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
'''

print("Generated src/app.py content")