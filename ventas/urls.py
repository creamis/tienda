from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='ventas/login.html', redirect_authenticated_user=True), name='login'),
    path('home/', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('particular/', views.particular, name='particular'),
    path('empresa/', views.empresa, name='empresa'),
    path('particular/fibra-movil/', views.fibra_movil, name='fibra_movil'),
    path('particular/solo-movil/', views.solo_movil, name='solo_mov_url'),
    path('tienda/', views.tienda, name='tienda'),

]
