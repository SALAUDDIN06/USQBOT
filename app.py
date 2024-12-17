import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import re  
from dotenv import load_dotenv
import os



# Set page configuration
st.set_page_config(page_title="University Student Query-Bot", page_icon="🎓", layout="wide")

# Set the API key directly
api_key = "AIzaSyCR0gaNYWLJKAKwvKHQmbdeO5Za9CRC_j8"

# Debug: Check if the API key is set
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key  # Set the API key in the environment variable
    try:
        genai.configure(api_key=api_key)  # Configure Google Generative AI
    except Exception as e:
        st.error(f"Failed to configure Google Generative AI: {e}")
else:
    st.error("API key not set. Please provide a valid API key.")

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
    conversation_history =[
        "input: Malla Reddy University is loacted at?",
        "output: It is loacted in the Hyderabad at misammaguda Medchal District",
        "input: Who is the Vice chancellor?",
        "output: V.S.K Reddy",
        "input: Who is the Registrar of Malla reddy university?",
        "output: Dr. M Anjaneyulu",
        "input: Who is the Chancellor  of Malla reddy university?",
        "output: Smt. Ch Kalpana",
        "input: Who is the placement cell incharge  of Malla reddy university?",
        "output:Prof. KODUKULA KAILASA RAO",
        "input: Who is the School of engineering(SOE) Dean of Malla reddy university?",
        "output:Prof. KODUKULA KAILASA RAO",
        "input: Who is the chairman for Malla Reddy University ?",
        "output: C.H Malla Reddy",
        "input: Who is the Dean for Data Science Department ?",
        "output: D.R Naveen Kumar",
        "input: 3rd Year DS - faculty?",
        "Output:Faculty of MLDS: Ms. M. Shailaja, Faculty of MLDS Lab: Ms. M. Shailaja / Ms. Prashanthi, Faculty of DAA: Ms. Priyanka Chaumwal, Faculty of CCS: Mr. Naga Mallik, Faculty of CCS Lab: Mr. Naga Mallik / Ms. Priyanka / Ms. S. Mrudhula, Faculty of AD: Ms. Flora Ann Mathew, Faculty of PDS: Ms. D. Meenakshi, Faculty of Gen AI: Ms. Krushima, Faculty of Gen AI Lab: Ms. Krushima / Ms. R. Swarna Teja",
        "input : 1st year DS - Omega faculty?",
        "output : Faculty of PP: Dr. Ekta Maini, Faculty of UIWD: Mr. T. Krishnamurthy, Faculty of ACT: Mr. K. Srinivasa Rao, Faculty of ENG: Dr. Akhil Kumar, Faculty of M1: Dr. Imthiyaz Wani, Faculty of AP: Mr. A. Shiva Krishna",
        "input :1st year DS - Zeta faculty?",
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
        "output: Faculty of PP: Mr. K. Mahesh Raj, Faculty of UIWD: Ms. Shebaa, Faculty of ACT: Dr. Jawahar, Faculty of ENG: Dr. Kalyan, Faculty of M1: Dr. Nidhi Humnekhar, Faculty of AP: Mr. J. Sashi Kumar " ,
        "input: Who are the faculty members of the 2nd year CSE?",
        "output:Data Structures through java(Dr. B.Jogeshwarao,Mr.G.Ganesh) , Database Management System(Dr.P.Archana,Mrs.K.Manasa) , Discrete Mathematics(Mr.P.Chandramohan,Dr.G.venkata Suman), Computer Networks(Dr.Nanda Kishore Kumar, Mr.M.Goutam), Object Oriented Software Engineering(Ms.I.swapna, Mr.T.Srajan Kumar), Data Visualization(Mr.G.Ganesh,Ms.J.Devi Priya), Indian Heritage and Economy(Mr.V.Ravichandra Shekar)",
        "input : Who is the Dean of CSE?",
        "output : shaik meeravalli",
        "input: Who are the faculty of 3rd year CSE?",
        "output: Artificial Intelligence and Machine Learing(Mrs.Sagarika,Mr.Naveen Kumar), Internet Of Things(Dr.T.Pandindra,Mr.G.Kishore Kumar), Compiler Design(Mrs.Preethi Reddy,Mrs.Shilpa), Agile Software Development(Mrs.S.Sowmya), Distributed Operating System(Mr.G.Raju), Salesforce Platform Developer(Dr.Arunsingh Chouhan,Dr.Shaik Hussian), Human Resource Management(Dr.Nazia,Mrs.K.Sudha), Artificial Intelligence and Machine Learing Lab(Mr.Naveen Kumar, Mr.Joshi), Internet Of Things Lab(Dr.T.Panindra,Mr.P.Prudhi Prasad), Salesforce Platform Developer Lab(Dr.Arun Singh Chouhan,Ms.G.Nandhini), App Devolopment - IOT and Machinelearning Explore(Mrs.Preethi Reddy,Mrs.Sowmya) Proffesional Development Skills(Mrs.K.Sudha, Mr.G.Mohanram)"
]
    
    conversation_history.append(f"input: {user_input}")
    conversation_history.append("output: ")

    try:
        response = model.generate_content(conversation_history)
        return response.text.strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Function to extract names from the response
def extract_names(text):
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s,.\-]", "", text)
    names = re.findall(r"(Mr\.?|Ms\.?|Dr\.?|Prof\.?)\s?[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?", cleaned_text)
    return names

# Function to get voice input
def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        try:
            audio = recognizer.listen(source)
            st.write("Recognizing...")
            user_input = recognizer.recognize_google(audio)
            st.write(f"Recognized Text: {user_input}")
            return user_input
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            st.error("Error with the Google API.")
    return ""

# Function for text-to-speech response
def speak_response(response_text):
    try:
        tts = gTTS(response_text)
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        st.audio(audio_file, format="audio/mp3")
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")

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
st.write("Ask me anything about the university!")

# Store previous conversations in session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Display previous conversations
st.write("#### Previous Conversations")
if st.session_state.conversation_history:
    if st.button("✕ Clear History"):
        st.session_state.conversation_history = []
    for convo in st.session_state.conversation_history:
        st.markdown(f"**You:** {convo['prompt']}")
        st.markdown(f"**Bot:** {convo['response']}")
else:
    st.write("No previous conversations yet.")

# Create a text input for user prompt
prompt = st.text_input("Type your message here...")

# Submit button
if st.button("Submit") and prompt:
    response = generate_response(prompt)
    st.session_state.conversation_history.append({"prompt": prompt, "response": response})
    
    # Extract names from the response and display them
    names = extract_names(response)
    if names:
        st.markdown(f"**Names Found:** {', '.join(names)}")
    
    st.markdown(f"**You:** {prompt}")
    st.markdown(f"**Bot:** {response}")
    
    # Speak the response
    speak_response(response)


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
                <a href='https://github.com/SALAUDDIN06'><i class='fab fa-github'></i></a>
                <a href='https://www.linkedin.com/in/mohammed-salauddin-223804266/'><i class='fab fa-linkedin'></i></a>
                <a href='https://accounts.snapchat.com/accounts/v2/login'><i class='fab fa-snapchat'></i></a>
                <a href='https://hammerandchisel.zendesk.com/'><i class='fab fa-discord'></i></a>
                <p style =color:pink>Developer: Md. Salauddin </p>
            </div>
            <style>
                @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
            </style>
        </div>
        """,
        unsafe_allow_html=True
    )
