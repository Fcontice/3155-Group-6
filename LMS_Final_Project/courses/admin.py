from django.contrib import admin
from .models import Course, Assignment, Submission, UserProfile

admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(UserProfile)