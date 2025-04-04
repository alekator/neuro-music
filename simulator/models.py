from django.db import models

class EmotionProfile(models.Model):
    EMOTION_CHOICES = [
        ('relax', 'Расслабление'),
        ('happy', 'Радость'),
        ('sad', 'Грусть'),
    ]
    
    session_key = models.CharField(max_length=40, primary_key=True)
    stress_level = models.IntegerField()
    main_emotion = models.CharField(max_length=10, choices=EMOTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)