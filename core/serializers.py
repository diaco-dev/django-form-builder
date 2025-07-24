
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings



# ---------------------------------------------------------------------------------------------------------------------
# refresh token
# ---------------------------------------------------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        token['exp_time'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        return token

