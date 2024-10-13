import os
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import sounddevice as sd
import wave
from gtts import gTTS
from io import BytesIO
import re  
import tempfile

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
        "input: Malla Reddy University is located at?",
        "output: It is located in Hyderabad at Maisammaguda, Medchal District.",
        "input: Who is the Vice Chancellor?",
        "output: V.S.K Reddy",
        "input: Who is the chairman for Malla Reddy University?",
        "output: C.H Malla Reddy",
        "input: Who is the Dean for the Data Science Department?",
        "output: D.R Naveen Kumar",
        "input: 3rd Year DS - faculty?",
        "output: Faculty of MLDS: Ms. M. Shailaja, Faculty of MLDS Lab: Ms. M. Shailaja / Ms. Prashanthi, Faculty of DAA: Ms. Priyanka Chaumwal, Faculty of CCS: Mr. Naga Mallik, Faculty of CCS Lab: Mr. Naga Mallik / Ms. Priyanka / Ms. S. Mrudhula, Faculty of AD: Ms. Flora Ann Mathew, Faculty of PDS: Ms. D. Meenakshi, Faculty of Gen AI: Ms. Krushima, Faculty of Gen AI Lab: Ms. Krushima / Ms. R. Swarna Teja",
        "input: 1st year DS - Omega faculty?",
        "output: Faculty of PP: Dr. Ekta Maini, Faculty of UIWD: Mr. T. Krishnamurthy, Faculty of ACT: Mr. K. Srinivasa Rao, Faculty of ENG: Dr. Akhil Kumar, Faculty of M1: Dr. Imthiyaz Wani, Faculty of AP: Mr. A. Shiva Krishna",
        "input: 1st year DS - Zeta faculty?",
        "output: Faculty of PP: Dr. Ekta Maini, Faculty of UIWD: Ms. V. Nagahemakumari, Faculty of ACT: Mr. Vikram Kalvala, Faculty of ENG: Dr. Smitha, Faculty of M1: Dr. B. Seetharambabu, Faculty of AP: Dr. P. Ramana Reddy",
        "input: 1st year DS - Sigma faculty?",
        "output: Faculty of PP: Mr. V. Nitish, Faculty of UIWD: Dr. Menagadevi, Faculty of ACT: Mr. K. Vijay Krupa, Faculty of ENG: Dr. Zareena, Faculty of M1: Dr. Kushbu Singh, Faculty of AP: Dr. P. Ramana Reddy",
        "input: 1st year DS - Delta faculty?",
        "output: Faculty of PP: Mr. Mahesh, Faculty of UIWD: Mr. Krishnamurthy, Faculty of ACT: Dr. Jawahar, Faculty of ENG: Dr. Zareena, Faculty of M1: Dr. Khusbhu Singh, Faculty of AP: Dr. P. Srinivas",
        "input: 1st year DS - Gamma faculty?",
        "output: Faculty of PP: Dr. Vijay, Faculty of UIWD: Ms. Shiva, Faculty of ACT: Mr. Vijay Krupa, Faculty of ENG: Ms. Sadia, Faculty of M1: Ms. Lakshmi, Faculty of AP: Dr. Ashok",
        "input: 1st year DS - Beta faculty?",
        "output: Faculty of PP: Mr. Samuel Raju, Faculty of UIWD: Mr. Chalapathirao, Faculty of ACT: Mr. Joseph, Faculty of ENG: Ms. Sadia, Faculty of M1: Dr. Nidhi, Faculty of AP: Dr. Sampath",
        "input: 1st year DS - Alpha faculty?",
        "output: Faculty of PP: Mr. K. Mahesh Raj, Faculty of UIWD: Ms. Shebaa, Faculty of ACT: Dr. Jawahar, Faculty of ENG: Dr. Kalyan, Faculty of M1: Dr. Nidhi Humnekhar, Faculty of AP: Mr. J. Sashi Kumar"
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

    # Save to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav_file:
        with wave.open(temp_wav_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())
        temp_wav_path = temp_wav_file.name

    # Use speech recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_wav_path) as source:
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
prompt = st.text_input("Type your message here...", "")

# Button to get audio input
if st.button("🎤 Speak"):
    user_input = get_audio_input()
else:
    user_input = prompt

# If user input is provided
if user_input:
    response_text = generate_response(user_input)
    st.session_state.conversation_history.append({"prompt": user_input, "response": response_text})

    # Display the bot's response
    st.markdown(f"**Bot:** {response_text}")
    
    # Speak the response
    speak_response(response_text)
