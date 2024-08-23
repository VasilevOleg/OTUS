from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm
from django.shortcuts import get_object_or_404

def index(request):
    events = Event.objects.all()
    return render(request, 'myapp/index.html', {'events': events})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = EventForm()
    return render(request, 'myapp/event_form.html', {'form': form})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        return redirect('index')