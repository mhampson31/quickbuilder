from django.urls import path

from . import views

app_name = 'qb'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ship/<int:pk>/', views.ShipView.as_view(), name='ship_detail'),
    path('random/', views.random_quickbuild, name='random_quickbuild')
]

