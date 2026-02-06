import streamlit as st
import cv2
import pyttsx3
import os
from google import genai
from google.genai import types

# --- 1. CONFIG & IMAGE-MATCHED STYLING ---
st.set_page_config(page_title="HandyTalk AI", layout="wide", page_icon="🤟")

st.markdown("""
    <style>
    /* Dark Premium Background */
    .main { 
        background-color: #0f1116; 
        color: white; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Branded Glow Header */
    .header-container { text-align: center; padding: 20px 0px; }
    .logo-text { 
        font-size: 75px; font-weight: 800; color: #00f2fe; 
        text-shadow: 0 0 25px rgba(0, 242, 254, 0.8); 
        margin-bottom: 0px;
    }
    .tagline { color: #8E2DE2; font-size: 1.4rem; font-weight: 500; margin-top: -15px; }

    /* THE EXTERNAL CONTAINERS: Styling the Signer & Listener boxes */
    div[data-testid="column"] {
        background: rgba(22, 25, 31, 0.95) !important;
        border: 1px solid rgba(45, 49, 57, 1) !important;
        border-radius: 25px !important;
        padding: 45px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6) !important;
        margin-bottom: 20px !important;
        min-height: 650px;
    }

    /* Elegant Thinner Buttons (Startup Look) */
    .stButton>button { 
        background: linear-gradient(90deg, #8E2DE2 0%, #00f2fe 100%) !important; 
        color: white !important; border: none !important; border-radius: 30px !important; 
        font-weight: 600 !important; height: 2.8em !important; font-size: 0.95rem !important;
        transition: 0.3s !important; margin-top: 20px !important;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 242, 254, 0.4); }
    
    [data-testid="stSidebar"] { background-color: #11141a !important; border-right: 1px solid #2d3139 !important; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION ---
GEMINI_KEY = os.getenv("GEMINI_KEY")
if not GEMINI_KEY:
    st.error("GEMINI_KEY is not set. Add it as an environment variable (do not put it in code).")
    st.stop()

client = genai.Client(api_key=GEMINI_KEY)
engine = pyttsx3.init()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00f2fe;'>🤟 HandyTalk</h2>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.radio("Navigation", ["Home / Translator", "Sign Library", "About Project"])
    st.markdown("---")
    st.info("Built for Gemini 3 Hackathon 2026")

# --- 4. BRANDED HEADER ---
st.markdown("<div class='header-container'><div class='logo-text'>HandyTalk</div><div class='tagline'>Bridging Silence with Gemini 3 AI</div></div>", unsafe_allow_html=True)

# --- 5. MAIN PAGE: TRANSLATOR ---
if choice == "Home / Translator":
    # These two columns will act as the 'external boxes'
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("🧏🏻 Signer")
        context_hint = st.selectbox("Set Context", ["General Chat", "Health & Habits", "Emergency", "Food/Daily Needs"])
        uploaded_file = st.file_uploader("Upload Sign Video", type=['mp4', 'mov'])
        
        if uploaded_file:
            st.video(uploaded_file)
            if st.button("✨ Translate Sign"):
                video_bytes = uploaded_file.read()
                try:
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=[f"Translate this sign video about {context_hint}", 
                                  types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")]
                    )
                    st.success(f"Result: {response.text}")
                    engine.say(response.text)
                    engine.runAndWait()
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.subheader("🔊 Listener")
        
        # Smart Matching Logic: Checks folder directly, then synonyms
        synonyms = {
            "hi": "hello", "hey": "hello", "greet": "hello",
            "thx": "thankyou", "thanks": "thankyou", "thank you": "thankyou",
            "aid": "help", "emergency": "help", "assist": "help"
        }
        
        user_input = st.text_input("Type your response:", key="listener_box")
        submit_listener = st.button("🚀 Send to Signer")

        if user_input or submit_listener:
            clean_text = user_input.lower().strip()
            words = clean_text.split()
            target_file = None
            
            # Match check: whole phrase -> individual word -> synonym
            if clean_text in synonyms:
                target_file = synonyms[clean_text]
            if not target_file:
                for word in words:
                    w = "".join(filter(str.isalnum, word))
                    if os.path.exists(f"signs/{w}.mp4"):
                        target_file = w
                        break
                    elif w in synonyms:
                        target_file = synonyms[w]
                        break

            if target_file and os.path.exists(f"signs/{target_file}.mp4"):
                st.info(f"Visualizing: '{target_file}'")
                st.video(f"signs/{target_file}.mp4")
            elif user_input:
                st.warning(f"Could not find a sign for '{user_input}'.")

# --- 6. SIGN LIBRARY (Tiles only, no extra buttons) ---
elif choice == "Sign Library":
    st.title("📚 Sign Dictionary")
    if os.path.exists("signs"):
        available = [f.split('.')[0] for f in os.listdir("signs") if f.endswith(".mp4")]
        cols = st.columns(4)
        for i, sign in enumerate(available):
            with cols[i % 4]:
                if st.button(f"🤟 {sign.upper()}", key=f"lib_{sign}"):
                    st.video(f"signs/{sign}.mp4")


# --- 7. ABOUT PROJECT (Final Polished Version) ---
elif choice == "About Project":
    st.title("ℹ️ About HandyTalk")
    
    st.markdown("""
    ### The Vision
    **HandyTalk** was created to bridge the communication gap for the speech and hearing-impaired. 
    It focuses on moving beyond robotic, one-way translation to create a meaningful two-way dialogue.
    
    ### The Solution
    Using **Gemini 3's native multimodality**, this project demonstrates how we can:
    1.  **See** movement and intent in sign language.
    2.  **Speak** the translation clearly to a hearing person.
    3.  **Visualize** responses back in sign language for the user.

    ### Tech Stack
    - **Frontend:** Streamlit (Python 3.13)
    - **Brain:** Gemini 3 Flash (Vision/Video Reasoning)
    - **Roadmap:** High-speed C++ logic for real-time 'Open Camera' processing (Planned for production).
    """)

    # --- The Collection (Developer's Note) ---
    st.markdown("---")
    st.info("""
    **Developer's Note:** This project is a demonstration of a core idea. Building a production-ready, industry-level version of 
    HandyTalk requires massive datasets, specialized engineering, and high-performance computing resources 
    beyond the scope of a hackathon. This is an exploration of what can be achieved by a student 
    leveraging the power of Generative AI.
    """)
    # --- The Signature Line ---
    st.markdown("---")
    st.markdown("<center><b>Developed by Diksha Sirohi with Gemini | Gemini 3 Hackathon 2026</b></center>", unsafe_allow_html=True)