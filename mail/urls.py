from django.urls import path, include
from rest_framework.routers import DefaultRouter

from mail import views

router = DefaultRouter()
router.register('user-email-history', views.UserEmailHistoryViewSet, basename='user_email_history')
router.register('contact-email-history', views.UserEmailHistoryViewSet, basename='contact_email_history')

app_name = 'mail'

urlpatterns = [
    path('', include(router.urls)),
]