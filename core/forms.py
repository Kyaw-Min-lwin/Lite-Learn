from django import forms
from .models import Lecture


class LectureUploadForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ["title", "original_video", "youtube_url"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Lecture Title (Optional for YouTube)",
                }
            ),
            "original_video": forms.FileInput(attrs={"class": "form-control"}),
            "youtube_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "Paste YouTube URL here"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        video = cleaned_data.get("original_video")
        url = cleaned_data.get("youtube_url")

        if not video and not url:
            raise forms.ValidationError("Please upload a video OR paste a YouTube URL.")
        return cleaned_data
