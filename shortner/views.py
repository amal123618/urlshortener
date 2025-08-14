from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from .forms import ShortenForm
from .models import ShortURL

def index(request):
    short_url = None
    if request.method == "POST":
        form = ShortenForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]
            custom = form.cleaned_data["custom_code"].strip()
            with transaction.atomic():
                if custom:
                    if len(custom) > 8:
                        form.add_error("custom_code", "Max 8 characters.")
                    elif ShortURL.objects.filter(short_code=custom).exists():
                        form.add_error("custom_code", "That code is already taken.")
                    else:
                        obj = ShortURL.objects.create(original_url=url, short_code=custom)
                else:
                    obj = ShortURL.objects.create(original_url=url)

            if not form.errors:
                short_url = request.build_absolute_uri(
                    reverse("shortner:redirect", args=[obj.short_code])
                )
    else:
        form = ShortenForm()

    return render(request, "index.html", {"form": form, "short_url": short_url})

def redirect_code(request, code):
    try:
        obj = ShortURL.objects.get(short_code=code)
    except ShortURL.DoesNotExist:
        return HttpResponseNotFound("Short URL not found.")

    ShortURL.objects.filter(pk=obj.pk).update(
        clicks=F("clicks") + 1,
        last_accessed=timezone.now()
    )
    return redirect(obj.original_url)

def stats(request):
    items = ShortURL.objects.order_by("-created_at")[:50]
    base = request.build_absolute_uri("/")
    return render(request, "stats.html", {"items": items, "base": base})

def api_shorten(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    url = request.POST.get("url", "").strip()
    custom = request.POST.get("custom_code", "").strip() or None
    if not url:
        return HttpResponseBadRequest("Missing 'url'")
    if custom and len(custom) > 8:
        return HttpResponseBadRequest("custom_code too long (max 8)")
    if custom and ShortURL.objects.filter(short_code=custom).exists():
        return HttpResponseBadRequest("custom_code already taken")

    obj = ShortURL.objects.create(original_url=url, short_code=custom or ShortURL.generate_unique_code())
    short_url = request.build_absolute_uri(
        reverse("shortner:redirect", args=[obj.short_code])
    )
    return JsonResponse({"short_url": short_url, "code": obj.short_code})
