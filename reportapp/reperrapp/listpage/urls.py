from django.urls import path

from . import views

urlpatterns = [
	path('', views.main, name='main'),
	path('<path:mvolfolder_name>', views.hierarch, name = "hierarch")
]