from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('add/', views.add_event, name='add_event'),  # Добавление нового события
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),  # Удаление события
]
