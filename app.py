# app.py

import streamlit as st
import threading
import queue
from translator import listen_and_translate, text_to_speech, get_audio_filename
import os
import tempfile
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Real-Time Language Translator",
    page_icon="🌐",
    layout="wide"
)

# Define supported languages
LANGUAGES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-CN"
}

# Language flags
LANGUAGE_FLAGS = {
    "en": "🇺🇸",
    "fr": "🇫🇷",
    "es": "🇪🇸",
    "de": "🇩🇪",
    "it": "🇮🇹",
    "pt": "🇵🇹",
    "ru": "🇷🇺",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "zh-CN": "🇨🇳"
}

def main():
    # App title and description
    st.title("🌐 Real-Time Language Translator")
    st.markdown("Speak in one language, translate to another in real-time.")
    
    # Initialize session state
    if 'translation_active' not in st.session_state:
        st.session_state.translation_active = False
    if 'input_queue' not in st.session_state:
        st.session_state.input_queue = queue.Queue()
    if 'output_queue' not in st.session_state:
        st.session_state.output_queue = queue.Queue()
    if 'translation_thread' not in st.session_state:
        st.session_state.translation_thread = None
    
    # Language selection
    col1, col2 = st.columns(2)
    with col1:
        source_lang_name = st.selectbox(
            "Source Language",
            list(LANGUAGES.keys()),
            index=0
        )
        source_lang = LANGUAGES[source_lang_name]
        st.write(f"Selected: {LANGUAGE_FLAGS.get(source_lang, '')} {source_lang_name}")
    
    with col2:
        target_lang_name = st.selectbox(
            "Target Language",
            list(LANGUAGES.keys()),
            index=1
        )
        target_lang = LANGUAGES[target_lang_name]
        st.write(f"Selected: {LANGUAGE_FLAGS.get(target_lang, '')} {target_lang_name}")
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.translation_active:
            if st.button("Start Translation", type="primary", use_container_width=True):
                st.session_state.translation_active = True
                # Start translation in a separate thread
                st.session_state.translation_thread = threading.Thread(
                    target=listen_and_translate,
                    args=(source_lang, target_lang, st.session_state.input_queue, st.session_state.output_queue),
                    daemon=True
                )
                st.session_state.translation_thread.start()
                st.rerun()
    with col2:
        if st.session_state.translation_active:
            if st.button("Stop Translation", type="secondary", use_container_width=True):
                st.session_state.translation_active = False
                # Clear queues
                while not st.session_state.input_queue.empty():
                    st.session_state.input_queue.get()
                while not st.session_state.output_queue.empty():
                    st.session_state.output_queue.get()
                st.rerun()
    
    # Display translation status
    if st.session_state.translation_active:
        st.success("Translation is active. Speak into your microphone.")
        
        # Create placeholders for recognized and translated text
        recognized_placeholder = st.empty()
        translated_placeholder = st.empty()
        
        # Check for new translations
        try:
            if not st.session_state.output_queue.empty():
                recognized_text, translated_text = st.session_state.output_queue.get(block=False)
                
                # Display recognized text
                with recognized_placeholder.container():
                    st.markdown("### Recognized Speech")
                    st.markdown(f"**{LANGUAGE_FLAGS.get(source_lang, '')} {source_lang_name}:** {recognized_text}")
                
                # Display translated text
                with translated_placeholder.container():
                    st.markdown("### Translation")
                    st.markdown(f"**{LANGUAGE_FLAGS.get(target_lang, '')} {target_lang_name}:** {translated_text}")
                
                # Play the translation
                try:
                    # Get audio file path without playing it
                    audio_file = get_audio_filename(translated_text, target_lang)
                    
                    # Check if file exists
                    if audio_file.exists():
                        st.audio(str(audio_file))
                    else:
                        # Generate the audio file
                        from gtts import gTTS
                        tts = gTTS(text=translated_text, lang=target_lang)
                        tts.save(str(audio_file))
                        st.audio(str(audio_file))
                except Exception as e:
                    st.warning(f"Could not play audio: {str(e)}")
                    st.info("Audio playback requires ffmpeg to be installed.")
        except Exception as e:
            st.error(f"Error processing translation: {str(e)}")
    
    # Manual text translation section
    st.markdown("---")
    st.markdown("### Manual Text Translation")
    
    manual_text = st.text_area("Enter text to translate:", height=100)
    if st.button("Translate Text", type="primary"):
        if manual_text:
            try:
                # Use the same translation function but with manual text
                st.session_state.input_queue.put(manual_text)
                
                # Create a temporary thread for manual translation
                temp_thread = threading.Thread(
                    target=listen_and_translate,
                    args=(source_lang, target_lang, st.session_state.input_queue, st.session_state.output_queue),
                    daemon=True
                )
                temp_thread.start()
                
                # Wait for translation to complete
                temp_thread.join(timeout=5)
                
                # Get the translation result
                if not st.session_state.output_queue.empty():
                    recognized_text, translated_text = st.session_state.output_queue.get(block=False)
                    
                    st.markdown("### Translation Result")
                    st.markdown(f"**{LANGUAGE_FLAGS.get(target_lang, '')} {target_lang_name}:** {translated_text}")
                    
                    # Play the translation
                    try:
                        # Get audio file path without playing it
                        audio_file = get_audio_filename(translated_text, target_lang)
                        
                        # Check if file exists
                        if audio_file.exists():
                            st.audio(str(audio_file))
                        else:
                            # Generate the audio file
                            from gtts import gTTS
                            tts = gTTS(text=translated_text, lang=target_lang)
                            tts.save(str(audio_file))
                            st.audio(str(audio_file))
                    except Exception as e:
                        st.warning(f"Could not play audio: {str(e)}")
                        st.info("Audio playback requires ffmpeg to be installed.")
            except Exception as e:
                st.error(f"Error translating text: {str(e)}")
        else:
            st.warning("Please enter text to translate.")
    
    # App information
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This application uses:
    - Google's Speech Recognition API for speech-to-text
    - Google Translate for translation
    - Google Text-to-Speech for audio output
    
    For best results, speak clearly and in a quiet environment.
    """)

if __name__ == "__main__":
    main()
