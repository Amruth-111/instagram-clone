from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    # path('profile/<str:username>/', views.profile, name='profile'),
    # Add other URLs here as needed
    path('profile/', views.view_profile, name='profile'),
    # path('profile/1', views.display_user_posts, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', LogoutView.as_view(next_page='/login'), name='logout'),
    # path('users/<int:user_id>/', views.view_user, name='view_user'),
    path('users/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('search_users/', views.search_users, name='search_users'),
]
