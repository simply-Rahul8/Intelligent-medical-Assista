import streamlit as st
import requests
from gtts import gTTS
import whisper
import sounddevice as sd
import wavio
import os
from streamlit_drawable_canvas import st_canvas
import uuid
from datetime import datetime
import json
import time

# ========== CONFIGURATION ==========
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", os.getenv("PERPLEXITY_API_KEY"))

# ========== INIT MODELS ==========
try:
    whisper_model = whisper.load_model("tiny", device="cpu")
except Exception as e:
    st.error(f"Whisper model initialization failed: {e}")
    whisper_model = None

# ========== TTS FUNCTION (gTTS + Streamlit Audio) ==========
def speak_text(text):
    try:
        tts = gTTS(text=text)
        filename = f"tts_output_{uuid.uuid4().hex}.mp3"
        tts.save(filename)
        with open(filename, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")
        os.remove(filename)
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")

# ========== API and TRANSCRIPTION ==========
def generate_consent_summary(medical_record):
    if not PERPLEXITY_API_KEY:
        raise ValueError("Perplexity API key not found. Please set PERPLEXITY_API_KEY in .streamlit/secrets.toml.")
    prompt = f"""
    You are an AI assistant designed to provide clear, empathetic, and non-technical summaries for medical procedures. Given the following medical record or procedure description, generate a patient-friendly summary that includes the procedure details, expected outcomes, risks, and patient rights. Keep the language simple, empathetic, and understandable.

    Medical Record: {medical_record}

    Summary:
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful medical assistant with access to up-to-date medical information."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9
    }
    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        error_response = json.loads(e.response.text) if e.response else {}
        error_message = error_response.get("error", {}).get("message", str(e))
        raise Exception(f"Failed to generate summary: {error_message}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")

def answer_question(question, context):
    if not PERPLEXITY_API_KEY:
        raise ValueError("Perplexity API key not found. Please set PERPLEXITY_API_KEY in .streamlit/secrets.toml.")
    prompt = f"""
    You are an AI assistant helping a patient understand a medical procedure. Answer the following question in a clear, empathetic, and non-technical manner. Use the provided context to inform your response.

    Context: {context}
    Question: {question}

    Answer:
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful medical assistant with access to up-to-date medical information."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.7,
        "top_p": 0.9
    }
    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        error_response = json.loads(e.response.text) if e.response else {}
        error_message = error_response.get("error", {}).get("message", str(e))
        raise Exception(f"Failed to answer question: {error_message}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")

def record_audio(duration=5, sample_rate=44100):
    try:
        status_placeholder = st.empty()
        status_placeholder.markdown("🔴 **Recording audio... Please speak now.**")
        start_time = time.time()
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        elapsed_time = time.time() - start_time
        filename = f"temp_recording_{uuid.uuid4()}.wav"
        wavio.write(filename, recording, sample_rate, sampwidth=2)
        status_placeholder.markdown(f"✅ **Recording complete** (duration: {elapsed_time:.1f} seconds).")
        return filename
    except Exception as e:
        st.error(f"Audio recording error: {e}")
        return None

def transcribe_audio(audio_file):
    if not whisper_model:
        raise Exception("Whisper model not initialized.")
    try:
        result = whisper_model.transcribe(audio_file, language="en")
        os.remove(audio_file)
        return result["text"].strip()
    except Exception as e:
        os.remove(audio_file) if os.path.exists(audio_file) else None
        raise Exception(f"Audio transcription error: {e}")

def log_medical_record(medical_record):
    try:
        with open("medical_records.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Medical Record: {medical_record}\n")
    except Exception as e:
        st.error(f"Error logging medical record: {e}")

# ========== SESSION STATE ==========
if "consent_summary" not in st.session_state:
    st.session_state.consent_summary = ""
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False
if "spoken_question" not in st.session_state:
    st.session_state.spoken_question = ""

# ========== UI ==========
st.title("Intelligent Consent Flow for Medical Care")

if not PERPLEXITY_API_KEY:
    st.error("Perplexity API key not found. Please set PERPLEXITY_API_KEY in .streamlit/secrets.toml.")
    st.stop()

# Step 1: Medical Record Input
st.header("Enter Medical Record or Procedure Description")
medical_record = st.text_area(
    "Medical Record", 
    placeholder="Enter procedure details or medical record...", 
    height=150
)
if st.button("Generate Consent Summary", disabled=not medical_record):
    try:
        with st.spinner("Generating summary..."):
            st.session_state.consent_summary = generate_consent_summary(medical_record)
            log_medical_record(medical_record)
    except Exception as e:
        st.error(str(e))

# Step 2: Display Consent Summary
if st.session_state.consent_summary:
    st.header("Consent Summary")
    st.markdown(st.session_state.consent_summary)
    if st.button("Read Summary Aloud"):
        speak_text(st.session_state.consent_summary)

# Step 3: Conversational Q&A
st.header("Ask Questions About the Procedure")
question = st.text_input(
    "Your Question", 
    value=st.session_state.spoken_question, 
    placeholder="Type or speak your question here..."
)
if question and st.session_state.spoken_question:
    if st.button("Read Question Aloud"):
        speak_text(question)

if st.button("Record Question", disabled=not whisper_model):
    audio_file = record_audio()
    if audio_file:
        try:
            with st.spinner("Transcribing question..."):
                transcribed_question = transcribe_audio(audio_file)
                st.session_state.spoken_question = transcribed_question
                st.success(f"Transcribed question: '{transcribed_question}'")
        except Exception as e:
            st.error(str(e))

if st.button("Submit Question", disabled=not question):
    try:
        with st.spinner("Generating answer..."):
            answer = answer_question(question, st.session_state.consent_summary)
            answer_placeholder = st.empty()
            displayed_text = ""
            for i in range(0, len(answer), 10):
                displayed_text += answer[i:i+10]
                answer_placeholder.markdown(f"**Answer:** {displayed_text}")
                time.sleep(0.05)
            st.session_state.questions.append(question)
            st.session_state.answers.append(answer)
            st.session_state.spoken_question = ""
    except Exception as e:
        st.error(str(e))

# Conversation history and manual speak-out only
if st.session_state.questions:
    st.subheader("Conversation History")
    for idx, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {a}")
        if st.button(f"Read Answer Aloud: {q[:20]}...", key=f"read_{idx}"):
            speak_text(a)

# Step 4: Consent Capture
st.header("Provide Consent")
consent_option = st.radio("Choose how to provide consent:", ("Verbal Consent", "Digital Signature"))

if consent_option == "Verbal Consent":
    st.markdown(
        "**Instructions**: Click the button below and say 'I consent' clearly. "
        "The microphone will record for 5 seconds."
    )
    if st.button("Record Verbal Consent", disabled=not whisper_model):
        audio_file = record_audio()
        if audio_file:
            try:
                with st.spinner("Transcribing audio..."):
                    transcription = transcribe_audio(audio_file)
                    if "i consent" in transcription.lower():
                        st.session_state.consent_given = True
                        st.success("Verbal consent verified: 'I consent' detected.")
                    else:
                        st.error(f"Consent not detected. Transcription: '{transcription}'. Please say 'I consent' clearly.")
            except Exception as e:
                st.error(str(e))

elif consent_option == "Digital Signature":
    st.markdown("Sign below to provide consent:")
    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="canvas"
    )
    if st.button("Submit Signature", disabled=not (canvas_result.json_data and canvas_result.json_data["objects"])):
        if canvas_result.json_data and canvas_result.json_data["objects"]:
            st.session_state.consent_given = True
            st.success("Signature received.")

# Step 5: Consent Confirmation
if st.session_state.consent_given:
    st.header("Consent Complete")
    st.markdown("Thank you for providing your informed consent.")
