import streamlit as st
from dotenv import load_dotenv
import os
import sentry_sdk
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Sentry
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))

# Page config
st.set_page_config(
    page_title="Real-Time Translation App",
    page_icon="🌎",
    layout="wide"
)

# Session state initialization
if 'meetings' not in st.session_state:
    st.session_state.meetings = []

def create_meeting():
    meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.meetings.append({
        'meeting_id': meeting_id,
        'created_at': datetime.now(),
        'host_language': st.session_state.host_language,
        'participant_language': st.session_state.participant_language,
    })
    return meeting_id

# Main UI
st.title("Real-Time Translation App 🌎")

# Sidebar for language selection
with st.sidebar:
    st.header("Language Settings")
    st.session_state.host_language = st.selectbox(
        "Your Language",
        ["English", "Spanish", "French", "German", "Chinese"],
        key="host_lang"
    )
    st.session_state.participant_language = st.selectbox(
        "Participant's Language",
        ["English", "Spanish", "French", "German", "Chinese"],
        key="participant_lang"
    )
    
    if st.button("Create New Meeting"):
        meeting_id = create_meeting()
        st.success(f"Meeting created! ID: {meeting_id}")

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.header("Your Speech")
    st.text_area("Your message", key="host_message", height=200)
    if st.button("Send"):
        # Here you would implement the translation and sending logic
        st.success("Message sent and translated!")

with col2:
    st.header("Participant's Speech")
    st.text_area("Received messages", key="received_messages", height=200, disabled=True)

# Display active meetings
st.header("Active Meetings")
if st.session_state.meetings:
    for meeting in st.session_state.meetings:
        st.write(f"Meeting ID: {meeting['meeting_id']}")
        st.write(f"Created: {meeting['created_at']}")
        st.write(f"Languages: {meeting['host_language']} ↔ {meeting['participant_language']}")
        st.divider()
else:
    st.info("No active meetings. Create one using the sidebar!") 