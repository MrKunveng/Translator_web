# Real-Time Language Translator

A real-time speech translation application built with Python, Streamlit, and Google's translation services.

## Features

- Real-time speech recognition in multiple languages
- Instant translation between 10 languages
- Text-to-speech output of translations
- Clean, modern user interface
- Audio caching for improved performance

## Supported Languages

- English 🇺🇸
- French 🇫🇷
- Spanish 🇪🇸
- German 🇩🇪
- Italian 🇮🇹
- Portuguese 🇵🇹
- Russian 🇷🇺
- Japanese 🇯🇵
- Korean 🇰🇷
- Chinese 🇨🇳

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/real-time-translator.git
   cd real-time-translator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Select your source and target languages from the dropdown menus
2. Click "Start Translation" to begin
3. Speak into your microphone in the source language
4. The application will display the recognized speech, translate it, and play the translation

## Requirements

- Python 3.7+
- Streamlit
- SpeechRecognition
- deep-translator
- gTTS (Google Text-to-Speech)
- playsound

## Project Structure

- `app.py`: Main Streamlit application
- `translator.py`: Core translation functionality
- `requirements.txt`: Required Python packages
- `translation_cache/`: Directory for caching audio files

## License

MIT

## Acknowledgements

- Google Translate API
- Google Speech Recognition
- Streamlit 