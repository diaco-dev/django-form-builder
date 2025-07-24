from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.serializers import CustomSerializer
from core.types import UserType
from history.models import UserEmailHistory

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('password', 're_password', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        if 're_password' in validated_data:
            validated_data.pop('re_password')

        validated_data['email'] = validated_data['email'].lower()

        # user = User.objects.create(
        #     email=str(validated_data['email']).lower()
        # )
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    re_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 're_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

    # def validate_username(self, value):
    #     user = self.context['request'].user
    #     if User.objects.exclude(pk=user.pk).filter(username=value).exists():
    #         raise serializers.ValidationError({"username": "This username is already in use."})
    # #     return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


# -----------------------------------------------------------------------------------------
class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        try:
            password_validation.validate_password(attrs["password"], user)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return super().validate(attrs)


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            raise serializers.ValidationError({"current_password": 'Current password is invalid.'})


class PasswordRetypeSerializer(PasswordSerializer):
    re_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["password"] == attrs["re_password"]:
            return attrs
        else:
            raise serializers.ValidationError({"password": "password and re-type password doesn't match."})


class PasswordUserSerializer(serializers.Serializer):
    user = serializers.UUIDField()

    def validate_user(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError({"user": "User not found."})
        return value


class SetPasswordSerializer(PasswordRetypeSerializer, PasswordSerializer, PasswordUserSerializer):
    pass


class ChangePasswordSerializer(PasswordRetypeSerializer, PasswordSerializer, CurrentPasswordSerializer):
    pass


class ProfileChangePasswordSerializer(PasswordRetypeSerializer, PasswordSerializer, CurrentPasswordSerializer):
    pass


class RegisterSerializer(PasswordRetypeSerializer, PasswordSerializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email": "Email is already taken."})
        return value


class ActiveBanUserSerializer(serializers.Serializer):
    user = serializers.UUIDField()
    status = serializers.BooleanField()

    def validate_user(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError({"user": "User not found."})
        return value


class SendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError({"email": "Email not registered."})
        if user.is_banned:
            raise serializers.ValidationError({"email": "User is banned."})
        if user.email_verified:
            raise serializers.ValidationError({"email": "User is already verified."})
        return value


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.IntegerField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError({"email": "Email not registered."})
        if user.is_banned:
            raise serializers.ValidationError({"email": "User is banned."})
        if user.mobile_verified:
            raise serializers.ValidationError({"email": "User is already verified."})
        return value

    def validate_token(self, value):
        email = self.context['request'].data['email']
        user = User.objects.filter(email=email).first()
        if user.verify_email_token_expire_at < timezone.now():
            raise serializers.ValidationError("Timeout.")
        if user.verify_email_token != value:
            raise serializers.ValidationError("Invalid token.")
        return value


class ChangeAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True)

    def validate_avatar(self, image):
        if image.size > settings.MAX_AVATAR_FILE_SIZE:
            print(image.size)
            raise ValidationError("File size too big!")
        return image

    class Meta:
        model = get_user_model()
        fields = ('avatar',)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Email not registered.")
        if user.is_banned:
            raise serializers.ValidationError("User is banned.")
        if not user.email_verified:
            raise serializers.ValidationError("User is not active.")
        return value


class ResetPasswordConfirmSerializer(PasswordRetypeSerializer, PasswordSerializer, serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.IntegerField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Email not registered.")
        if user.is_banned:
            raise serializers.ValidationError("User is banned.")
        if not user.email_verified:
            raise serializers.ValidationError("User is not active.")
        return value

    def validate_token(self, value):
        email = self.context['request'].data['email']
        user = User.objects.filter(email=email).first()
        if user.verify_email_token_expire_at < timezone.now():
            raise serializers.ValidationError("Timeout.")
        if user.verify_email_token != value:
            raise serializers.ValidationError("Invalid token.")
        return value


# -----------------------------------------------------------------------------------------


class ListUserSerializer(serializers.ModelSerializer):
    # user_type_list = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'user_type', 'is_active', 'can_delete', 'mobile',
                  'avatar', 'created_by', 'updated_by', 'created_at', 'updated_at',
                  'email_verified', 'mobile_verified', 'two_step_auth')  # 'user_type_list',
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # def get_user_type_list(self, user):
    #     types = []
    #     for t in UserType.choices:
    #         if user.user_type == UserType.MANAGER:
    #             continue
    #         types.append(t)
    #     return types


class RetrieveUserSerializer(serializers.ModelSerializer):
    # user_type_list = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'full_name', 'first_name', 'last_name', 'email', 'email_verified', 'user_type', 'is_active',
                  'can_delete', 'mobile', 'mobile_verified', 'is_staff', 'joined_at', 'logout_at', 'login_at',
                  'is_banned', 'can_delete', 'notify_after_login', 'two_step_auth', 'avatar',
                  'created_by', 'updated_by', 'created_at', 'updated_at'
                  )  # 'user_type_list',

    # def get_user_type_list(self, user):
    #     types = []
    #     for t in UserType.choices:
    #         if user.user_type == UserType.MANAGER:
    #             continue
    #         types.append(t)
    #     return types


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'user_type', 'is_active', 'mobile')
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class UserSerializer(serializers.ModelSerializer):
    # user_type_list = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
        'id', 'full_name', 'first_name', 'last_name', 'email', 'user_type', 'is_active', 'can_delete', 'mobile',
        'avatar', 'created_by', 'updated_by', 'created_at', 'updated_at'
        )  # 'user_type_list',
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class CurrentUserSerializer(serializers.ModelSerializer):
    # user_type_list = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
        'id', 'full_name', 'first_name', 'last_name', 'email', 'user_type', 'is_active', 'can_delete', 'mobile',
        'avatar', 'created_by', 'updated_by', 'created_at', 'updated_at'
        )  # 'user_type_list',
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SERIALIZER: UserEmailSerializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ProfileEmailHistorySerializer(CustomSerializer):
    class Meta:
        model = UserEmailHistory
        fields = ('id', 'subject', 'body', 'created_at')


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'full_name', 'first_name', 'last_name', 'email', 'user_type', 'avatar', 'two_step_auth',
                  'notify_after_login')
        read_only_fields = ('id', 'email', 'full_name', 'user_type', 'avatar')


class UpdateUserSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'mobile', 'avatar')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
