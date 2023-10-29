# Import necessary modules and libraries
from dataclasses import dataclass
from typing import Literal
import streamlit as st

# Import custom modules from langchain package
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
import streamlit.components.v1 as components


# Define a data class for chat messages
@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str


# Function to load custom CSS styles for the app
def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


# Function to initialize session state variables
def initialize_session_state():
    # Check if session state variables exist, if not, initialize them
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "conversation" not in st.session_state:
        # Initialize OpenAI language model and conversation memory
        llm = OpenAI(
            temperature=0,
            openai_api_key=st.secrets["openai_api_key"],
            model_name="text-davinci-003"
        )
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),
        )


# Callback function when the "Submit" button is clicked
def on_click_callback():
    # Get the user's input prompt
    with get_openai_callback() as cb:
        human_prompt = st.session_state.human_prompt
        # Generate AI response using the conversation chain
        llm_response = st.session_state.conversation.run(human_prompt)
        # Update chat history and token count
        st.session_state.history.append(Message("human", human_prompt))
        st.session_state.history.append(Message("ai", llm_response))
        st.session_state.token_count += cb.total_tokens


# Load custom CSS styles
load_css()

# Initialize session state variables
initialize_session_state()

# Set the title for the Streamlit app
st.title("ChatBot created using Streamlit and OpenAI LLM")

# Create containers for chat history, input prompt, and additional content
chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()

# Display chat history in the chat_placeholder container
with chat_placeholder:
    for chat in st.session_state.history:
        # Generate HTML for displaying chat bubbles with user and AI messages
        div = f"""
<div class="chat-row 
    {'' if chat.origin == 'ai' else 'row-reverse'}">
    <img class="chat-icon" src="app/static/{
        'ai_icon.png' if chat.origin == 'ai'
        else 'user_icon.png'}"
         width=32 height=32>
    <div class="chat-bubble
    {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
        &#8203;{chat.message}
    </div>
</div>
        """
        # Display chat bubbles using markdown
        st.markdown(div, unsafe_allow_html=True)

    # Add spacing between chat bubbles
    for _ in range(3):
        st.markdown("")

# Display input form for user to enter chat messages in prompt_placeholder container
with prompt_placeholder:
    # Create columns for chat input and submit button
    st.markdown("**Chat**")
    cols = st.columns((6, 1))
    # Text input for user to enter chat messages
    cols[0].text_input(
        "Chat",
        value="Hello bot",
        label_visibility="collapsed",
        key="human_prompt",
    )
    # Submit button to send user's message to the AI model
    cols[1].form_submit_button(
        "Submit",
        type="primary",
        on_click=on_click_callback,
    )

# Display information about token usage and conversation memory in credit_card_placeholder
credit_card_placeholder.caption(f"""
Used {st.session_state.token_count} tokens \n
Debug Langchain conversation: 
{st.session_state.conversation.memory.buffer}
""")

# Add JavaScript code to enable pressing Enter key to submit the chat form
components.html("""
<script>
const streamlitDoc = window.parent.document;

const buttons = Array.from(
    streamlitDoc.querySelectorAll('.stButton > button')
);
const submitButton = buttons.find(
    el => el.innerText === 'Submit'
);

streamlitDoc.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'Enter':
            submitButton.click();
            break;
    }
});
</script>
""",
                height=0,
                width=0,
                )
