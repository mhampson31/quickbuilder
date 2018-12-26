from django.urls import path

from . import views

app_name = 'qb'
urlpatterns = [
    path(r'', views.IndexView.as_view(), name='index'),
    path(r'ship/<int:pk>/', views.ShipView.as_view(), name='ship_detail'),
    path(r'random/', views.random_quickbuild, name='random_quickbuild')
]

