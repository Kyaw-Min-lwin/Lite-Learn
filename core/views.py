from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import FileResponse
import os


from .models import Lecture
from .forms import LectureUploadForm
from .media_processor import ContentProcessor
from .pdf_generator import generate_lecture_pdf


def upload_lecture(request):
    if request.method == "POST":
        form = LectureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)  # Don't save to DB yet

            processor = ContentProcessor()
            output_dir = os.path.join(settings.MEDIA_ROOT, "processed")
            os.makedirs(output_dir, exist_ok=True)

            try:
                # BRANCH A: YouTube URL
                if lecture.youtube_url:
                    results = processor.process_youtube(lecture.youtube_url, output_dir)
                    # Use the title from YouTube if user didn't provide one
                    if not lecture.title:
                        lecture.title = results["title"]
                    lecture.save()  # Now we save to get an ID

                # BRANCH B: File Upload
                elif lecture.original_video:
                    lecture.save()  # Save first to get file path
                    video_path = lecture.original_video.path
                    results = processor.process_lecture(video_path, output_dir)

                # Common Wrap-up
                with open(results["audio_url"], "rb") as f:
                    lecture.processed_audio.save(
                        f"{lecture.title[:20]}_audio.mp3", ContentFile(f.read())
                    )

                lecture.transcript = results["transcript"]
                lecture.summary = results["summary"]
                lecture.new_size_mb = results["new_size_mb"]
                # For YouTube, we don't know "original size" exactly,
                # so we can mock it or leave it 0.
                if lecture.youtube_url and lecture.original_size_mb == 0:
                    # Estimate: 1 minute of 1080p video is roughly 20MB
                    # This is a rough heuristic for the 'Data Saved' display
                    lecture.original_size_mb = lecture.new_size_mb * 15

                lecture.save()
                return redirect("lecture_detail", pk=lecture.pk)

            except Exception as e:
                print(f"Error: {e}")
                # Add error handling here

    else:
        form = LectureUploadForm()

    return render(request, "core/upload.html", {"form": form})


def lecture_detail(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    return render(request, "core/lecture_detail.html", {"lecture": lecture})


def download_pdf(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)

    # Generate the PDF in memory
    pdf_buffer = generate_lecture_pdf(lecture)

    # Return as a downloadable file
    filename = f"{lecture.title[:20].replace(' ', '_')}_Notes.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)
