from django.db import models
from django.contrib.auth.models import User

class RoadFeedback(models.Model):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('very_poor', 'Very Poor'),
    ]

    ISSUE_TYPES = [
        ('pothole', 'Potholes'),
        ('cracks', 'Cracks'),
        ('drainage', 'Drainage Issues'),
        ('signs', 'Missing/Damaged Signs'),
        ('lighting', 'Poor Lighting'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    road_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES)
    description = models.TextField()
    image = models.ImageField(upload_to='road_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.road_name} - {self.location} ({self.created_at.date()})"

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    """User comments attached to a RoadFeedback entry."""
    feedback = models.ForeignKey(RoadFeedback, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # oldest first for conversational flow

    def __str__(self):
        return f"Comment by {self.user.username} on {self.feedback.id}" 
