# ⚡ LiteLearn MM: Low-Bandwidth Learning Platform

Bridging the digital divide in Myanmar by reducing educational data usage by 95%.

## 📖 The Problem

In developing regions like Myanmar, internet access is often unstable, slow, or prohibitively expensive. Students cannot afford to stream 500MB video lectures, creating a massive knowledge gap compared to their peers in developed nations.

## 💡 The Solution

LiteLearn is an offline-first educational tool that transforms heavy video content into lightweight, accessible assets.

Video Processing: Extracts audio and compresses it to "Radio Quality" (32kbps mono).

AI Intelligence: Uses OpenAI Whisper for transcription and Google Gemini 1.5 Flash for structured summarization.

Portability: Generates a downloadable PDF containing the summary and transcript for offline study.

Impact: A 200MB video lecture is converted into a 5MB audio+text package.

## 🛠 Tech Stack

Backend: Django (Python 3.10+)

Media Processing: FFmpeg, yt-dlp (YouTube extraction)

## AI Models:

Transcription: openai-whisper (Base model)

Summarization: Google Gemini API (gemini-1.5-flash)

PDF Generation: ReportLab

Database: SQLite (Prototype) / PostgreSQL (Production)

## ✨ Key Features

Dual Ingestion: Upload local video files OR paste YouTube links.

Smart Compression: Automatically strips video tracks to isolate audio.

AI Study Guides: Auto-generates "Key Concepts" and summaries using LLMs.

Data Saver Dashboard: Visualizes the exact MB saved for every lecture.

Offline PDF: One-click download of all notes and transcripts.

## 🚀 Installation & Setup

Prerequisites

Python 3.8+ installed.

FFmpeg installed and added to your System PATH.



## 🧪 How It Works (Under the Hood)

Ingestion: The app accepts a file or URL.

Extraction: yt-dlp or ffmpeg extracts the audio track using -ac 1 (mono) and -ab 32k (low bitrate).

Transcription: The audio is passed through the Whisper base model to generate a timestamped text.

Reasoning: The transcript is sent to Gemini Flash with a prompt to "act as an academic tutor" and extract key bullet points.

Generation: ReportLab renders the text into a clean PDF layout for download.

## 🔮 Future Roadmap

[ ] Burmese Language Support: Fine-tune Whisper for better local dialect recognition.

[ ] PWA (Progressive Web App): Allow offline caching on Android devices.

[ ] SMS Fallback: Send text-only summaries via SMS for users with 0 data.

👨‍💻 Author

Built with ❤️ for Myanmar.


