from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.views import custom_login, custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('login/', custom_login, name='custom_login'),
    path('logout/', custom_logout, name='custom_logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)