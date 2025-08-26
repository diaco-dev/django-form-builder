from rest_framework_simplejwt.tokens import  RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import user_logged_out, user_logged_in, get_user_model

User = get_user_model()

# -----------------------------------------------------------------------------------

class BaseAPIView(APIView):
    def success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
        data = data or {}
        return Response(data, status=status_code)

class BaseModelViewSet(ModelViewSet):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            status=status.HTTP_204_NO_CONTENT)

# ---------------------------------------------------------------------------------------------------------------------
# refresh-token
# ---------------------------------------------------------------------------------------------------------------------

class CustomTokenRefreshView(TokenRefreshView):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS: LogoutAPIView
#
# Logout user and add current token to blacklist and send logout signal.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS: CustomTokenObtainPairView
#
# Takes a set of user credentials and returns an access and refresh JSON web token pair to prove the authentication
# of those credentials. Also perform login and send login signal.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            payload = jwt.decode(response.data.get('access'), settings.SIMPLE_JWT['VERIFYING_KEY'],
                                 algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user = User.objects.get(id=payload.get('user_id'))

            if not user.email_verified:
                return Response({"detail": "not verified"}, status=status.HTTP_403_FORBIDDEN)

            user.login()
            user_logged_in.send(sender=user.__class__, request=request, user=user)

        return response
