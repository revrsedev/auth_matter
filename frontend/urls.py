from django.urls import path
from .views import chat_view, home, login_view, profile, register_with_anope, logout_view
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('profile/', profile, name='profile'),
    path('register_with_anope/', register_with_anope, name='register_with_anope'),
    path('chat/', chat_view, name='chat'),
    path('logout/', logout_view, name='logout'),
    path('kiwiirc_config/', views.kiwiirc_config, name='kiwiirc_config'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

