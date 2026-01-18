import os
import subprocess
import whisper
import shutil
import uuid


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

    def process_lecture(self, video_path, output_dir):
        # 2. Generate a SAFE, short filename to avoid Windows 260 char limit errors
        safe_id = str(uuid.uuid4())[:8]
        filename = f"lecture_{safe_id}"

        audio_path = os.path.join(output_dir, f"{filename}.mp3")
        transcript_path = os.path.join(output_dir, f"{filename}.txt")

        print(f"Processing video: {video_path}")
        print(f"Saving audio to: {audio_path}")

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
        summary = full_text[:500] + "... (Summary truncated)"

        # 7. Calculate Stats
        original_size = os.path.getsize(video_path)
        new_size = os.path.getsize(audio_path)

        return {
            "title": filename,
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
