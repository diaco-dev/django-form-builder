from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views


router = DefaultRouter()
router.register('admin/users', views.UserViewSet, basename='user')



app_name = 'user'

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterVerifyView.as_view(), name='register'),
    path('admin/create-user/', views.CreateUserView.as_view(), name='add_user'),
    path('admin/update-user/<uuid:id>/', views.UpdateUserView.as_view(), name='update_user'),
    path('send-code/', views.SendCodeView.as_view(), name='send_code_step2'),
    path('send-code-login/', views.SendCodeLoginView.as_view(), name='send_code_step1'),
    path('login-otp/', views.loginOTPView.as_view(), name='log_in_otp'),
    path('login/', views.LoginView.as_view(), name='log_in'),
    path('profile/', views.ProfileView.as_view(), name='auth_update_profile'),
    path('change_password/', views.ProfileChangePasswordView.as_view(), name='auth_change_password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-forgot-code/', views.VerifyForgotCodeView.as_view(), name='verify_forgot_code'),

    # ----------------------------bc/admin-------------------------------#
    path('admin/check-password/', views.SendCodePasswordAdminView.as_view(), name='check_password_send_code_admin'),
    path('admin/verify-login/', views.LoginVerifyView.as_view(), name='verify_login_otp_admin'),

]
