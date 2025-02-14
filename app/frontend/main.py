import streamlit as st
import requests
import json

# Configure API endpoint
API_BASE_URL = "http://127.0.0.1:5000"

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
            data = {
                "email": email,
                "password": password,
                "username": username,
                "phone": phone
            }
            if admin_code:
                data["admin_code"] = admin_code

            response = requests.post(f"{API_BASE_URL}/signup", json=data)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json().get("error", "Signup failed"))

def login():
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["token"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(response.json().get("error", "Login failed"))

def display_articles():
    st.subheader("Articles")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_BASE_URL}/articles", headers=headers)
    
    if response.status_code == 200:
        articles = response.json()
        
        # Get user progress first
        progress_response = requests.get(f"{API_BASE_URL}/user/progress", headers=headers)
        if progress_response.status_code == 200:
            completed_questions = {entry['question_id'] for entry in progress_response.json()}
            st.session_state.completed_questions = completed_questions
        
        for idx, article in enumerate(articles):
            with st.expander(f"📚 {article['title']}"):
                st.write(article['content'])
                st.write(f"Category: {article['category']}")
                
                questions_response = requests.get(
                    f"{API_BASE_URL}/articles/{article['id']}/questions",
                    headers=headers
                )
                if questions_response.status_code == 200:
                    questions = questions_response.json()["related_questions"]
                    if questions:
                        st.subheader("Practice Questions")
                        for qidx, question in enumerate(questions):
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(f"🔗 [{question['title']}]({question['link']})")
                            with col2:
                                st.write(f"Difficulty: {question['difficulty']}")
                            with col3:
                                button_key = f"btn_{article['id']}_{question['id']}_{idx}_{qidx}"
                                if question['id'] in st.session_state.completed_questions:
                                    st.success("✅ Completed")
                                else:
                                    if st.button("Mark as Done", key=button_key):
                                        mark_response = requests.post(
                                            f"{API_BASE_URL}/questions/{question['id']}/mark-read",
                                            headers=headers
                                        )
                                        if mark_response.status_code == 200:
                                            st.session_state.completed_questions.add(question['id'])
                                            st.rerun()
                                        else:
                                            st.error("Failed to mark as completed")

def show_progress():
    st.subheader("Your Progress")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_BASE_URL}/user/progress", headers=headers)
    
    if response.status_code == 200:
        progress = response.json()
        total = len(progress)
        st.metric("Total Questions Completed", total)
        
        if total > 0:
            st.subheader("Completed Questions")
            for entry in progress:
                st.success(f"✅ Question ID: {entry['question_id']}")
        else:
            st.info("No questions completed yet. Start solving problems to track your progress!")

def main():
    st.set_page_config(page_title="DSA Tutor", layout="wide")
    st.title("DSA Tutor")
    init_session_state()

    if st.session_state.token is None:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login()
        with tab2:
            signup()
    else:
        st.sidebar.success("Logged in successfully!")
        if st.sidebar.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

        tab1, tab2 = st.tabs(["Articles & Questions", "Progress"])
        with tab1:
            display_articles()
        with tab2:
            show_progress()

if __name__ == "__main__":
    main()