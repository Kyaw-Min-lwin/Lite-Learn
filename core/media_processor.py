import os
import subprocess
import whisper
from moviepy import VideoFileClip
import shutil
import uuid
# Note: For summarization, you might use HuggingFace transformers or a simple frequency-based summarizer
# from transformers import pipeline

import os
os.environ["IMAGEIO_FFMPEG_EXE"] = r"D:\ffmpeg-2026-01-14-git-6c878f8b82-essentials_build\ffmpeg-2026-01-14-git-6c878f8b82-essentials_build\bin\ffmpeg.exe"

class ContentProcessor:
    def __init__(self):
        # Load the base model. 'tiny' or 'base' are fast and good enough for clear lectures.
        print("Loading Whisper Model...")
        self.transcriber = whisper.load_model("base")
        # self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def process_lecture(self, video_path, output_dir):
        """
        Takes a video file, extracts low-bitrate audio, and generates a text summary.
        Returns a dictionary of file paths and stats.
        """
        safe_id = str(uuid.uuid4())[:8]
        filename = f"lecture_{safe_id}"
        audio_path = os.path.join(output_dir, f"{filename}_low.mp3")
        transcript_path = os.path.join(output_dir, f"{filename}_transcript.txt")

        # 1. Extract and Compress Audio (using FFmpeg via subprocess for control)
        # -ac 1: Mono audio (saves data)
        # -ab 32k: 32kbps bitrate (very low, but readable for speech)
        # -vn: No video
        print(f"Compressing Audio for {filename}...")
        ffmpeg_path = r"D:\ffmpeg-2026-01-14-git-6c878f8b82-essentials_build\ffmpeg-2026-01-14-git-6c878f8b82-essentials_build\bin\ffmpeg.exe"
        command = [
            ffmpeg_path,
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
            audio_path,  # -y overwrites output
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 2. Transcribe Text
        print("Transcribing...")
        result = self.transcriber.transcribe(audio_path)
        full_text = result["text"]

        # 3. Generate Summary (Simple truncation mock-up for this script)
        # In production, use the 'summarizer' pipeline commented out above
        summary = full_text[:500] + "... (Summary truncated for demo)"

        # Save Transcript
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        # Calculate Data Savings
        original_size = os.path.getsize(video_path)
        new_size = os.path.getsize(audio_path) + os.path.getsize(transcript_path)
        savings = ((original_size - new_size) / original_size) * 100

        return {
            "title": filename,
            "audio_url": audio_path,
            "transcript": full_text,
            "summary": summary,
            "original_size_mb": round(original_size / (1024 * 1024), 2),
            "new_size_mb": round(new_size / (1024 * 1024), 2),
            "data_saved_percent": round(savings, 1),
        }


# --- Example Usage (If running locally) ---
if __name__ == "__main__":
    # Mocking the process
    # processor = ContentProcessor()
    # result = processor.process_lecture("my_lecture.mp4", "./output")
    # print(result)
    pass
