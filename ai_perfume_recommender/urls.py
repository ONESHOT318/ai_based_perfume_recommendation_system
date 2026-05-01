from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('autocomplete/', views.perfume_autocomplete, name='perfume_autocomplete'),
    path('note-autocomplete/', views.note_autocomplete, name='note_autocomplete'),
]