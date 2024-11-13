from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView.as_view(),name='portfolio'),
    path('contact/', views.contact_view, name='contact'),
]
