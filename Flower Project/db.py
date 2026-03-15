import streamlit as st
from supabase import create_client
from hashlib import sha256

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def hash_password(password):
    return sha256(password.encode()).hexdigest()


def check_username_exists(username):
    """Check if username already exists in database"""
    if not username or len(username.strip()) == 0:
        return False
    
    try:
        res = supabase.table("users").select("username").eq("username", username.strip()).execute()
        return res.data and len(res.data) > 0
    except Exception:
        return False


def register_user(username, password, security_q, security_a):
    # Check if username already exists
    if check_username_exists(username):
        return False, "Username already exists. Please try another one."
    
    data = {
        "username": username.strip(),
        "password": hash_password(password),
        "security_q": security_q,
        "security_a": security_a.lower().strip()
    }

    try:
        response = supabase.table("users").insert(data).execute()
        if response.data:
            return True, "Registration successful!"
        else:
            return False, "Registration failed. Please try again."
            
    except Exception as e:
        error_str = str(e).lower()
        if "23505" in str(e) or "duplicate" in error_str or "unique" in error_str:
            return False, "Username already exists. Please try another one."
        return False, f"Registration failed: {str(e)}"


def verify_login(username, password):
    try:
        res = supabase.table("users").select("password").eq("username", username.strip()).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["password"] == hash_password(password)
        return False
    except Exception:
        return False


def get_security_question(username):
    try:
        res = supabase.table("users").select("security_q").eq("username", username.strip()).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["security_q"]
        return None
    except Exception:
        return None


def verify_security_answer(username, answer):
    try:
        res = supabase.table("users").select("security_a").eq("username", username.strip()).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["security_a"] == answer.lower().strip()
        return False
    except Exception:
        return False


def reset_password(username, new_password):
    try:
        supabase.table("users").update({
            "password": hash_password(new_password)
        }).eq("username", username.strip()).execute()
        return True
    except Exception:
        return False