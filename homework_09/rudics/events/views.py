from django.views.generic import ListView, DetailView, CreateView, DeleteView
from .models import Event
from .forms import EventForm
from django.urls import reverse_lazy


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 10


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("event_list")


class EventDeleteView(DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("event_list")
