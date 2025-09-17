from django.db import models
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    

class Course(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    tags = models.JSONField(default=list)  

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    LESSON_TYPES = [
        ('Video', 'Video'),
        ('PDF', 'PDF'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPES)
    video_url = EmbedVideoField(blank=True, null=True)  
    file = models.FileField(upload_to="lessons/", blank=True, null=True)  
    order = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    completed_lessons = models.ManyToManyField(Lesson, blank=True)

    class Meta:
        unique_together = ('student', 'course')  

    def __str__(self):
        return f"{self.student.user.username} -> {self.course.title}"
