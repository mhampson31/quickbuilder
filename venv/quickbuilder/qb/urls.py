from django.urls import path

from . import views

app_name = 'qb'
urlpatterns = [
    path('', views.index, name='index'),
    path('ship/<int:id>/', views.ship, name='ship')
]

