from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.student_signup, name='signup'),
    path('login/', views.student_login, name='login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),

    path('course/', views.course, name='course'),       
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/lessons/', views.lesson_list, name='lesson_list'),
    path("course/<int:course_id>/lesson/<int:lesson_id>/", views.lesson_detail, name="lesson_detail"),
    path('course/<int:course_id>/lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),

    path('enrollments/', views.enrollments_page, name='enrollments_page'),
    path('enroll_course/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path("courses/<int:course_id>/unenroll/", views.unenroll_course, name="unenroll_course"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
