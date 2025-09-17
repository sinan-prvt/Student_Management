from django.contrib import admin
from .models import Student, Course, Lesson, Enrollment
# Register your models here.


admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)