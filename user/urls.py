from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from core.views import LogoutAPIView, CustomTokenObtainPairView
from user import views

router = DefaultRouter()
router.register('user', views.UserViewSet, basename='user')

app_name = 'user'

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('accounts/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('accounts/logout/', LogoutAPIView.as_view(), name='logout'),
]

urlpatterns += [
    # path('accounts/profile/', views.RetrieveUserView.as_view(), name='profile'),
    # path('accounts/profile/update/<uuid:pk>/', views.UpdateProfileView.as_view(), name='auth_update_profile'),
    path('accounts/profile/', views.ProfileView.as_view(), name='auth_update_profile'),
    path('accounts/emails-history/', views.ProfileEmailHistoryView.as_view(), name='auth_update_profile'),
    path('accounts/change_password/', views.ProfileChangePasswordView.as_view(), name='auth_change_password'),
    path('accounts/change_avatar/', views.ProfileChangeAvatarView.as_view(), name='auth_change_avatar'),
]
