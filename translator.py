# translator.py

import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import time
import hashlib
from pathlib import Path
import threading
import queue
import playsound

class RealTimeTranslator:
    def __init__(self, source_lang='en', target_lang='fr'):
        """
        Initializes the translator with source and target languages.
        
        Args:
            source_lang (str): Source language code (default is 'en').
            target_lang (str): Target language code (default is 'fr').
        """
        print("Initializing translator...")
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Validate language codes before initializing
        try:
            self.translator = GoogleTranslator(source=source_lang, target=target_lang)
            # Test translation to verify languages are supported
            test_translation = self.translator.translate("test")
            if not test_translation:
                raise ValueError("Failed to initialize translator: Invalid language codes.")
        except Exception as e:
            raise ValueError(f"Failed to initialize translator: {str(e)}")
        
        self.recognizer = sr.Recognizer()
        self.cache_dir = Path("translation_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.translation_cache = {}
        self.max_cache_size = 1000  # Maximum number of cached translations
        
        # Configure speech recognition settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("Initialization complete!")
    
    def get_audio_filename(self, text, target_lang):
        """
        Generates a unique filename for the audio based on text content.
        
        Args:
            text (str): The text to convert to audio.
            target_lang (str): The language code for the audio.
        
        Returns:
            Path: The file path for the audio file.
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.cache_dir / f"audio_{target_lang}_{text_hash}.mp3"
    
    def adjust_for_ambient_noise(self, source, duration=1):
        """
        Adjusts the recognizer for ambient noise.
        
        Args:
            source (sr.Microphone): The microphone source.
            duration (int): Duration in seconds to adjust for noise.
        """
        print("\nAdjusting for ambient noise... Please wait...")
        for i in range(3):
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"Calibrating... {i+1}/3")
        print("Ambient noise adjustment complete!")
    
    def start_translation(self, input_queue, output_queue):
        """
        Starts the translation process, listening for audio input and translating it.
        
        Args:
            input_queue (queue.Queue): Queue to put recognized text.
            output_queue (queue.Queue): Queue to put translated text.
        """
        try:
            with sr.Microphone() as source:
                self.adjust_for_ambient_noise(source)
                print(f"\nListening... (Speak in {self.source_lang})")
                print("Press Ctrl+C to stop")
                
                while True:
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        text = self.recognizer.recognize_google(audio, language=self.source_lang)
                        input_queue.put(text)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        print("\nCould not understand audio. Please try again.")
                    except sr.RequestError as e:
                        print(f"\nError with speech recognition service: {e}")
                    except Exception as e:
                        print(f"\nUnexpected error: {str(e)}")
        except KeyboardInterrupt:
            print("\nTranslation stopped by user.")
        except Exception as e:
            print(f"\nMicrophone error: {str(e)}")
    
    def text_to_speech(self, text, target_lang):
        """
        Converts text to speech and plays it.
        
        Args:
            text (str): The text to convert.
            target_lang (str): The language code for the speech.
        """
        try:
            audio_file = self.get_audio_filename(text, target_lang)
            
            if not audio_file.exists():
                print("Generating audio...", end='\r')
                tts = gTTS(text=text, lang=target_lang)
                tts.save(str(audio_file))
            
            playsound.playsound(str(audio_file))
        except Exception as e:
            print(f"\nFailed to process text-to-speech: {str(e)}")
    
    def manage_cache(self):
        """
        Manages the translation cache size by removing the oldest entries.
        """
        if len(self.translation_cache) > self.max_cache_size:
            # Remove oldest 20% of entries
            items_to_remove = int(self.max_cache_size * 0.2)
            for _ in range(items_to_remove):
                # Remove the first item (oldest) from the ordered dict
                self.translation_cache.popitem(last=False)

def listen_and_translate(source_lang, target_lang, input_queue, output_queue):
    """
    Initializes and starts the real-time translation process.
    
    Args:
        source_lang (str): Source language code.
        target_lang (str): Target language code.
        input_queue (queue.Queue): Queue to receive recognized text.
        output_queue (queue.Queue): Queue to send translated text.
    """
    translator = RealTimeTranslator(source_lang=source_lang, target_lang=target_lang)
    translator.start_translation(input_queue, output_queue)

def text_to_speech(text, target_lang):
    """
    Converts text to speech and plays it.
    
    Args:
        text (str): The text to convert.
        target_lang (str): The language code for the speech.
    """
    translator = RealTimeTranslator(target_lang=target_lang)
    translator.text_to_speech(text, target_lang)

def get_audio_filename(text, target_lang):
    """
    Generates a unique filename for the audio based on text content.
    
    Args:
        text (str): The text to convert to audio.
        target_lang (str): The language code for the audio.
    
    Returns:
        Path: The file path for the audio file.
    """
    translator = RealTimeTranslator(target_lang=target_lang)
    return translator.get_audio_filename(text, target_lang)