from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'calender'  # ✅ آپ کی app کا correct نام
