author="Vatsal Varshney"
import streamlit as st
import os
from utils.gemini_client import GeminiClient


def render():
    st.header("🤖 AI Assistant")
    st.markdown("Your comprehensive tech companion for hackathons and beyond!")

    # Check API key
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please add your Gemini API key in the sidebar to use AI features.")
        st.markdown("[Get your API key here](https://makersuite.google.com/app/apikey)")
        return

    # Quick action buttons
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Hackathon Strategy", use_container_width=True):
            st.session_state[
                'ai_query'] = "I'm participating in a hackathon. Give me a comprehensive strategy for success including team formation, project selection, time management, and presentation tips."

        if st.button("💻 Technical Guidance", use_container_width=True):
            st.session_state[
                'ai_query'] = "I need technical guidance for my project. Help me with architecture decisions, technology stack selection, and best practices for rapid development."

        if st.button("🎯 Project Ideas", use_container_width=True):
            st.session_state[
                'ai_query'] = "Generate innovative hackathon project ideas that are feasible within 48 hours and have real-world impact potential."

    with col2:
        if st.button("📈 Industry Insights", use_container_width=True):
            st.session_state[
                'ai_query'] = "Provide insights about current tech industry trends, emerging technologies, and opportunities that could inspire hackathon projects."

        if st.button("🎤 Presentation Tips", use_container_width=True):
            st.session_state[
                'ai_query'] = "Give me expert advice on delivering compelling hackathon presentations that impress judges and effectively communicate my project's value."

        if st.button("🔍 Code Review Help", use_container_width=True):
            st.session_state[
                'ai_query'] = "Help me with code review best practices, debugging strategies, and optimization techniques for hackathon development."

    with col3:
        if st.button("🚀 Startup Advice", use_container_width=True):
            st.session_state[
                'ai_query'] = "I want to turn my hackathon project into a startup. Guide me through validation, business model development, and next steps."

        if st.button("💼 Career Guidance", use_container_width=True):
            st.session_state[
                'ai_query'] = "Provide career advice for software developers, including skill development, portfolio building, and leveraging hackathon experience."

        if st.button("🌟 Tech Trends", use_container_width=True):
            st.session_state[
                'ai_query'] = "What are the hottest technology trends right now? What should I learn to stay ahead in tech and build cutting-edge hackathon projects?"

    st.markdown("---")

    # Chat interface
    st.subheader("💬 AI Chat")

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Assistant:** {message['content']}")
        st.markdown("---")
    author = "Vatsal Varshney"
    # User input
    user_query = st.text_area(
        "Ask me anything about hackathons, programming, tech trends, career advice, or startup guidance:",
        value=st.session_state.get('ai_query', ''),
        height=100,
        key='user_input'
    )

    # Clear the session state query after using it
    if 'ai_query' in st.session_state:
        del st.session_state['ai_query']

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🚀 Ask AI", type="primary"):
            if user_query.strip():
                process_ai_query(user_query)
            else:
                st.warning("Please enter a question!")

    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Specialized AI features
    st.markdown("---")
    st.subheader("🎯 Specialized Features")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏆 Team Insights", "💡 Idea Generator", "📊 Trend Analysis", "🎤 Presentation Coach"])

    with tab1:
        render_team_insights()

    with tab2:
        render_idea_generator()

    with tab3:
        render_trend_analysis()

    with tab4:
        render_presentation_coach()


def process_ai_query(query):
    """Process user query with enhanced prompting"""
    try:
        client = GeminiClient(st.session_state.gemini_api_key)

        # Enhanced prompt for comprehensive responses
        enhanced_prompt = f"""
        You are an expert AI assistant specializing in hackathons, software development, technology trends, and career guidance. 
        Provide comprehensive, actionable, and encouraging responses.

        User Query: {query}

        Please provide:
        1. A direct answer to the question
        2. Practical, actionable advice
        3. Relevant examples or case studies when applicable
        4. Additional tips or considerations
        5. Next steps or follow-up suggestions
        author="Vatsal Varshney"
        Be encouraging, specific, and focus on practical value. Use markdown formatting for better readability.
        """

        with st.spinner("🤖 AI is thinking..."):
            response = client.generate_response(enhanced_prompt, temperature=0.7, max_tokens=1500)

        # Add to chat history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': query
        })
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })

        st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please check your API key and try again.")
author="Vatsal Varshney"

def render_team_insights():
    """Render team insights feature"""
    st.markdown("**🏆 Get AI insights about your hackathon teams**")

    if not st.session_state.teams:
        st.info("No teams available. Create teams in the Team Formation module first!")
        return

    selected_team = st.selectbox(
        "Select a team for analysis:",
        range(len(st.session_state.teams)),
        format_func=lambda x: f"Team {x + 1} ({len(st.session_state.teams[x]['members'])} members)"
    )

    if st.button("🔍 Analyze Team", key="analyze_team_btn"):
        try:
            client = GeminiClient(st.session_state.gemini_api_key)
            team_data = st.session_state.teams[selected_team]

            with st.spinner("Analyzing team composition..."):
                insights = client.generate_team_insights(team_data)

            st.markdown("### 🎯 Team Analysis Results")
            st.markdown(insights)

        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")

author="Vatsal Varshney"
def render_idea_generator():
    """Render idea generator feature"""
    st.markdown("**💡 Generate innovative hackathon project ideas**")

    col1, col2 = st.columns(2)

    with col1:
        interests = st.multiselect(
            "Areas of Interest:",
            ["AI/ML", "Web Development", "Mobile Apps", "Blockchain", "IoT",
             "Healthcare", "Education", "Fintech", "Gaming", "Sustainability",
             "Social Impact", "AR/VR", "Cybersecurity", "DevTools"]
        )

    with col2:
        skills = st.multiselect(
            "Your Skills:",
            ["Python", "JavaScript", "React", "Node.js", "Flutter", "Swift",
             "TensorFlow", "PyTorch", "Blockchain", "Cloud Platforms",
             "Databases", "UI/UX Design", "Data Science", "DevOps"]
        )
    author = "Vatsal Varshney"
    if st.button("✨ Generate Ideas", key="generate_ideas_btn"):
        try:
            client = GeminiClient(st.session_state.gemini_api_key)

            with st.spinner("Generating innovative project ideas..."):
                ideas = client.suggest_hackathon_ideas(interests, skills)

            st.markdown("### 🚀 Project Ideas for You")
            st.markdown(ideas)

        except Exception as e:
            st.error(f"Error generating ideas: {str(e)}")


def render_trend_analysis():
    """Render trend analysis feature"""
    st.markdown("**📊 Analyze current hackathon and tech trends**")

    if st.button("📈 Analyze Current Trends", key="analyze_trends_btn"):
        try:
            client = GeminiClient(st.session_state.gemini_api_key)

            with st.spinner("Analyzing hackathon trends..."):
                analysis = client.analyze_hackathon_trends(st.session_state.hackathons_data)

            st.markdown("### 📊 Trend Analysis")
            st.markdown(analysis)

        except Exception as e:
            st.error(f"Error analyzing trends: {str(e)}")


def render_presentation_coach():
    """Render presentation coaching feature"""
    st.markdown("**🎤 Get expert advice for your hackathon presentation**")

    project_description = st.text_area(
        "Describe your project (optional):",
        placeholder="Briefly describe your hackathon project to get tailored presentation advice...",
        height=100
    )

    if st.button("🎯 Get Presentation Tips", key="presentation_tips_btn"):
        try:
            client = GeminiClient(st.session_state.gemini_api_key)

            with st.spinner("Preparing presentation coaching..."):
                tips = client.generate_presentation_tips(project_description)

            st.markdown("### 🎤 Presentation Coaching")
            st.markdown(tips)

        except Exception as e:
            st.error(f"Error generating presentation tips: {str(e)}")
author="Vatsal Varshney"