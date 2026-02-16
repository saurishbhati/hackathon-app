import streamlit as st
import openai
from transformers import pipeline
import sqlite3
import datetime
#from twilio.rest import Client  # Uncomment if you wish to use Twilio for emergency alerts

# -------------------------------
# Initialize Sentiment Analysis
# -------------------------------
sentiment_analyzer = pipeline("sentiment-analysis")

# -------------------------------
# Set your OpenAI API key
# -------------------------------
openai.api_key = "key"  # Replace with your actual OpenAI API key

# -------------------------------
# Initialize Conversation History (in session state)
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "system", "content": "You are a compassionate and understanding mental health assistant. Engage in an empathetic conversation and provide thoughtful responses based on the user's emotional state."}
    ]

# -------------------------------
# Initialize (or connect to) the SQLite Database
# -------------------------------
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

def save_message(role, content):
    """Save a single message (role and content) to the database."""
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def show_conversation_history():
    """Retrieve and display the conversation history from the database."""
    cursor.execute("SELECT role, content, timestamp FROM chat_history ORDER BY id ASC")
    rows = cursor.fetchall()
    if rows:
        st.markdown("<h1 style='text-align: center;'>Conversation History</h1>", unsafe_allow_html=True)
        for row in rows:
            role, content, timestamp = row
            st.write(f"**{role.capitalize()}** ({timestamp}): {content}")
    else:
        st.info("No conversation history found.")

def show_mental_health_chatbot():
    st.markdown("<h1 style='text-align: center;'>Mental Health Chatbot</h1>", unsafe_allow_html=True)

    # Ensure session state is initialized before use
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "system", "content": "You are a compassionate and understanding mental health assistant. Engage in an empathetic conversation and provide thoughtful responses based on the user's emotional state."}
        ]

    st.write("""
    This is a 24/7 chat space. Please be open and honest, and type any issues on your mind here so we can help you out.
    """)

    # Chat input from the user
    user_input = st.text_area("Type your feelings or concerns here...", height=150)

    if st.button("Send to Chatbot", key="send_chatbot"):  # Unique key added
        if not user_input.strip():
            st.error("Please enter your feelings or concerns before sending.")
        else:
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            save_message("user", user_input)  # Save to the database

            # Call GPT-4 Turbo for a response
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=st.session_state["chat_history"],
                    temperature=0.9,
                    max_tokens=200
                )
                chatbot_reply = response.choices[0].message.content

                st.session_state["chat_history"].append({"role": "assistant", "content": chatbot_reply})
                save_message("assistant", chatbot_reply)  # Save to the database
            except Exception as e:
                st.error(f"Error communicating with the AI: {e}")
                return

            st.write("**Bot:**", chatbot_reply)

            sentiment = sentiment_analyzer(user_input)[0]
            print("Sentiment analysis:", sentiment)

            if sentiment["label"] == "NEGATIVE" and sentiment["score"] > 0.9:
                st.warning("We detect significant emotional distress. If you are in immediate danger, please call 911 immediately.")

        if st.button("Show Conversation History", key="show_history"):  # Unique key added
            show_conversation_history()



    # Button to display conversation history from the database
    if st.button("Show Conversation History"):
        show_conversation_history()


# To use this page, call show_mental_health_chatbot() in your main Streamlit app.
