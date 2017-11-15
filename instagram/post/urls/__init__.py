from django.conf.urls import url, include
from . import views, apis

urlpatterns = [
    url(r'^', include(views)),
    url(r'^', include(apis)),
]