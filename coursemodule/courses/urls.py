from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course-list'),
    path('last/', views.last_courses, name='last-courses'),
    path('<int:pk>/', views.course_detail, name='course-detail'),
    path('<int:pk>/materials/', views.course_materials, name='course-materials'),
    path('<int:pk>/enrollments/', views.course_enrollments, name='course-enrollments'),
    path('<int:pk>/requests/', views.course_requests, name='course-requests'),
    path('requests/<int:pk>/', views.handle_request, name='handle-request'),
]