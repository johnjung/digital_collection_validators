from django.urls import path

from . import views

urlpatterns = [
    path('errorreport/', views.errpage, name='errpage'),
    path('mvolreport/', views.prelistpage, name='prelistpage'),
    path('mvolreport/<status>/', views.listpage, name='listpage'),
    path('', views.homepage, name='home'),
    path('<path:mvolfolder_name>/', views.hierarch, name="hierarch"),
]
