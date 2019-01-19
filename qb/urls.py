from django.urls import path

from . import views

app_name = 'qb'
urlpatterns = [
    path(r'', views.IndexView.as_view(), name='index'),
    path(r'ship/<int:pk>/', views.ShipView.as_view(), name='ship_detail'),
    path(r'random/', views.random_quickbuild, name='random_quickbuild'),
    path(r'quicklist/<str:qb_list>/', views.quickbuild_list, name='quickbuild_list'),
    path(r'quickbuilds/<str:faction>/', views.faction_builds, name='faction_builds'),
    path(r'qb/<int:qb_id>/', views.qb_detail, name='qb_detail')
]

