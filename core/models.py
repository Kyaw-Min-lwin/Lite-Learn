from django.db import models
import os


class Lecture(models.Model):
    title = models.CharField(max_length=200)
    # The heavy original video
    original_video = models.FileField(upload_to="videos/")

    # The processed lightweight assets (initially blank)
    processed_audio = models.FileField(upload_to="audio/", blank=True, null=True)
    transcript = models.TextField(blank=True)
    summary = models.TextField(blank=True)

    # Impact Metrics (to show off to judges)
    original_size_mb = models.FloatField(default=0)
    new_size_mb = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate original size if video exists
        if self.original_video and not self.original_size_mb:
            # Basic size estimation in MB
            try:
                self.original_size_mb = round(
                    self.original_video.size / (1024 * 1024), 2
                )
            except:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def data_saved_percentage(self):
        if self.original_size_mb > 0 and self.new_size_mb > 0:
            saved = (
                (self.original_size_mb - self.new_size_mb) / self.original_size_mb
            ) * 100
            return round(saved, 1)
        return 0
