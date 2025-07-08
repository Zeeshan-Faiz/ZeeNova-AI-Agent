import streamlit as st
from openai import RateLimitError, APIError
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from models.model_enum import ModelName
from agent.agent_setup import get_agent_executor
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="ZeeNova AI Agent", layout="centered", initial_sidebar_state="expanded")

# --- Custom Styling ---
st.markdown("""<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.main-header h1 {
    color: white;
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.main-header p {
    color: rgba(255,255,255,0.9);
    text-align: center;
    font-size: 1.1rem;
}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>ZeeNova AI Agent</h1>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Model Selector ---
MODEL_DISPLAY_NAMES = {
    ModelName.GPT_4_1: "OpenAI GPT-4.1",
    ModelName.GPT_4_1_MINI: "OpenAI GPT-4.1 Mini",
    ModelName.GPT_4O: "OpenAI GPT-4o",
    ModelName.GPT_4O_MINI: "OpenAI GPT-4o Mini",
}

with st.sidebar:
    st.markdown("<div class='sidebar-header'><h2>⚙️ Settings</h2></div>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "Choose your AI model:",
        list(ModelName),
        format_func=lambda model: MODEL_DISPLAY_NAMES.get(model, model.value),
        key="model_selector"
    )

# --- Init State ---
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
            "role": "assistant",
            "avatar": "❄️",
            "content": (
                "**Hello!👋 I'm ZeeNova — your smart AI assistant.**\n\n"
                "I am designed to provide helpful, accurate and real-time answers to "
                "your questions. I can access tools to look up facts, check the latest news, get stock "
                "prices and more. My goal is to assist you with reliable information and thoughtful responses. "
                "Just type your question below and I'm ready to help!"
            )
        })

if (
    "agent_executor" not in st.session_state or
    st.session_state.get("model_used") != selected_model
):
    st.session_state.agent_executor = get_agent_executor(selected_model, st.session_state.memory)
    st.session_state.model_used = selected_model

#Input box:
for msg in st.session_state.messages:
    role = msg.get("role", "assistant")
    avatar = msg.get("avatar", None)

    if avatar:
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])
    else:
        with st.chat_message(role):
            st.markdown(msg["content"])

if user_prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "avatar": "👨‍💻", "content": user_prompt})
    with st.chat_message("user", avatar ="👨‍💻"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="❄️"):
        message_placeholder = st.empty()  # Reserve a UI space
        try:
            st.session_state.memory.chat_memory.add_message(HumanMessage(content=user_prompt))

            with st.spinner("Thinking..."):
                response = st.session_state.agent_executor.invoke({"input": user_prompt})
                output = response.get("output", "[No output]")

            # Once response is ready, update UI
            message_placeholder.markdown(output)

            # Save to memory and messages
            st.session_state.memory.chat_memory.add_message(AIMessage(content=output))
            st.session_state.messages.append({"role": "assistant", "avatar": "❄️", "content": output})

        except RateLimitError:
            msg = "⚠️ I'm currently over my usage limit. Please try again later."
            st.error(msg)
            st.session_state.messages.append({"role": "assistant", "avatar": "❄️", "content": msg})

        except APIError as e:
            msg = f"🚨 API Error: {str(e)}"
            st.error(msg)
            st.session_state.messages.append({"role": "assistant", "avatar": "❄️", "content": msg})

        except Exception as e:
            msg = f"An unexpected error occurred: {str(e)}"
            st.error(msg)
            st.session_state.messages.append({"role": "assistant", "avatar": "❄️", "content": msg})
