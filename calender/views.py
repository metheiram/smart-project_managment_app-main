from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
 
def calender_view(request):
    return render(request, 'calender/calender.html')

def get_events_json(request):
    events = Event.objects.all()
    events_data = [
        {
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'color': event.color
        } for event in events
    ]
    return JsonResponse(events_data, safe=False)

@csrf_exempt  # for JS POST without CSRF (not recommended for production)
def create_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            title = data.get('title')
            start = parse_datetime(data.get('start'))
            end = parse_datetime(data.get('end'))
            color = data.get('color', '#3b82f6')  # default color

            Event.objects.create(title=title, start_time=start, end_time=end, color=color)
            return JsonResponse({'message': 'Event created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
