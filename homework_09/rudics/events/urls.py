from django.urls import path
from .views import EventListView, EventDetailView, EventCreateView, EventDeleteView

urlpatterns = [
    path("", EventListView.as_view(), name="event_list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("add/", EventCreateView.as_view(), name="event_add"),
    path("delete/<int:pk>/", EventDeleteView.as_view(), name="event_delete"),
]
