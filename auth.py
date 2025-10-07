import streamlit as st
import bcrypt
from database import FinanceDatabase

def check_auth():
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)

def login(username, password):
    """Authenticate user with database."""
    db = FinanceDatabase()
    user = db.get_user_by_username(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_id = user['id']
        return True
    return False

def signup(username, password):
    """Register a new user."""
    if not username or not password:
        return False, "Username and password are required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    db = FinanceDatabase()
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.create_user(username, hashed)
        return True, "Account created successfully! You can now log in."
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, "Failed to create account"

def logout():
    """Log out the user."""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'username' in st.session_state:
        del st.session_state.username
    if 'user_id' in st.session_state:
        del st.session_state.user_id
    st.rerun()

def login_page():
    """Display the login/signup page."""
    st.title("🔐 Finance Tracker Authentication")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.markdown("### Login to your account")

        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            submitted = st.form_submit_button("Login")

            if submitted:
                if login(username, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

    with tab2:
        st.markdown("### Create a new account")

        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    success, message = signup(new_username, new_password)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")

def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if not check_auth():
            login_page()
            return
        return func(*args, **kwargs)
    return wrapper

def show_auth_status():
    """Show authentication status in sidebar."""
    if check_auth():
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.sidebar.button("Logout"):
            logout()
    else:
        st.sidebar.markdown("**Not logged in**")