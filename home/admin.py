from django.contrib import admin
from .models import Student, Course, Lesson, Enrollment
# from embed_video.admin import AdminVideoMixin

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)