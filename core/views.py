from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.base import ContentFile
import os

from .models import Lecture
from .forms import LectureUploadForm
from .media_processor import ContentProcessor


def upload_lecture(request):
    if request.method == "POST":
        form = LectureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Save the initial video object
            lecture = form.save()

            # 2. Initialize our Processor
            processor = ContentProcessor()

            # 3. Define paths
            # We need the absolute path of the uploaded video for FFmpeg
            video_path = lecture.original_video.path
            output_dir = os.path.join(settings.MEDIA_ROOT, "processed")
            os.makedirs(output_dir, exist_ok=True)

            # 4. RUN THE HEAVY LIFTING (This will take time!)
            print(f"Processing {lecture.title}...")  # Check your console
            try:
                results = processor.process_lecture(video_path, output_dir)

                # 5. Update the Database with results
                # We open the generated audio file and save it to the Django model
                with open(results["audio_url"], "rb") as f:
                    lecture.processed_audio.save(
                        f"{lecture.title}_low.mp3", ContentFile(f.read())
                    )

                lecture.transcript = results["transcript"]
                lecture.summary = results["summary"]
                lecture.new_size_mb = results["new_size_mb"]
                lecture.save()

                print("Processing Complete.")
                return redirect("lecture_detail", pk=lecture.pk)

            except Exception as e:
                print(f"Error: {e}")
                # In real life, handle errors gracefully
                pass

    else:
        form = LectureUploadForm()

    return render(request, "core/upload.html", {"form": form})


def lecture_detail(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    return render(request, "core/lecture_detail.html", {"lecture": lecture})
