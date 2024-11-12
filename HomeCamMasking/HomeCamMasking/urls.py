# HomeCamMasking/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('masking/', include('masking.urls')),  # 마스킹 앱 URL 포함
]
