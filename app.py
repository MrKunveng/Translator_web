# app.py

import streamlit as st
from translator import listen_and_translate, text_to_speech, get_audio_filename
import threading
import queue
import time
import os
from pathlib import Path
import hashlib
from deep_translator import GoogleTranslator

# Set page configuration
st.set_page_config(
    page_title="Real-Time Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 1rem;
    }
    .language-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .text-display {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 5px;
        min-height: 100px;
        border-left: 4px solid #1E88E5;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #757575;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Define available languages
languages = {
    'en': 'English 🇺🇸',
    'fr': 'French 🇫🇷',
    'es': 'Spanish 🇪🇸',
    'de': 'German 🇩🇪',
    'it': 'Italian 🇮🇹',
    'pt': 'Portuguese 🇵🇹',
    'ru': 'Russian 🇷🇺',
    'ja': 'Japanese 🇯🇵',
    'ko': 'Korean 🇰🇷',
    'zh': 'Chinese 🇨🇳'
}

def main():
    # Header
    st.markdown("<h1 class='main-header'>🌐 Real-Time Language Translator</h1>", unsafe_allow_html=True)
    st.markdown("Speak in one language and get instant translation to another language.")
    
    # Language selection in a nice box
    st.markdown("<div class='language-box'>", unsafe_allow_html=True)
    st.markdown("### Select Languages")
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("Source Language", list(languages.keys()), index=0, format_func=lambda x: languages[x])
    with col2:
        target_lang = st.selectbox("Target Language", list(languages.keys()), index=1, format_func=lambda x: languages[x])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Start/Stop translation buttons with better styling
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("🎙️ Start Translation", use_container_width=True)
    with col2:
        stop_button = st.button("⏹️ Stop Translation", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Initialize queues and translator thread
    input_queue = queue.Queue()
    output_queue = queue.Queue()
    translator_thread = None
    
    # In the main function, add a state variable to track audio playback
    if 'audio_playing' not in st.session_state:
        st.session_state.audio_playing = False
    if 'audio_start_time' not in st.session_state:
        st.session_state.audio_start_time = 0
    
    # Start translation if start button is pressed
    if start_button:
        if translator_thread is None:
            translator_thread = threading.Thread(target=listen_and_translate, args=(source_lang, target_lang, input_queue, output_queue), daemon=True)
            translator_thread.start()
            st.success("🎉 Translation started! Speak into your microphone.")
        else:
            st.warning("⚠️ Translation is already running.")
    
    # Stop translation if stop button is pressed
    if stop_button:
        if translator_thread is not None:
            # To stop the thread, we need to handle it properly, possibly using a kill flag
            # For simplicity, we'll just restart the app
            os._exit(0)
        else:
            st.warning("⚠️ No translation is running.")
    
    # Display areas for text
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='sub-header'>🗣️ Spoken Text</h3>", unsafe_allow_html=True)
        spoken_text_placeholder = st.empty()
        spoken_text_placeholder.markdown("<div class='text-display'>Waiting for speech input...</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3 class='sub-header'>🔄 Translated Text</h3>", unsafe_allow_html=True)
        translated_text_placeholder = st.empty()
        translated_text_placeholder.markdown("<div class='text-display'>Translation will appear here...</div>", unsafe_allow_html=True)
    
    # Audio player
    st.markdown("<h3 class='sub-header'>🔊 Audio Output</h3>", unsafe_allow_html=True)
    audio_placeholder = st.empty()
    
    # Continuously check for new input and output
    while True:
        if not input_queue.empty():
            spoken_text = input_queue.get()
            spoken_text_placeholder.markdown(f"<div class='text-display'>{spoken_text}</div>", unsafe_allow_html=True)
            # Translate the text
            try:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                translated = translator.translate(spoken_text)
                output_queue.put(translated)
                # Convert translated text to speech
                text_to_speech(translated, target_lang)
            except Exception as e:
                st.error(f"Translation error: {e}")
        
        if not output_queue.empty():
            translated_text = output_queue.get()
            translated_text_placeholder.markdown(f"<div class='text-display'>{translated_text}</div>", unsafe_allow_html=True)
            
            # Play the translated audio
            audio_file = get_audio_filename(translated_text, target_lang)
            if audio_file.exists():
                current_time = time.time()
                
                # If audio was playing and enough time has passed, clear it
                if st.session_state.audio_playing and (current_time - st.session_state.audio_start_time > 5):
                    audio_placeholder.empty()
                    st.session_state.audio_playing = False
                
                # Play new audio
                audio_placeholder.audio(str(audio_file), format='audio/mp3')
                st.session_state.audio_playing = True
                st.session_state.audio_start_time = current_time
        
        time.sleep(0.1)
    
    # Footer
    st.markdown("<div class='footer'>Powered by Google Translate and Speech Recognition</div>", unsafe_allow_html=True)

def get_audio_filename(text, target_lang):
    """
    Generates a unique filename for the audio based on text content.
    
    Args:
        text (str): The text to convert to audio.
        target_lang (str): The language code for the audio.
    
    Returns:
        Path: The file path for the audio file.
    """
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return Path("translation_cache") / f"audio_{target_lang}_{text_hash}.mp3"

if __name__ == "__main__":
    main()