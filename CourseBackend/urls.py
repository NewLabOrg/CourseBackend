from django.urls import path
from some import views

urlpatterns = [
    path('', views.index, name='hello'),
]
