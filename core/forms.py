from django import forms
from .models import Lecture


class LectureUploadForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ["title", "original_video"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Lecture Title"}
            ),
            "original_video": forms.FileInput(attrs={"class": "form-control"}),
        }
