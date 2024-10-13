import os
import streamlit as st
import google.generativeai as genai
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
import tempfile
import re  
from gtts import gTTS
from io import BytesIO

# Set page title and configuration
st.set_page_config(page_title="University Student Query-Bot", page_icon="🎓", layout="wide")

# Set the API key in the environment variable
os.environ["GOOGLE_API_KEY"] = "AIzaSyCR0gaNYWLJKAKwvKHQmbdeO5Za9CRC_j8"  # Replace with your actual API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Generation configuration for the chatbot
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

# Function to generate a response
def generate_response(user_input):
    conversation_history = [
        "input: Malla Reddy University is located at?",
        "output: It is located in Hyderabad at Maisammaguda, Medchal District.",
        # Add more predefined interactions as needed
    ]
    
    conversation_history.append(f"input: {user_input}")
    conversation_history.append("output: ")

    response = model.generate_content(conversation_history)
    return response.text.strip()

# Function to extract names from the response
def extract_names(text):
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s,.\-]", "", text)
    names = re.findall(r"(Mr\.?|Ms\.?|Dr\.?|Prof\.?)(\s?[A-Z][a-zA-Z]+\s?[A-Z]?[a-zA-Z]*)+", cleaned_text)
    return [f"{title} {name.strip()}" for title, name in names]

# Function to record audio
def record_audio(duration=5, fs=44100):
    st.write("Recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()  # Wait for the recording to finish
    return audio_data, fs

# Function to save the recorded audio as a WAV file
def save_audio(audio_data, fs):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    write(temp_file.name, fs, audio_data)
    return temp_file.name

# Function to recognize speech from the recorded audio
def recognize_speech_from_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Sorry, there was an error with the Google API."

# Function for text-to-speech response
def speak_response(response_text):
    tts = gTTS(response_text)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    st.audio(audio_file, format="audio/mp3")

# UI layout and styles
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f, #0ff);
        animation: neon 1.5s infinite alternate;
    }
    @keyframes neon {
        from {
            filter: brightness(80%) drop-shadow(0 0 5px #f0f) drop-shadow(0 0 10px #0ff);
        }
        to {
            filter: brightness(80%) drop-shadow(0 0 20px #f0f) drop-shadow(0 0 30px #0ff);
        }
    }
    </style>
    """, unsafe_allow_html=True
)

# Title
st.title("🎓 University Student Query-Bot")

# Store previous conversations in session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Display previous conversations
st.write("#### Previous Conversations")
if st.session_state.conversation_history:
    clear_history = st.button("✕ Clear History")
    if clear_history:
        st.session_state.conversation_history = []
    for convo in st.session_state.conversation_history:
        st.markdown(f"**You:** {convo['prompt']}")
        st.markdown(f"**Bot:** {convo['response']}")
else:
    st.write("No previous conversations yet.")

# Create a text input for user prompt
prompt = st.text_input("Type your message here...😊")

# Create columns for buttons
col1, col2 = st.columns([1, 1])

with col1:
    # Record button
    record_audio_button = st.button("Record Audio 🎙️")

with col2:
    # Submit button
    submit_text = st.button("Submit", key="submit_button")

# Handle the submit button for text input
if submit_text and prompt:
    response = generate_response(prompt)
    st.session_state.conversation_history.append({"prompt": prompt, "response": response})
    
    # Extract names from the response and display them
    names = extract_names(response)
    if names:
        st.markdown(f"**Names Found:** {', '.join(names)}")
    
    st.markdown(f"**You:** {prompt}")
    st.markdown(f"**Bot:** {response}")
    speak_response(response)

# Handle the record audio button
if record_audio_button:
    audio_data, fs = record_audio()
    
    # Save the recorded audio to a temporary file
    audio_file = save_audio(audio_data, fs)
    
    # Display the recognized speech
    recognized_text = recognize_speech_from_audio(audio_file)
    st.write(f"Recognized Text: {recognized_text}")
    
    # Generate response based on the recognized text
    response = generate_response(recognized_text)
    st.session_state.conversation_history.append({"prompt": recognized_text, "response": response})
    
    # Extract names from the response and display them
    names = extract_names(response)
    if names:
        st.markdown(f"**Names Found:** {', '.join(names)}")
    
    st.markdown(f"**You:** {recognized_text}")
    st.markdown(f"**Bot:** {response}")
    speak_response(response)

# Additional UI elements can be added as needed
