from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import  RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
import django_filters
from django_filters import rest_framework as filters

from common.views import BaseViewSet
from utils.paginations import CustomLimitOffsetPagination
from user.models import Group
from user.permissions import ManagePermission, HostAllowedPermission
from .serializers import LoginSerializer, UserSerializer, ProfileUserSerializer, \
    ChangePasswordSerializer, \
    ForgotPasswordSerializer, VerifyForgotCodeSerializer, RegisterVerifySerializer, LoginOtpSerializer, \
    SendCodeLoginSerializer, SendCodePasswordCheckBCSerializer, UserFastSerializer, \
    SendCodeSerializer, LoginVerifySerializer, SendCodePasswordCheckAdminSerializer, CreateUserSerializer, \
    UpdateUserSerializer
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from django.contrib.auth import get_user_model
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
# send code mobile
# ---------------------------------------------------------------------------------------------------------------------
class SendCodeView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = SendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.success_response({})

# ---------------------------------------------------------------------------------------------------------------------
# register update information when verify
# ---------------------------------------------------------------------------------------------------------------------
class RegisterVerifyView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = RegisterVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return self.success_response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
# ---------------------------------------------------------------------------------------------------------------------
# register update information when verify
# ---------------------------------------------------------------------------------------------------------------------
class CreateUserView(BaseAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "ثبت نام با موفقیت انجام شد."}, status=status.HTTP_201_CREATED)


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"detail": "کاربر پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "اطلاعات با موفقیت به‌روزرسانی شد."}, status=status.HTTP_200_OK)
# ---------------------------------------------------------------------------------------------------------------------
# forget password
# ---------------------------------------------------------------------------------------------------------------------
class ForgotPasswordView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.success_response({})

class VerifyForgotCodeView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = VerifyForgotCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return self.success_response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
# ---------------------------------------------------------------------------------------------------------------------
# log-in with email/mobile -- user
# ---------------------------------------------------------------------------------------------------------------------
class SendCodeLoginView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = SendCodeLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.success_response({})

class loginOTPView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return self.success_response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

class LoginView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return self.success_response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

# ---------------------------------------------------------------------------------------------------------------------
# refresh-token
# ---------------------------------------------------------------------------------------------------------------------

class CustomTokenRefreshView(TokenRefreshView):
    pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: all user
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# -------------  change password user -------------#
class ProfileChangePasswordView(UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [IsAuthenticated,]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(request_body=ChangePasswordSerializer)

    def get_queryset(self):
        return User.objects.filter(email=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.validated_data["password"])
        self.request.user.save()

        return Response({}, status=status.HTTP_200_OK)

# -------------  profile user ---------------#
class ProfileView(RetrieveUpdateAPIView):

    http_method_names = ['get', 'patch']
    permission_classes = [IsAuthenticated,]
    serializer_class = ProfileUserSerializer
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(request_body=ProfileUserSerializer)
    def get_queryset(self):
        return User.objects.filter(email=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user

#---------all/admin------------------------
class UserFilter(filters.FilterSet):
    role = django_filters.BaseInFilter(field_name='role', lookup_expr='in')

    class Meta:
        model = User
        fields = ['role']

class UserViewSet(BaseViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CustomLimitOffsetPagination
    filter_backends = ( OrderingFilter, SearchFilter,DjangoFilterBackend)
    filterset_class = UserFilter
    ordering_fields = ('_created_at', '_updated_at')
    search_fields = ('email', 'first_name', 'last_name','mobile')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: admin
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SendCodePasswordBCView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = SendCodePasswordCheckBCSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.success_response({})

#-----------------ADMIN----------------------
class SendCodePasswordAdminView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = SendCodePasswordCheckAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.success_response({})


class LoginVerifyView(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return self.success_response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
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
# CLASS: chatbot API
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserAPIViewSet(RetrieveAPIView):
    permission_classes = [IsAuthenticated,HostAllowedPermission]
    serializer_class = UserFastSerializer
    queryset = User.objects.all()
    pagination_class = CustomLimitOffsetPagination
    lookup_field = 'id'