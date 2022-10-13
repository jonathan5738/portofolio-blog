from django.urls import path 
from . import views 

urlpatterns = [
    path('signin', views.RegisteUserView.as_view(), name="sign_user"),
    path('login', views.LoginUserView.as_view(), name='login_user'),
    path('edit', views.EditUserView.as_view(), name='edit_user'),
    path('delete', views.EditUserView.as_view(), name='delete_user'),
    path('reset', views.ResetPasswordView.as_view(), name='reset_password')
]