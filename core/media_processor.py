import os
import subprocess
import whisper
import shutil
import uuid
import yt_dlp
import google.generativeai as genai
from dotenv import load_dotenv
import markdown

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No API key found. Please check your .env file.")

# 3. Configure Gemini
genai.configure(api_key=api_key)
class ContentProcessor:
    def __init__(self):
        # 1. Check if FFmpeg is actually visible to Python
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError(
                "FFmpeg not found! Make sure it's installed and added to your System PATH. "
                "Restart VS Code if you just installed it."
            )

        print("Loading Whisper Model...")
        # Use 'base' or 'tiny' for speed.
        self.transcriber = whisper.load_model("base")
        self.ai_model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_ai_summary(self, transcript_text):
        """Sends transcript to Gemini for a structured summary."""
        print("Contacting Gemini API for summary...")

        prompt = f"""
        You are an expert academic tutor. 
        Analyze the following lecture transcript and produce a concise study guide.
        
        Structure your response exactly like this:
        **1. Core Subject:** (One sentence on what this is about)
        **2. Key Concepts:** (3-5 bullet points of the most important ideas)
        **3. Detailed Summary:** (A 2-paragraph explanation of the content)
        
        TRANSCRIPT:
        {transcript_text}
        """

        try:
            response_text = self.ai_model.generate_content(prompt).text
            html_text = markdown.markdown(response_text)
            return html_text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            # Fallback if API fails (no internet, quota limit, etc.)
            return f"AI Summary Unavailable. Preview: {transcript_text[:500]}..."

    def process_lecture(self, video_path, output_dir):
        # 2. Generate a SAFE, short filename to avoid Windows 260 char limit errors
        safe_id = str(uuid.uuid4())[:8]
        filename = f"lecture_{safe_id}"

        audio_path = os.path.join(output_dir, f"{filename}.mp3")

        # 3. Compress Audio
        # We use -y to overwrite if exists
        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",
            "-ac",
            "1",
            "-ab",
            "32k",
            "-ar",
            "22050",
            "-y",
            audio_path,
        ]

        try:
            # We allow stdout/stderr to show in console so you can see if FFmpeg errors
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print("FFmpeg failed to convert video.")
            raise e

        # 4. Verify Audio File Exists and isn't empty
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise FileNotFoundError(f"Audio file was not created: {audio_path}")

        # 5. Transcribe
        print("Transcribing (this may take a moment)...")
        try:
            # fp16=False prevents warnings on CPU
            result = self.transcriber.transcribe(audio_path, fp16=False)
            full_text = result["text"]
        except Exception as e:
            print(f"Whisper crashed: {e}")
            raise e

        # 6. Generate Summary
        summary = self.generate_ai_summary(full_text)

        # 7. Calculate Stats
        new_size = os.path.getsize(audio_path)

        return {
            "title": filename,
            "audio_url": audio_path,
            "transcript": full_text,
            "summary": summary,
            "new_size_mb": round(new_size / (1024 * 1024), 2),
        }

    def process_youtube(self, url, output_dir):
        # 1. Generate Safe Filename
        safe_id = str(uuid.uuid4())[:8]
        filename = f"yt_lecture_{safe_id}"
        audio_path = os.path.join(output_dir, f"{filename}.mp3")

        print(f"Downloading Audio from YouTube: {url}")

        # 2. Configure yt-dlp options
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, f"{filename}.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "32",  # Low bandwidth target
                }
            ],
            "quiet": True,
        }

        # 3. Download
        meta = {}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                meta["title"] = info.get("title", "Unknown Title")
                meta["duration"] = info.get("duration", 0)
                # yt-dlp might save as .mp3 directly depending on codec,
                # but we enforced conversion. Let's ensure path is correct.
                # Sometimes it saves as filename.mp3, check existence:
                if not os.path.exists(audio_path):
                    # Fallback check if it saved with a different extension
                    pass
        except Exception as e:
            print(f"YouTube Download Error: {e}")
            raise e

        # 4. Transcribe (Reuse the existing logic logic, but easier)
        # Verify file existence first
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"YouTube audio download failed for {audio_path}")

        print("Transcribing YouTube Audio...")
        result = self.transcriber.transcribe(audio_path, fp16=False)
        full_text = result["text"]

        # 5. Summary & Stats
        summary = self.generate_ai_summary(full_text)
        new_size = os.path.getsize(audio_path)

        return {
            "title": meta["title"],  # Return the real YouTube title
            "audio_url": audio_path,
            "transcript": full_text,
            "summary": summary,
            "new_size_mb": round(new_size / (1024 * 1024), 2),
        }


# --- Example Usage (If running locally) ---
if __name__ == "__main__":
    # Mocking the process
    # processor = ContentProcessor()
    # result = processor.process_lecture("my_lecture.mp4", "./output")
    # print(result)
    pass
