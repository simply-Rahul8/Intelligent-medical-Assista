
# Intelligent Consent Flow for Medical Care/ Intelligent Medical Assista

A secure, real-time web application that transforms the medical procedure consent process with conversational AI, natural language summaries, and accessible, privacy-preserving interactions.

## Overview

This app helps patients understand medical procedures, ask questions, and provide consent (voice or digital signature) in a simple, guided, and friendly way. Consent content is auto-generated in plain English from raw medical notes via Perplexity AI’s API (Pro), and the system supports both typed and spoken input or output. No identifiable patient data or conversation is stored: only minimally necessary event records.

## Features

- **Patient-Friendly Consent Summaries:**  
  Converts free-text medical notes or procedure codes into clear, plain-language explanations using Perplexity AI’s LLMs.

- **Conversational Q&A:**  
  Patients can ask questions in text or by voice. Responses are generated with up-to-date medical insights via Perplexity API.

- **Accessible Audio Output:**  
  All information (summaries, answers) can be instantly read aloud using local TTS for accessibility and inclusivity.

- **Flexible Consent Capture:**  
  Supports both spoken ("I consent") and digital signature via a touchscreen or mouse, with instant feedback.

- **Minimal Logging (Privacy-First):**  
  Stores only the medical record/procedure note and timestamp—no conversations, audio files, or personal details are retained.

- **Local, Real-Time Use:**  
  Fast, intuitive Streamlit UI; LLM runs on Perplexity’s cloud, speech runs locally for privacy and speed.

## Technology Stack

- **Perplexity AI API (Pro Plan):**  
  For all LLM tasks (summaries, Q&A, multi-model support).
- **Python / Streamlit:**  
  Rapid UI, audio, signature pad (streamlit-drawable-canvas).
- **gTTS:**  
  Local text-to-speech for on-demand audio playback.
- **Whisper:**  
  Local ASR for voice consent/questions and privacy.
- **sounddevice/wavio:**  
  In-app audio recording.
- **Other:**  
  `requests`, `uuid`, `datetime`, `json` (for logging/events).

## Usage Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Intelligent-medical-Assista.git
   cd Intelligent-medical-Assista
   ```

2. **[Optional] Create a Conda Environment**
   ```bash
   conda create --name consent-app python=3.9
   conda activate consent-app
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Your Perplexity AI API Key**
   - Save your API key in `.streamlit/secrets.toml`:
     ```
     [general]
     PERPLEXITY_API_KEY = "your_perplexity_api_key_here"
     ```
   - Or set it in your environment as `PERPLEXITY_API_KEY`.

5. **Run the App**
   ```bash
   streamlit run app.py
   ```

## App Workflow

1. **Enter Medical Notes:**  
   Paste/enter procedure record or code in the text area.
2. **Consent Summary:**  
   The app generates (and optionally reads aloud) a clear, patient-friendly summary.
3. **Q&A:**  
   Patients may ask questions by typing or voice—AI provides plain-language answers, also playable in audio.
4. **Consent:**  
   Patients record "I consent" (verified by local ASR) or provide a digital signature.
5. **Completion:**  
   The app thanks the user, logs only the record text and timestamp, and clears data for privacy.

## Customization & Extensibility

- Swap Perplexity LLM models by editing the `model` field in API calls.
- Local TTS/ASR can be substituted for platform-specific modules or newer libraries.
- Multilingual support can be added with small prompt/UI changes.
- Conversation/audit logging is not enabled by default, but modular code allows easy extension.

## Troubleshooting

- **API Issues:**  
  Ensure your Perplexity Pro key is valid and correctly set in `.streamlit/secrets.toml` or your environment.
- **Audio Errors:**  
  Ensure microphone and speaker permissions are granted; install missing audio dependencies as required.
- **Signature Pad:**  
  Requires `streamlit-drawable-canvas`.

## Acknowledgements

- Powered by Perplexity AI Pro, Streamlit, OpenAI Whisper, and open-source tools.

**This app is a prototype and NOT for clinical/production use. All data is processed for demonstration only.**

Feel free to copy/adapt this README for your GitHub repo—including updating your username, repo URL, or adding screenshots and contributors!
