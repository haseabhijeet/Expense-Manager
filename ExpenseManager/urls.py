"""
URL configuration for ExpenseManager project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
    path('api/', include('expenses.api_urls')),
]
