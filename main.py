import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------

load_dotenv()

# ---------------------------------------------------------------------
# Speech & Audio Setup
# ---------------------------------------------------------------------

recognizer = sr.Recognizer()
microphone = sr.Microphone()

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)

# ---------------------------------------------------------------------
# LLM Setup
# ---------------------------------------------------------------------

llm = ChatOllama(
    model="llama3.2",
    temperature=0.4
)

# Simple conversation memory
conversation_history = []
MAX_HISTORY = 6

# ---------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------

def speak(text: str):
    """Convert text to speech."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen() -> str:
    """Capture voice input and convert to text."""
    with microphone as source:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ You: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return ""

def generate_response(user_input: str) -> str:
    """Generate LLM response with short conversation memory."""
    global conversation_history

    messages = conversation_history + [HumanMessage(content=user_input)]
    response = llm.invoke(messages).content

    conversation_history.append(HumanMessage(content=user_input))
    conversation_history.append(AIMessage(content=response))

    conversation_history = conversation_history[-MAX_HISTORY:]

    return response

# ---------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------

def main():
    speak("Hello. I am your voice assistant. You can start speaking.")

    while True:
        user_input = listen()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "stop"}:
            speak("Goodbye. Have a nice day.")
            break

        response = generate_response(user_input)
        print(f"🤖 Assistant: {response}")
        speak(response)

# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
