# EchoMind – AI Meeting Intelligence Assistant

EchoMind is an AI-powered Meeting Intelligence Assistant built with Python that transforms meeting audio into structured insights, searchable knowledge, and interactive conversations.

The application can process YouTube meeting videos or uploaded audio files, generate transcripts using local Whisper transcription, summarize discussions using Mistral AI with LangChain LCEL pipelines, extract action items and key decisions, and enable conversational Q&A using a RAG pipeline powered by ChromaDB and Hugging Face embeddings.

---

# Features

## Audio Input Support

* Process YouTube video URLs
* Upload local audio files
* Automatic audio extraction using yt-dlp + FFmpeg

## AI Transcription

* Local Whisper transcription
* Hindi / Hinglish support
* Audio chunking for long meetings
* Fast and efficient processing pipeline

## AI Summarization

* Meeting summaries
* Action item extraction
* Key decision extraction
* Structured meeting insights

## RAG-Based Meeting Chat

* Chat with meeting transcripts
* Semantic search using embeddings
* ChromaDB vector storage
* Context-aware question answering

## Export Support

* Export transcript and summaries as:

  * PDF
  * TXT

## Interactive UI

* Streamlit-based user interface
* Clean workflow for processing meetings
* Easy interaction with transcript knowledge base

---

# Tech Stack

## Backend

* Python
* FastAPI (planned)

## AI / NLP

* Whisper
* Mistral AI
* LangChain LCEL
* Hugging Face Embeddings

## RAG Pipeline

* ChromaDB
* Sentence Transformers

## Frontend

* Streamlit

## Audio Processing

* yt-dlp
* FFmpeg
* pydub

---

# Architecture

```text
YouTube URL / Audio File
            ↓
      Audio Extraction
            ↓
       Audio Chunking
            ↓
     Whisper Transcription
            ↓
   Translation (if needed)
            ↓
     Meeting Summarization
            ↓
  Action Items & Decisions
            ↓
        Text Chunking
            ↓
   HuggingFace Embeddings
            ↓
         ChromaDB
            ↓
        RAG Pipeline
            ↓
      Conversational Q&A
            ↓
         Streamlit UI
```

---

# Project Structure

```text
EchoMind/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
├── .gitignore
│
├── core/
│   ├── extractor.py
│   ├── summarizer.py
│   ├── transcriber.py
│   ├── rag_engine.py
│   └── vector_store.py
│
├── utils/
│   ├── audio_processor.py
│   └── youtube_utils.py
│
├── downloads/
├── chunks/
├── chroma_db/
└── exports/
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/rathorepriyansh01/echomind.git
cd echomind
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_api_key
SARVAM_API_KEY=your_api_key
```

---

# FFmpeg Setup

FFmpeg is required for audio processing.

Download:
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Add FFmpeg to your system PATH.

Verify installation:

```bash
ffmpeg -version
```

---

# Running the Application

## Streamlit App

```bash
streamlit run app.py
```

## CLI Pipeline

```bash
python main.py
```

---

# Example Workflow

1. Enter YouTube URL or upload audio file
2. Audio gets downloaded and processed
3. Whisper generates transcript
4. Mistral AI summarizes meeting
5. Action items and key decisions extracted
6. Transcript indexed into ChromaDB
7. User chats with meeting using RAG

---

# Future Improvements

* Speaker diarization
* Multi-meeting memory
* Team workspace support
* Real-time meeting assistant
* Voice interaction
* Cloud deployment
* FastAPI backend integration
* Authentication system
* Meeting analytics dashboard

---

# Why EchoMind?

EchoMind is designed to transform meetings into searchable organizational memory.

Instead of manually revisiting long recordings or notes, users can:

* retrieve decisions instantly
* search conversations semantically
* track action items
* summarize discussions automatically
* interact with meetings conversationally

---

# Author

## Priyansh Rathore

B.Tech CSE AIML Student
AI Enthusiast | Python Developer | RAG & LLM Explorer

GitHub:
[https://github.com/rathorepriyansh01](https://github.com/rathorepriyansh01)

---

# License

This project is built for learning, experimentation, and portfolio purposes.
