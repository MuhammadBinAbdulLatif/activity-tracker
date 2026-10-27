from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.SignInView.as_view(), name="login"),
    path("logout/", views.SignOutView.as_view(), name="logout"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
]
