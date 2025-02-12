import streamlit as st
from PIL import Image
from llama_model import LLAMA_MODEL
from utils import get_default_message

# Custom styles for the sidebar and messages using CSS
st.markdown(
    """
    <style>
    /* Ensure entire app has a white background */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* Chat messages styling */
    .user-message {
        border: 1px solid #d0f4f7;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: #e0f7fa; /* Light Blue */
        color: #000000; /* Ensure black text for visibility */
        font-weight: bold;
    }

    .bot-message {
        border: 1px solid #d0f4f7;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f9f9f9; /* Light Gray */
        color: #000000; /* Ensure black text for visibility */
        font-weight: bold;
    }

    /* Input box fixed at the bottom */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        border-top: 1px solid #d0f4f7;
        z-index: 1000;
    }

    /* Sidebar title */
    .sidebar-title {
        color: #264653 !important;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Load the logo image
logo = Image.open('logo.jpg')

# Define the layout of the app
if logo:
    st.sidebar.image(logo, use_column_width=True)
st.sidebar.markdown(
    "<h1 style='text-align: center; color: white;'>Chatbot Assistant</h1>",
    unsafe_allow_html=True
)

# Function to initialize the model
def initialize_model():
    try:
        with st.spinner('Loading model...'):
            st.session_state['model'] = LLAMA_MODEL()
            print('Model loaded successfully...')
        st.session_state['model_initialized'] = True
    except Exception as e:
        st.session_state['model_error'] = str(e)

# Initialize the model in session state if not already initialized
if 'model_initialized' not in st.session_state:
    st.session_state['model_initialized'] = False
    st.session_state['model_error'] = None
    initialize_model()

# Display error message if model initialization failed
if st.session_state['model_error']:
    st.error(f"Model initialization failed: {st.session_state['model_error']}")

# Greeting messages
st.markdown("""
# Smart Document Chatbot Assistant
Hello 👋, I am your smart assistant, specialized in the documents you are using. I can help answer your inquiries based on the available information.

أهلاً 👋، أنا مساعدك الذكي المتخصص في المستندات التي تستخدمها. يمكنني مساعدتك في الإجابة على استفساراتك بناءً على المعلومات المتاحة.
""")

# Ensure there is space to store the conversation in session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to add a new message to the conversation
def add_message(sender, message):
    st.session_state['messages'].append({'sender': sender, 'message': message})

# Function to handle errors
def handle_error(error_message):
    add_message('bot', error_message)

# Display the conversation history at the top
st.markdown("<div class='message-container'>", unsafe_allow_html=True)

# Prevent mid-loop changes by making a copy
messages_to_display = list(st.session_state['messages'])
for message in messages_to_display:
    if message['sender'] == 'user':
        st.markdown(f"<div class='user-message'><strong>You:</strong> {message['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'><strong>Bot:</strong> {message['message']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Fixed input field at the bottom
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
with st.form(key='my_form', clear_on_submit=True):
    question = st.text_input("Ask me anything about white land regulations")
    submit_button = st.form_submit_button("Submit")
st.markdown("</div>", unsafe_allow_html=True)

# Handle question submission
if submit_button and question:
    if st.session_state['model_initialized']:
        add_message('user', question)
        st.write(f"**You:** {question}")  # Immediate UI update

        try:
            with st.spinner('Processing your question...'):
                result = st.session_state['model'].get_important_facts(question.strip())
            if result == "":
                result = get_default_message(question)
        except Exception as err:
            print(err)
            result = get_default_message(question)

        st.write(f"**Bot:** {result}")  # Immediate UI update
        add_message('bot', result)

    else:
        handle_error("Model is not yet initialized. Please wait a moment and try again.")
