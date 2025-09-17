from django.contrib import admin
from .models import Student, Course, Lesson, Enrollment
from embed_video.admin import AdminVideoMixin

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level')
    list_filter = ('level', 'category')
    search_fields = ('title', 'category')

@admin.register(Lesson)
class LessonAdmin(AdminVideoMixin, admin.ModelAdmin):
    list_display = ('title', 'course', 'lesson_type')
    list_filter = ('lesson_type', 'course')
    search_fields = ('title',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'progress')
    list_filter = ('course',)
    search_fields = ('student__user__username', 'course__title')
