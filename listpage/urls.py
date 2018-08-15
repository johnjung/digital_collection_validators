from django.urls import path

from . import views

urlpatterns = [
	path('directoryreport', views.listpage, name='listpage'),
	path('errorreport', views.errpage, name = 'errpage'),
	path('', views.homepage, name = 'home'),
	path('<path:mvolfolder_name>', views.hierarch, name = "hierarch"),
]