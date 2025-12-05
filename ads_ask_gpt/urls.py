from __future__ import annotations

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import health_check, index, report

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("health", health_check, name="health"),
    path("report", report, name="report"),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=False)),
]

urlpatterns += staticfiles_urlpatterns()
