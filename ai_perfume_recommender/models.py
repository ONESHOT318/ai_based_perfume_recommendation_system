from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='note_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Perfume(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    notes = models.ManyToManyField(Note, related_name='perfumes')
    season = models.CharField(max_length=100)
    longevity = models.CharField(max_length=100)
    image = models.ImageField(upload_to='perfume_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.brand} - {self.name}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_text = models.CharField(max_length=255)
    liked = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {'Liked' if self.liked else 'Disliked'}"
