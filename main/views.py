from django.contrib import messages
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, RouteEditForm
from .models import Route
import gpxpy
import gpxpy.gpx


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
        uploaded_files = request.FILES.getlist('files')
        success_count = 0
        skipped_count = 0

        for i, uploaded_file in enumerate(uploaded_files):
            points = []
            total_length = 0

            try:
                if uploaded_file.name.endswith('.gpx') or uploaded_file.name.endswith('.tcx'):
                    uploaded_file.seek(0)
                    gpx = gpxpy.parse(uploaded_file.read())
                    for track in gpx.tracks:
                        for segment in track.segments:
                            for point in segment.points:
                                points.append([point.latitude, point.longitude])
                    total_length = gpx.length_3d() / 1000

                else:
                    messages.add_message(request, messages.WARNING, f"Skipping file '{uploaded_file.name}': Unknown file type.")
                    skipped_count += 1
                    continue

                if not points:
                    messages.add_message(request, messages.WARNING, f"Skipping file '{uploaded_file.name}': No track points found after parsing.")
                    skipped_count += 1
                    continue
                
                route_name = request.POST.get(f'name_{i}')
                activity_type_id = request.POST.get(f'activity_type_{i}')

                if not route_name or not activity_type_id:
                    messages.add_message(request, messages.WARNING, f"Skipping file '{uploaded_file.name}': Form data (name or activity) was missing.")
                    skipped_count += 1
                    continue

                try:
                    activity_type = ActivityType.objects.get(pk=activity_type_id)
                except ActivityType.DoesNotExist:
                    messages.add_message(request, messages.WARNING, f"Skipping file '{uploaded_file.name}': Invalid activity type selected.")
                    skipped_count += 1
                    continue

                Route.objects.create(
                    user=request.user,
                    name=route_name,
                    activity_type=activity_type,
                    points=points,
                    length=total_length
                )
                success_count += 1

            except Exception as e:
                messages.add_message(request, messages.ERROR, f"An error occurred while processing '{uploaded_file.name}': {e}")
                skipped_count += 1
        
        if success_count > 0:
            messages.add_message(request, messages.SUCCESS, f"Successfully uploaded {success_count} route(s).")
        if skipped_count > 0:
            messages.add_message(request, messages.WARNING, f"Skipped {skipped_count} file(s). See other messages for details.")

        return redirect('home')
    else:
        activity_types = ActivityType.objects.all()
        return render(request, 'upload_route.html', {'activity_types': activity_types})


@login_required
def delete_route(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    if route.user != request.user:
        raise Http404
    route.delete()
    messages.add_message(request, messages.SUCCESS, f"Route '{route.name}' has been deleted.")
    return redirect('home')


@login_required
def edit_route(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    if route.user != request.user:
        raise Http404

    if request.method == 'POST':
        form = RouteEditForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"Route '{route.name}' has been updated.")
            return redirect('home')
    else:
        form = RouteEditForm(instance=route)

    return render(request, 'edit_route.html', {'form': form, 'route': route})


def home(request):
    routes = Route.objects.all()
    return render(request, 'home.html', {'routes': routes})


def route_api(request):
    routes = Route.objects.all().values(
        'id', 'name', 'user__username',
        'activity_type__name', 'points', 'length'
    )
    return JsonResponse(list(routes), safe=False)
