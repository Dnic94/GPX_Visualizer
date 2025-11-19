from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, RouteForm
from .models import Route
import gpxpy
import gpxpy.gpx
from tcxparser import TCXParser
from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = (sin(dLat / 2) * sin(dLat / 2) +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dLon / 2) * sin(dLon / 2))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


from .models import ActivityType


@login_required
def upload_route(request):
    if request.method == 'POST':
        form = RouteForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('files')
            for i, uploaded_file in enumerate(uploaded_files):
                points = []
                total_length = 0
                if uploaded_file.name.endswith('.gpx'):
                    gpx = gpxpy.parse(uploaded_file)
                    for track in gpx.tracks:
                        for segment in track.segments:
                            for point in segment.points:
                                points.append(
                                    [point.latitude, point.longitude]
                                )
                    # Convert to km
                    total_length = gpx.length_3d() / 1000
                elif uploaded_file.name.endswith('.tcx'):
                    # For TCX, we need to decode the file content
                    tcx_content = uploaded_file.read().decode('utf-8')
                    tcx = TCXParser(tcx_content)
                    if tcx.position_values:
                        for j in range(len(tcx.position_values) - 1):
                            lat1, lon1 = tcx.position_values[j]
                            lat2, lon2 = tcx.position_values[j+1]
                            points.append([lat1, lon1])
                            total_length += haversine(lat1, lon1, lat2, lon2)
                        # Add the last point
                        last_point = tcx.position_values[-1]
                        points.append([last_point[0], last_point[1]])

                route_name = request.POST.get(f'name_{i}')
                activity_type_id = request.POST.get(f'activity_type_{i}')
                activity_type = ActivityType.objects.get(pk=activity_type_id)

                if points and route_name and activity_type:
                    Route.objects.create(
                        user=request.user,
                        name=route_name,
                        activity_type=activity_type,
                        points=points,
                        length=total_length
                    )
            return redirect('home')
    else:
        form = RouteForm()
    return render(request, 'upload_route.html', {'form': form})


def home(request):
    routes = Route.objects.all()
    return render(request, 'home.html', {'routes': routes})


def route_api(request):
    routes = Route.objects.all().values(
        'id', 'name', 'user__username',
        'activity_type__name', 'points', 'length'
    )
    return JsonResponse(list(routes), safe=False)
