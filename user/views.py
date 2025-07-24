from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.paginations import CustomLimitOffsetPagination
from core.permissions import IsManager, IsManagerOrAbove, CurrentUserOrManager, IsOwner, IsSystemManager, \
    IsOfficeEmployee, IsSystemManagerOrIsManagerOrOfficeEmployee
from core.types import UserType
from core.utils import encode_uid
from history.generics import HistoryViewSet
from history.mixins import ActivityLogMixin
from mail.generics import BaseEmailMessage
from core import signals
from history.models import UserEmailHistory
from user.notifications import ConfirmationEmail, PasswordResetEmail, ManagerSetPasswrdNotifyEmail, UserBanNotifyEmail
from user.serializers import UpdateUserSerializer, UserSerializer, CreateUserSerializer, ListUserSerializer, \
    RetrieveUserSerializer, SetPasswordSerializer, ChangePasswordSerializer, ActivationSerializer, \
    SendActivationSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer, RegisterSerializer, \
    ActiveBanUserSerializer, CurrentUserSerializer, ProfileUserSerializer, ChangeAvatarSerializer, \
    ProfileEmailHistorySerializer
from user.utils import logout_user

User = get_user_model()


# ACTIVATION_URL = '/users/reset_password/'
# PASSWORD_RESET_CONFIRM_URL = '/users/reset_password_confirm/'


class UserViewSet(ModelViewSet):
    # permission_classes = (IsManagerOrAbove,)
    # serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (IsSystemManagerOrIsManagerOrOfficeEmployee,)
        elif self.action == "change_password":
            self.permission_classes = (IsAuthenticated,)
        elif self.action == "set_password":
            self.permission_classes = (CurrentUserOrManager,)
        elif self.action == "active_user":
            self.permission_classes = (IsManagerOrAbove,)
        elif self.action == "ban_user":
            self.permission_classes = (IsManagerOrAbove,)
        elif self.action == "send_activation":
            self.permission_classes = (AllowAny,)
        elif self.action == "activation":
            self.permission_classes = (AllowAny,)
        elif self.action == "reset_password":
            self.permission_classes = (AllowAny,)
        elif self.action == "reset_password_confirm":
            self.permission_classes = (AllowAny,)
        elif self.action == "register":
            self.permission_classes = (AllowAny,)

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        elif self.action == 'list':
            return ListUserSerializer
        elif self.action == 'retrieve':
            return RetrieveUserSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer  # ToDo: incorrect !!!!!
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'active_user':
            return ActiveBanUserSerializer
        elif self.action == 'ban_user':
            return ActiveBanUserSerializer
        elif self.action == 'send_activation':
            return SendActivationSerializer
        elif self.action == 'activation':
            return ActivationSerializer
        elif self.action == 'reset_password':
            return ResetPasswordSerializer
        elif self.action == 'reset_password_confirm':
            return ResetPasswordConfirmSerializer
        elif self.action == 'register':
            return RegisterSerializer
        return UserSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.action == 'change_password':
                return User.objects.filter(id=self.request.user.id)
            # if self.request.user.user_type == UserType.MANAGER:
            #     return User.objects.filter(user_type=UserType.CUSTOMER, deletable=True)
            return User.objects.filter(deletable=True)
        return []

    def retrieve(self, request, *args, **kwargs):
        # if not self.request.user.is_authenticated:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        # if self.request.user.user_type > UserType.MANAGER:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_type = request.data.get('user_type', UserType.UNDEFINED)

        if self.request.user.user_type == UserType.SYSTEM_MANAGER:
            pass
        if self.request.user.user_type == UserType.MANAGER:
            if user_type == UserType.SYSTEM_MANAGER:
                raise ValidationError({"detail": "You do not have permission to perform this action."})
        elif self.request.user.user_type == UserType.OFFICE_EMPLOYEE:
            if user_type != UserType.CUSTOMER:
                raise ValidationError({"detail": "You do not have permission to perform this action."})
        else:
            raise ValidationError({"detail": "You do not have permission to perform this action."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        password = get_random_string(8)
        user.set_password(password)
        user.save()
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # response.data['password'] = password
        return response

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )
        return user

        # context = {"user": user}
        # to = [user.email]
        # if settings.SEND_ACTIVATION_EMAIL:
        #     settings.EMAIL.activation(self.request, context).send(to)
        # elif settings.SEND_CONFIRMATION_EMAIL:
        #     settings.EMAIL.confirmation(self.request, context).send(to)

    def perform_update(self, serializer, *args, **kwargs):
        user_to_update = self.get_object()

        if self.request.user.user_type not in (UserType.SYSTEM_MANAGER, UserType.MANAGER, UserType.OFFICE_EMPLOYEE):
            raise ValidationError({"detail", "You do not have permission to perform this action."})
        if self.request.user.user_type == UserType.OFFICE_EMPLOYEE:
            if user_to_update._created_by != self.request.user:
                raise ValidationError({"detail": "You do not have permission to perform this action."})
        super().perform_update(serializer)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # should we send activation email after update?
        # if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
        #     context = {"user": user}
        #     to = [user.email]
        #     settings.EMAIL.activation(self.request, context).send(to)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            logout_user(self.request)
        self.perform_destroy(instance)
        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=request.data.get('user'))
        user.set_password(serializer.validated_data["password"])
        user.save()

        if settings.MANAGER_PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {
                "user": self.request.user,
                "password": serializer.validated_data["password"]
            }
            to = [user.email]
            ManagerSetPasswrdNotifyEmail(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            user.logout()

        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user

        user.set_password(serializer.validate_data["password"])
        user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [user.email]
            ManagerSetPasswrdNotifyEmail(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            user.logout()

        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def active_user(self, request, *args, **kwargs):
        user_type = request.data.get('user_type', UserType.UNDEFINED)
        if self.request.user.user_type > UserType.MANAGER:
            raise PermissionError('only system manager perform this action.')
        if self.request.user.user_type == UserType.MANAGER:
            if user_type != UserType.CUSTOMER:
                raise PermissionError('manager can only set customer activation.')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=request.data.get('user'))
        user.is_active = serializer.data["status"]
        user.save()

        # if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
        #     context = {"user": self.request.user}
        #     to = [get_user_email(self.request.user)]
        #     settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        #
        # if settings.LOGOUT_ON_PASSWORD_CHANGE:
        #     utils.logout_user(self.request)
        # elif settings.CREATE_SESSION_ON_LOGIN:
        #     update_session_auth_hash(self.request, self.request.user)
        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def ban_user(self, request, *args, **kwargs):
        user_type = request.data.get('user_type', UserType.UNDEFINED)
        if self.request.user.user_type > UserType.MANAGER:
            raise PermissionError('only system manager perform this action.')
        if self.request.user.user_type == UserType.MANAGER:
            if user_type != UserType.CUSTOMER:
                raise PermissionError('manager can only set customer activation.')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=request.data.get('user'))
        is_banned = serializer.validated_data["status"]
        if is_banned != user.is_banned:
            user.is_banned = is_banned

            user.save()

            if settings.USER_BANNED_EMAIL_CONFIRMATION:
                context = {
                    "user": user,
                    "status": is_banned
                }
                to = [user.email]
                UserBanNotifyEmail(self.request, context).send(to)
        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def send_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data.get('email'))

        if user:
            user.generate_activation_token()
            context = {"user": user}
            to = [user.email]
            ConfirmationEmail(self.request, context).send(to)

        response = Response({}, status=status.HTTP_200_OK)
        response.data['timeout'] = settings.EMAIL_TOKEN_EXPIRE
        if settings.DEBUG:
            response.data['code'] = user.verify_email_token
        return response


    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.data.get('email'))
        user.is_active = True
        user.email_verified = True
        user.verify_email_token = 0
        user.verify_email_token_expire_at = timezone.now()
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [user.email]
            ConfirmationEmail(self.request, context).send(to)

        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data.get('email'))

        if user:
            user.generate_activation_token()
            context = {"user": user}
            to = [user.email]
            ConfirmationEmail(self.request, context).send(to)

        response = Response({}, status=status.HTTP_200_OK)
        response.data['timeout'] = settings.EMAIL_TOKEN_EXPIRE
        if settings.DEBUG:
            response.data['code'] = user.verify_email_token
        return response

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.data.get('email'))
        user.set_password(serializer.validated_data.get("password"))
        user.verify_email_token = 0
        user.verify_email_token_expire_at = timezone.now()
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [user.email]
            ConfirmationEmail(self.request, context).send(to)

        return Response({}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = request.data.pop('password')
        request.data.pop('re_password')
        user = User.objects.create(user_type=UserType.CUSTOMER, **request.data)
        user.set_password(password)
        user.user_type = UserType.CUSTOMER
        # user.is_active = False
        user.save()

        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        response.data['id'] = str(user.id)
        return response

    @action(["get, post"], detail=False)
    def logout(self, request, *args, **kwargs):
        logout_user(self.request)


# class RetrieveUserView(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         user = CurrentUserSerializer(user)
#
#         return Response(user.data, status=status.HTTP_200_OK)


class ProfileEmailHistoryView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileEmailHistorySerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return UserEmailHistory.objects.filter(user_id=self.request.user.id)

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(RetrieveUpdateAPIView):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileUserSerializer

    def get_queryset(self):
        return User.objects.filter(email=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user


class ValidateTokenForFastapi(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileUserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ProfileChangePasswordView(UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_queryset(self):
        return User.objects.filter(email=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.validated_data["password"])
        self.request.user.save()

        # ToDo: Send notification Email to user
        return Response({}, status=status.HTTP_200_OK)


class ProfileChangeAvatarView(UpdateAPIView):
    parser_classes = (FormParser, MultiPartParser)
    http_method_names = ('patch',)
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeAvatarSerializer

    def get_queryset(self):
        return User.objects.filter(email=self.request.user)

    def get_object(self, queryset=None):
        return self.request.user
