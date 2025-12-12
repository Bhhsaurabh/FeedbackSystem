from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/login.html', next_page='reports:login'), name='logout'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('analysis/', views.feedback_analysis, name='feedback_analysis'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/<int:pk>/comment/', views.add_comment, name='add_comment'),
    # My Posts
    path('my-posts/', views.my_posts, name='my_posts'),
    path('my-posts/<int:pk>/edit/', views.edit_feedback, name='edit_feedback'),
    path('my-posts/<int:pk>/delete/', views.delete_own_feedback, name='delete_own_feedback'),
    # Admin custom dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/delete-feedback/<int:pk>/', views.delete_feedback, name='delete_feedback'),
    path('admin-dashboard/delete-comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('admin-dashboard/delete-feedback-bulk/', views.bulk_delete_feedback, name='bulk_delete_feedback'),
]
