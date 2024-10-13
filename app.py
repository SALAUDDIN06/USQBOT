import os
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import re  
import sounddevice as sd
import numpy as np

# Set page title and configuration
st.set_page_config(page_title="University Student Query-Bot", page_icon="🎓", layout="wide")

# Set the API key in the environment variable
os.environ["GOOGLE_API_KEY"] = "AIzaSyCR0gaNYWLJKAKwvKHQmbdeO5Za9CRC_j8"
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
        # Example conversation history
        "input: Malla Reddy University is located at?",
        "output: It is located in Hyderabad at Maisammaguda, Medchal District.",
        # Additional example queries and responses...
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

# Function to get voice input
def get_audio_input():
    st.write("Press the record button to start speaking...")
    # Recording settings
    fs = 44100  # Sample rate
    duration = 5  # seconds

    # Record audio
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    audio_data = audio_data.flatten()

    # Convert to bytes
    audio_bytes = np.array(audio_data, dtype=np.int16).tobytes()

    # Use speech recognition
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(BytesIO(audio_bytes))
    
    with audio_file as source:
        audio = recognizer.record(source)

    try:
        st.write("Recognizing...")
        user_input = recognizer.recognize_google(audio)
        st.write(f"Recognized Text: {user_input}")
        return user_input
    except sr.UnknownValueError:
        st.write("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError:
        st.write("Error with the Google API.")
        return ""

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
    .input-container {
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True
)

# Title
st.title("🎓 University Student Query-Bot")
st.write("Ask me anything about the university!")
st.write("You can ask about courses, facilities, events, or anything else related to the university.")
st.write("I'll do my best to help you!")

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

# Initialize session state for conversation history if not already done
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Create a text input for user prompt
prompt = st.text_input("Type your message here...😊")  # Add a small emoji here

# Create columns for buttons
col1, col2 = st.columns([1, 1])

with col1:
    # Speak button
    speak_text = st.button("Voice 🎙️", key="speak_button", help="Click to speak the text.")

with col2:
    # Submit button
    submit_text = st.button("Submit", key="submit_button", help="Click to submit your text.")

# Handle the submit button for text input
if submit_text and prompt:
    response = generate_response(prompt)  # Function to generate the bot's response
    st.session_state.conversation_history.append({"prompt": prompt, "response": response})
    st.write(f"**Bot:** {response}")  # Display bot response
    speak_response(response)  # Speak the response
elif speak_text:
    audio_input = get_audio_input()
    if audio_input:  # Only generate a response if there is input
        response = generate_response(audio_input)
        st.session_state.conversation_history.append({"prompt": audio_input, "response": response})
        st.write(f"**Bot:** {response}")  # Display bot response
        speak_response(response)  # Speak the response

# Display the response audio after each interaction
with st.sidebar:
    st.markdown(
        """
        <style>
        .css-1d391kg {
            background-color: white; /*  background */
        }
        img {
            border-radius: 20%;
            width: 100px;
            height: 100px;
            object-fit: cover;
        }
        .sidebar-content {
            color: white;
            font-family: 'Roboto', sans-serif;
        }
        .neon-text {
            color: White;
            font-weight: bold;
            text-transform: uppercase;
            text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff, 0 0 15px #ff0000, 0 0 20px #ff0000, 0 0 25px #ff0000, 0 0 30px #ff0000, 0 0 35px #ff0000;
        }
        .neon-background {
            padding: 10px;
            background-color: #000;
            border-radius: 10px;
            color: white;
        }
        .social-icons a {
            color: white;
            margin-right: 10px;
            font-size: 24px;
            text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff;
        }
        .social-icons a:hover {
            color: Black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='sidebar-content neon-background'>
            <h1 class='neon-text' style='font-size: 40px;'>About</h1>
            <h3 style='font-size: 10px;'>
                The Student Query Bot is a digital assistant designed to help students, faculty, and staff quickly access essential information related to university subjects, departments, and faculty members. It provides personalized answers to common academic queries, assists in navigating university resources, and offers support on course schedules, subject details, faculty contact information, and campus-related inquiries. The bot aims to enhance the university experience by delivering timely, accurate information, making student life easier and more efficient.
            </h3>
            <div class='social-icons'>
                <a href='https://twitter.com/MusicalAnime1'><i class='fab fa-twitter'></i></a>
                <a href='https://www.instagram.com/salauddin_20_/'><i class='fab fa-instagram'></i></a>
                <a href='https://www.linkedin.com/in/salauddin-mohammed-93b7b2244/'><i class='fab fa-linkedin'></i></a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )