from django.urls import path
from . import views
from users import views as user_views
# from users.views import view_profile



urlpatterns = [
    path('posts/add-posts/', views.add_post, name='add-posts'),
    path('posts/<int:post_id>/', views.view_post_detail, name='view_post_detail'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('profile/', user_views.view_profile, name='user_profile'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    
    #comments
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('comments/<int:comment_id>/replies/', views.get_replies, name='get_replies'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

]



