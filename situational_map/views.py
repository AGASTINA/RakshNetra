from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from PIL import Image
import io

from events.models import Event
from situational_map.models import MapLayout, MapObject


@login_required(login_url='login')
@ensure_csrf_cookie
def situational_map_page(request):
    """Dedicated situational map editor page with AI auto-draw."""
    return render(request, 'situational_map.html')


@login_required(login_url='login')
def map_management(request):
    """Manage situational map layouts and objects."""
    if request.method == "POST":
        action = request.POST.get("action", "").strip().lower()

        if action == "upload_layout":
            event_id = request.POST.get("event")
            image = request.FILES.get("image")
            width_meters = request.POST.get("width_meters") or 0
            height_meters = request.POST.get("height_meters") or 0

            if not event_id or not image:
                messages.error(request, "Event and image are required")
                return redirect("map_management")

            event = get_object_or_404(Event, id=event_id)

            try:
                width_meters = float(width_meters) if width_meters else 0.0
                height_meters = float(height_meters) if height_meters else 0.0
            except ValueError:
                width_meters = 0.0
                height_meters = 0.0

            image_obj = Image.open(image)
            width_pixels, height_pixels = image_obj.size

            layout = MapLayout.objects.filter(event=event).first()
            if layout:
                layout.image = image
                layout.width_pixels = width_pixels
                layout.height_pixels = height_pixels
                layout.width_meters = width_meters or layout.width_meters
                layout.height_meters = height_meters or layout.height_meters
                layout.save()
                messages.success(request, "Map layout updated successfully")
                return redirect(f"/manage/map/?layout={layout.id}")

            layout = MapLayout.objects.create(
                event=event,
                image=image,
                width_pixels=width_pixels,
                height_pixels=height_pixels,
                width_meters=width_meters or 1.0,
                height_meters=height_meters or 1.0,
            )
            messages.success(request, "Map layout uploaded successfully")
            return redirect(f"/manage/map/?layout={layout.id}")

        if action == "add_object":
            layout_id = request.POST.get("layout_id")
            obj_type = request.POST.get("obj_type")
            label = request.POST.get("label", "").strip()
            x = request.POST.get("x")
            y = request.POST.get("y")

            if not layout_id or not obj_type or x is None or y is None:
                messages.error(request, "Layout, type, X and Y are required")
                return redirect("map_management")

            try:
                x = float(x)
                y = float(y)
            except ValueError:
                messages.error(request, "X and Y must be numbers")
                return redirect("map_management")

            layout = get_object_or_404(MapLayout, id=layout_id)
            MapObject.objects.create(
                map_layout=layout,
                obj_type=obj_type,
                x=x,
                y=y,
                label=label,
            )
            messages.success(request, "Map object added successfully")
            return redirect(f"/manage/map/?layout={layout.id}")

        if action == "seed_demo":
            event = Event.objects.order_by("-start_time").first()
            if event is None:
                now = timezone.now()
                event = Event.objects.create(
                    name="Demo Event",
                    start_time=now,
                    end_time=now + timezone.timedelta(hours=8),
                    location="Demo Site",
                    created_by=request.user,
                )

            layout = MapLayout.objects.filter(event=event).first()
            if layout is None:
                img = Image.new("RGB", (1200, 800), color=(12, 18, 36))
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                image_file = ContentFile(buffer.getvalue(), name="demo_map.png")
                layout = MapLayout.objects.create(
                    event=event,
                    image=image_file,
                    width_pixels=1200,
                    height_pixels=800,
                    width_meters=60.0,
                    height_meters=40.0,
                )

            demo_objects = [
                (MapObject.TYPE_CAMERA, 10, 10, "Gate Camera"),
                (MapObject.TYPE_ENTRY, 5, 20, "Main Entry"),
                (MapObject.TYPE_EXIT, 55, 35, "Exit"),
                (MapObject.TYPE_VIP, 30, 20, "VIP Stage"),
                (MapObject.TYPE_POLICE, 20, 30, "Police Unit"),
            ]
            for obj_type, x, y, label in demo_objects:
                MapObject.objects.create(
                    map_layout=layout,
                    obj_type=obj_type,
                    x=x,
                    y=y,
                    label=label,
                )

            messages.success(request, "Demo layout and objects created")
            return redirect(f"/manage/map/?layout={layout.id}")

    events = Event.objects.all().order_by("-start_time")
    layouts = MapLayout.objects.select_related("event").all()
    selected_layout_id = request.GET.get("layout")
    selected_layout = None
    map_objects = []
    if selected_layout_id:
        selected_layout = MapLayout.objects.filter(id=selected_layout_id).first()
        if selected_layout:
            map_objects = MapObject.objects.filter(map_layout=selected_layout).order_by("obj_type")

    return render(request, "management/map.html", {
        "events": events,
        "layouts": layouts,
        "selected_layout": selected_layout,
        "map_objects": map_objects,
        "object_types": MapObject.TYPE_CHOICES,
    })
