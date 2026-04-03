import streamlit as st
import json
from pathlib import Path
USER_FILE = Path("users.json")

if not USER_FILE.exists():
    with open(USER_FILE, "w") as f:
        json.dump([], f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

def register(username, password, role):
    users = load_users()
    
    for user in users:
        if user["username"] == username:
            return False, "Username already exists"
    
    users.append({
        "username": username,
        "password": password,
        "role": role
    })
    
    save_users(users)
    return True, "Account created successfully"

def login(username, password):
    users = load_users()
    
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True, user
    
    return False, None

if not st.session_state.logged_in:
    st.title(" Login System")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, user = login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        role = st.selectbox("Select Role", ["user", "admin"])

        if st.button("Register"):
            success, message = register(new_user, new_pass, role)
            if success:
                st.success(message)
            else:
                st.error(message)

else:
    user = st.session_state.user

    st.sidebar.title(f"Welcome, {user['username']}")
    
    page = st.sidebar.radio("Navigation", ["Dashboard", "Profile", "Settings", "Logout"])

    if page == "Dashboard":
        st.title(" Dashboard")

        if user["role"] == "admin":
            st.subheader("Admin Dashboard")
            st.write("You have full access.")
        else:
            st.subheader("User Dashboard")
            st.write("Limited access.")

    elif page == "Profile":
        st.title(" Profile")
        st.write(f"Username: {user['username']}")
        st.write(f"Role: {user['role']}")

    elif page == "Settings":
        st.title(" Settings")
        st.write("Settings page (you can expand this)")

    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Logged out")
        st.rerun()
