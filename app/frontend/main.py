import streamlit as st
import requests
import json
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "http://127.0.0.1:5000"  # Base URL without /api
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Make sure this is set in your .env file

def init_session_state():
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'completed_questions' not in st.session_state:
        st.session_state.completed_questions = set()

def signup():
    st.subheader("Sign Up")
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        username = st.text_input("Username")
        phone = st.text_input("Phone")
        admin_code = st.text_input("Admin Code (Optional)", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not email or not password or not username or not phone:
                st.error("All fields are required except Admin Code")
                return

            data = {
                "email": email,
                "password": password,
                "username": username,
                "phone": phone
            }
            if admin_code:
                data["admin_code"] = admin_code

            try:
                response = requests.post(
                    f"{API_BASE_URL}/users/signup",
                    headers={"Content-Type": "application/json"},
                    json=data
                )
                
                if response.status_code == 200:
                    st.success("Signup successful! Please check your email for verification.")
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error occurred")
                        st.error(f"Signup failed: {error_msg}")
                    except ValueError:
                        st.error(f"Signup failed: {response.text}")
                        
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Unable to connect to server. Please check your internet connection.")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Network error: {str(e)}")

def login():
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/users/login",  # Fixed endpoint path
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "email": email,
                        "password": password
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "token" in data:
                        st.session_state.token = data["token"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid response from server: missing token")
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error occurred")
                        st.error(f"Login failed: {error_msg}")
                    except ValueError:
                        st.error(f"Login failed: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Unable to connect to server. Please check your internet connection.")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Network error: {str(e)}")
            except ValueError as e:
                st.error(f"⚠️ Invalid response format: {str(e)}")

def display_articles():
    st.header("Learning Resources")
    
    if 'token' not in st.session_state or not st.session_state.token:
        st.error("Please login first")
        return
        
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/articles",
            headers=headers,
            timeout=10  # Add timeout
        )
        
        if response.status_code == 200:
            try:
                articles = response.json()
                if not articles:
                    st.info("No articles available yet.")
                else:
                    for article in articles:
                        with st.expander(f"📚 {article.get('title', 'Untitled')}"):
                            st.markdown(article.get('content', 'No content available'))
            except ValueError:
                st.error("Invalid response format from server")
        elif response.status_code == 401:
            st.error("Session expired. Please login again")
            st.session_state.token = None
            st.rerun()
        else:
            st.error(f"Error fetching articles: {response.text}")
            
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to server. Please check your internet connection.")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

def display_progress():
    st.header("📊 Learning Analytics")
    
    if 'token' not in st.session_state:
        st.error("Please login first")
        return
        
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/user/progress",
            headers=headers
        )
        
        if response.status_code == 200:
            progress_data = response.json()
            st.write("Your Learning Progress:", progress_data)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        st.error(f"Error fetching progress: {str(e)}")

def main():
    # Configure page with dark theme and wide layout
    st.set_page_config(
        page_title="DSA Tutor Pro",
        page_icon="👽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS for a more technical look
    st.markdown("""
        <style>
        .main {
            background-color: #0E1117;
        }
        .stButton button {
            background-color: #3B71CA;
            color: white;
            border-radius: 5px;
            transition: transform 0.2s ease, background-color 0.2s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            background-color: #2C5282;
        }
        
        /* Animated logo */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 0rem;
            padding: 1rem 0;
            margin-bottom: 0;
            animation: fadeIn 0.8s ease-out;
        }
        
        .logo-icon {
            font-size: 4.5rem;
            margin-right: -0.8rem;
            margin-left: -0.5rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .logo-text {
            font-weight: 900;
            color: #FFFFFF;
            font-size: 3rem;
            margin-bottom: 1rem;
            letter-spacing: -1px;
            margin-left: 0.7rem;
            animation: fadeIn 0.8s ease-out;
        }
        
        /* Animated cards */
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .stExpander {
            border: 1px solid #2E3440;
            border-radius: 8px;
            margin-bottom: 10px;
            animation: slideIn 0.5s ease-out;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stExpander:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Progress bar animation */
        @keyframes progressFill {
            from { width: 0; }
            to { width: 100%; }
        }
        
        /* Success message animation */
        @keyframes pulseSuccess {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .success {
            padding: 1rem;
            border-radius: 5px;
            background-color: #1E2749;
            animation: pulseSuccess 2s infinite;
        }
        
        /* Metric animations */
        .stMetric {
            transition: transform 0.3s ease;
        }
        
        .stMetric:hover {
            transform: scale(1.05);
        }
        
        /* Tab animations */
        .stTabs {
            transition: opacity 0.3s ease;
        }
        
        .stTab {
            transition: all 0.3s ease;
        }
        
        .stTab:hover {
            transform: translateY(-2px);
        }
        
        /* Search bar animation */
        .stTextInput input {
            border: 1px solid #3B71CA;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            transform: scale(1.01);
            box-shadow: 0 0 15px rgba(59, 113, 202, 0.2);
        }
        
        /* Category tag animation */
        .category-tag {
            background-color: #1E2749;
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            color: #3B71CA;
            transition: all 0.3s ease;
        }
        
        .category-tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Logo subtitle animation */
        .logo-subtitle {
            color: #6C757D;
            font-size: 1rem;
            margin-top: -1rem;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-out 0.3s backwards;
        }
        
        /* Sidebar logo */
        .sidebar-logo {
            font-size: 3rem;
            margin-right: 0rem;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 2rem;
            margin-bottom: 2rem;
            width: 100%;
        }
        
        .title-section {
            flex: 0 0 auto;
            margin-right: auto;
        }
        
        .quote-container {
            flex: 0 0 50%;
            background: linear-gradient(135deg, rgba(30, 39, 73, 0.6), rgba(44, 62, 80, 0.6));
            border: 1px solid rgba(59, 113, 202, 0.3);
            border-radius: 15px;
            padding: 15px 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(59, 113, 202, 0.1);
            animation: glow 3s infinite alternate;
            margin-top: 10px;
            margin-right: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.token is None:
        # Logo and Title for login page
        col1, col2 = st.columns([0.25, 5])
        with col1:
            st.markdown('<div class="logo-icon">👽</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="logo-text">DSA Tutor Pro</div>', unsafe_allow_html=True)
            st.markdown('<div class="logo-subtitle">Master Data Structures & Algorithms</div>', unsafe_allow_html=True)

        # Login page content
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.container():
                st.markdown("""
                    ### 🚀 Welcome to DSA Tutor Pro
                    Your personal guide to mastering algorithms
                    
                    - 📚 Curated DSA content
                    - 💡 Interactive learning
                    - 📊 Progress tracking
                    - 🤖 AI-powered assistance
                    - ⚡ Real-time feedback
                    - 🎯 Targeted practice
                """)
        with col2:
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
            with tab1:
                login()
            with tab2:
                signup()
    else:
        # Combined header with logo and quote
        st.markdown("""
            <div class="header-container">
                <div class="title-section">
                    <div class="logo-container">
                        <div class="logo-icon">👽</div>
                        <div>
                            <div class="logo-text">DSA Tutor Pro</div>
                            <div class="logo-subtitle">Master Data Structures & Algorithms</div>
                        </div>
                    </div>
                </div>
                <div class="quote-container">
                    <div class="quote-header">
                        <span class="tech-icon">⚡</span>Code of the Day
                    </div>
                    <div class="quote-text">
                        "First, solve the problem. Then, write the code."
                    </div>
                    <div class="quote-author">
                        - John Johnson
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Sidebar with user info and stats
        with st.sidebar:
            st.markdown("""
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <div class="logo-text" style='font-size: 2rem;'><span class="sidebar-logo">👽</span> DSA Pro</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 👤 User Dashboard")
            st.success("🟢 Logged in successfully!")
            
            # Add quick stats in sidebar
            st.markdown("### 📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Questions", len(st.session_state.completed_questions))
            with col2:
                progress_percent = len(st.session_state.completed_questions) * 100 / 50  # Assuming 50 total questions
                st.metric("Progress", f"{progress_percent:.1f}%")
            
            if st.button("🚪 Logout", type="primary"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

        # Main content area
        tab1, tab2 = st.tabs(["📚 Learning Hub", "📈 Progress Analytics"])
        with tab1:
            display_articles()
        with tab2:
            display_progress()

if __name__ == "__main__":
    main()