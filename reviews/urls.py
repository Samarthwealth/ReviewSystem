from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('submit/', views.submit_review, name='submit_self_review'),
    path('submit-manager-review/<int:reviewee_id>/', views.submit_review, name='submit_manager_review'),
    path('submit-manager-feedback/', views.submit_manager_feedback, name='submit_manager_feedback'),
    path('submit-final/<int:reviewee_id>/', views.submit_final_review, name='submit_final_review'),
    path('view-review/<int:review_id>/', views.view_review, name='view_review'),
]
