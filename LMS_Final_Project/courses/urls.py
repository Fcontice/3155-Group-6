from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('create-course/', views.create_course, name='create_course'),
    path('join-course/<int:course_id>/', views.join_course, name='join_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('course/<int:course_id>/gradebook/', views.gradebook, name='gradebook'),
    path('gradebook/', views.gradebook_overview, name='gradebook_overview'),
    path('profile/', views.profile, name='profile'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('course/<int:course_id>/discussions/', views.course_discussions, name='course_discussions'),
    path('course/<int:course_id>/discussions/create/', views.create_discussion, name='create_discussion'),
]
