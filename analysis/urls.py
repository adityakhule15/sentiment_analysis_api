from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_reviews, name='upload_reviews'),
]
