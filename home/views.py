from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from .forms import StudentSignupForm, StudentProfileUpdateForm
from .models import Student, Enrollment, Course, Lesson
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import re
from django import template

# -------------------------
# Student Signup
# -------------------------
def student_signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            # Create Student profile automatically
            Student.objects.create(user=user)

            # Auto-login
            auth_login(request, user)
            messages.success(request, "🎉 Welcome! Your account has been created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = StudentSignupForm()
    return render(request, 'signup.html', {'form': form})


# -------------------------
# Email Verification
# -------------------------
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "✅ Email verified successfully! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "❌ Invalid or expired verification link.")
        return redirect('signup')


# -------------------------
# Student Login
# -------------------------
def student_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            messages.success(request, f"👋 Welcome back, {user.username}!")

            # Role-based redirect
            if user.is_staff:  # Admin user
                return redirect('/admin/')
            else:  # Normal student
                return redirect('dashboard')

        else:
            messages.error(request, "⚠️ Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


# -------------------------
# Logout
# -------------------------
def student_logout(request):
    logout(request)
    messages.success(request, "👋 Logged out successfully!")
    return redirect('index')


# -------------------------
# Home / Index
# -------------------------
def index(request):
    return render(request, 'index.html')


# -------------------------
# User Dashboard
# -------------------------
@login_required
def user_dashboard(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "⚠️ Your student profile is missing. Please contact admin.")
        return redirect('index')
    
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    completed_courses = 0
    for e in enrollments:
        total = e.course.lessons.count()
        completed = e.completed_lessons.count()
        e.progress_percent = int((completed / total) * 100) if total else 0
        if e.progress_percent == 100:
            completed_courses += 1

    pending_courses = len(enrollments) - completed_courses
    all_courses = Course.objects.all()
    enrolled_courses_ids = enrollments.values_list('course_id', flat=True)

    return render(request, 'dashboard.html', {
        'student': student,
        'enrollments': enrollments,
        'all_courses': all_courses,
        'enrolled_courses_ids': enrolled_courses_ids,
        'completed_courses': completed_courses,
        'pending_courses': pending_courses,
    })


# -------------------------
# Enrollments Page
# -------------------------
@login_required
def enrollments_page(request):
    student = get_object_or_404(Student, user=request.user)
    all_courses = Course.objects.all()
    enrollments = Enrollment.objects.filter(student=student)
    enrolled_courses_ids = enrollments.values_list('course_id', flat=True)

    context = {
        'student': student,
        'all_courses': all_courses,
        'enrolled_courses_ids': enrolled_courses_ids,
    }
    return render(request, 'enrollment.html', context)


@login_required
def enroll_course(request, course_id):
    student = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    
    enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
    
    if created:
        messages.success(request, f"🎉 You have successfully enrolled in '{course.title}'!")
    else:
        messages.info(request, f"ℹ️ You are already enrolled in '{course.title}'.")
    
    return redirect('enrollments_page')


def unenroll_course(request, course_id):
    if request.method == "POST" and request.user.is_authenticated:
        course = get_object_or_404(Course, id=course_id)
        Enrollment.objects.filter(student=request.user.student, course=course).delete()
    return redirect("enrollments_page") 


# -------------------------
# User Profile / Update
# -------------------------
@login_required
def user_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.user != student.user:
        messages.error(request, "⚠️ You are not allowed to edit this profile.")
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentProfileUpdateForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            student.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect("user_detail", pk=student.pk)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = StudentProfileUpdateForm(instance=student, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        })

    enrollments = student.enrollments.all()
    return render(request, "user_detail.html", {
        "student": student,
        "form": form,
        "enrollments": enrollments
    })


# -------------------------
# Course List & Detail
# -------------------------
@login_required
def course(request):
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student).select_related('course')

    for e in enrollments:
        total_lessons = e.course.lessons.count()
        completed = e.completed_lessons.count()
        e.progress_percent = int((completed / total_lessons) * 100) if total_lessons else 0

    return render(request, 'course.html', {"enrollments": enrollments})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    student = request.user.student
    enrollment = get_object_or_404(Enrollment, student=student, course=course)
    completed_lessons = enrollment.completed_lessons.all()

    return render(request, 'lesson_list.html', {
        'course': course,
        'lessons': lessons,
        'completed_lessons': completed_lessons,
    })


# -------------------------
# Lessons
# -------------------------
def lesson_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    return render(request, 'lesson_list.html', {'course': course, 'lessons': lessons})


@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    enrollment = get_object_or_404(Enrollment, student=request.user.student, course=course)
    completed_lessons = enrollment.completed_lessons.all()

    lessons = list(course.lessons.order_by('order'))
    current_index = lessons.index(lesson)
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None

    return render(request, 'lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'completed_lessons': completed_lessons,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    })


@login_required
def complete_lesson(request, course_id, lesson_id):
    if request.method == "POST":
        enrollment = get_object_or_404(Enrollment, student=request.user.student, course_id=course_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)

        if lesson not in enrollment.completed_lessons.all():
            enrollment.completed_lessons.add(lesson)
            total = enrollment.course.lessons.count()
            done = enrollment.completed_lessons.count()
            enrollment.progress = int((done / total) * 100)
            enrollment.save()
            messages.success(request, f"✅ Lesson '{lesson.title}' marked as complete!")
        else:
            messages.info(request, f"ℹ️ Lesson '{lesson.title}' is already completed.")

        return redirect("course_detail", course_id=course_id)


# -------------------------
# Custom YouTube Embed Filter
# -------------------------
register = template.Library()

@register.filter
def youtube_embed(url):
    match = re.search(r'(?:v=|youtu\.be/|v=)([\w-]{11})', url)
    if match:
        return f'https://www.youtube.com/embed/{match.group(1)}'
    return url
