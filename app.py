author="Vatsal Varshney"
import streamlit as st
import os
from modules import hackathon_discovery, ai_assistant, team_formation, idea_board

# Set page configuration
st.set_page_config(
    page_title="HackHub - Complete Hackathon Platform"
               "author=Vatsal Varshney",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for shared data
if 'hackathons_data' not in st.session_state:
    st.session_state.hackathons_data = []
if 'participants' not in st.session_state:
    st.session_state.participants = []
if 'teams' not in st.session_state:
    st.session_state.teams = []
if 'ideas' not in st.session_state:
    st.session_state.ideas = []
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")


def main():
    # Creator attribution - appears on every page
    st.markdown("""
    <div style="position: fixed; top: 10px; right: 10px; z-index: 999; 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                color: white; padding: 8px 15px; border-radius: 25px; 
                font-weight: bold; font-size: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                animation: glow 2s ease-in-out infinite alternate;">
        🚀 Created by Vatsal Varshney
    </div>
    <style>
    @keyframes glow {
        from { box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        to { box-shadow: 0 6px 25px rgba(255,107,107,0.4); }
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #FF6B35; margin: 0;">🚀 HackHub</h1>
        <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 1.2rem;">Your Complete Hackathon Platform</p>
        <p style="color: #888; margin: 0; font-size: 0.9rem;">Discover • Connect • Create • Compete</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")

    # API Key setup in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 API Configuration")
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Enter your Google Gemini API key for AI features"
    )

    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key

    if not api_key:
        st.sidebar.info("💡 Add your Gemini API key to enable AI features!")
        st.sidebar.markdown("[Get API Key](https://makersuite.google.com/app/apikey)")
    else:
        st.sidebar.success("✅ API Key configured!")

    st.sidebar.markdown("---")

    # Navigation menu
    page = st.sidebar.radio(
        "Choose Module",
        [
            "🔍 Hackathon Discovery",
            "💡 Idea Board",
            "👥 Team Formation",
            "🤖 AI Assistant"
        ]
    )

    # Platform stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Platform Stats")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Hackathons", len(st.session_state.hackathons_data))
        st.metric("Ideas", len(st.session_state.ideas))
    with col2:
        st.metric("Participants", len(st.session_state.participants))
        st.metric("Teams", len(st.session_state.teams))

    # Route to appropriate module
    if page == "🔍 Hackathon Discovery":
        hackathon_discovery.render()
    elif page == "💡 Idea Board":
        idea_board.render()
    elif page == "👥 Team Formation":
        team_formation.render()
    elif page == "🤖 AI Assistant":
        ai_assistant.render()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem 0;">
        <p>Built By VATSAL VARSHNEY</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()