from django.conf.urls import url
from web import views

urlpatterns = [
    url(r'^server.html$', views.server),
    url(r'^server_json.html$', views.server_json),
]
