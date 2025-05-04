from django.urls import path
from .views import (
    course_list_view, 
    last_courses,
    course_detail,
    course_materials,
    course_enrollments,
    course_requests,
    handle_request
)

urlpatterns = [
    path('courses/', course_list_view, name='course-list'),
    path('courses/latest/', last_courses, name='latest-courses'),
    path('courses/<int:pk>/', course_detail, name='course-detail'),
    path('courses/<int:pk>/materials/', course_materials, name='course-materials'),
    path('courses/<int:pk>/enrollments/', course_enrollments, name='course-enrollments'),
    path('courses/<int:pk>/requests/', course_requests, name='course-requests'),
    path('requests/<int:pk>/', handle_request, name='handle-request'),
]