from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from .forms import StudentSignupForm, StudentProfileUpdateForm
from .models import Student, Enrollment, Course, Lesson
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from .filters import CourseFilter
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.encoding import force_str  
from django.http import Http404



def student_signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()

            current_site = get_current_site(request)
            subject = "Verify your email for Skilloria "
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = f"http://{current_site.domain}/verify/{uid}/{token}/"
            
            message = render_to_string('email_verification.html', {
                'user': user,
                'verification_link': verification_link
            })

            send_mail(
                subject,
                message,
                'no-reply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "Account created! Please check your email to verify your account.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentSignupForm()
    return render(request, 'signup.html', {'form': form})


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified successfully! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('signup')


def student_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            messages.success(request, f"Welcome back, {user.username}!")

            if user.is_staff: 
                return redirect('/admin/')
            else:
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def student_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('index')


@login_required
def user_detail(request, pk):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "Student not found")
        return redirect('enrollment')
    
    if request.user != student.user:
        messages.error(request, "You are not allowed to edit this profile.")
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
            messages.success(request, "Profile updated successfully!")
            return redirect("user_detail", pk=student.pk)
        else:
            messages.error(request, "Please correct the errors below.")
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


def index(request):
    return render(request, 'index.html')


@login_required
def user_dashboard(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "Your student profile is missing. Please contact admin.")
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


@login_required
def enrollments_page(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, "Student not found")
        return redirect('enrollment')
    all_courses_qs = Course.objects.all()

    course_filter = CourseFilter(request.GET, queryset=all_courses_qs)
    filtered_courses = course_filter.qs

    paginator = Paginator(filtered_courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    enrollments = Enrollment.objects.filter(student=student)
    enrolled_courses_ids = enrollments.values_list('course_id', flat=True)

    context = {
        'student': student,
        'filter': course_filter,
        'all_courses': page_obj,          
        'page_obj': page_obj,
        'enrolled_courses_ids': enrolled_courses_ids,
    }
    return render(request, 'enrollment.html', context)


@login_required
def enroll_course(request, course_id):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, "Student not Found")
        return redirect('enrollment')
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise Http404("Course not found")
    
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    
    if enrollment:
        messages.info(request, f"You are already enrolled in '{course.title}'.")
    else:
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, f"You have successfully enrolled in '{course.title}'!")

    return redirect('enrollments_page')
    


@login_required
def unenroll_course(request, course_id):
    if request.method == "POST" and request.user.is_authenticated:
        course = Course.objects.filter(id=course_id).first()
        if not course:
            messages.error(request, "Course not found")
            return redirect('lesson_list')
        
        Enrollment.objects.filter(student=request.user.student, course=course).delete()
    return redirect("enrollments_page") 



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
    course = Course.objects.filter(id=course_id).first()
    if not course:
        messages.error(request, "Course not found")
        return redirect('lesson_list')
    
    lessons = course.lessons.all().order_by('order')
    student = request.user.student

    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        messages.error(request, "Enrollment not found")
        return redirect('lesson_details')
    completed_lessons = enrollment.completed_lessons.all()

    return render(request, 'lesson_list.html', {
        'course': course,
        'lessons': lessons,
        'completed_lessons': completed_lessons,
    })


@login_required
def lesson_list(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        messages.error(request, "Courses not found")
        return redirect('lesson_list')
    lessons = course.lessons.all().order_by('order')
    return render(request, 'lesson_list.html', {'course': course, 'lessons': lessons})


@login_required
def lesson_detail(request, course_id, lesson_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        messages.error(request, "Course not found")
        return redirect('lesson_list')
    
    lesson = Lesson.objects.filter(id=lesson_id, course=course).first()
    if not lesson:
        messages.error(request, "Lesson not found")
        return redirect('lesson_detail')

    enrollment = Enrollment.objects.filter(student=request.user.student, course=course).first()
    if not enrollment:
        messages.error(request, "Enrollment not found")
        return redirect('lesson_details')
    
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
        enrollment = Enrollment.objects.filter(
            student=request.user.student, course_id=course_id
        ).first()
        if not enrollment:
            messages.error(request, "Enrollment not found")
            return redirect('lesson_list')
        
        lesson = Lesson.objects.filter(id=lesson_id, course_id=course_id).first()
        if not lesson:
            messages.error(request, "Lesson not found")
            return redirect('lesson_detil', course_id=course_id)

        if lesson not in enrollment.completed_lessons.all():
            enrollment.completed_lessons.add(lesson)
            total = enrollment.course.lessons.count()
            done = enrollment.completed_lessons.count()
            enrollment.progress = int((done / total) * 100)
            enrollment.save()
            messages.success(request, f"Lesson '{lesson.title}' marked as complete!")
        else:
            messages.info(request, f"Lesson '{lesson.title}' is already completed.")

        return redirect("course_detail", course_id=course_id)
