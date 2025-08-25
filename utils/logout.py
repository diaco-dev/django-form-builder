import rest_framework
from django.conf import settings
from django.contrib.auth import login, logout, user_logged_in, user_logged_out

def logout_user(request):
    rest_framework.authtoken.models.Token.objects.filter(user=request.user).delete()
    user_logged_out.send(
        sender=request.user.__class__, request=request, user=request.user
    )
    if settings.CREATE_SESSION_ON_LOGIN:
        logout(request)