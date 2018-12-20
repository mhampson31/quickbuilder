from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ship/<int:id>/', views.ship, name='ship')
]

