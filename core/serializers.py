from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import CustomUser, Industry, MobileList
from core.tasks import send_verification_sms
import random
import string
from django_redis import get_redis_connection
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
import logging
from django.db import transaction
from notifications.handlers import queue_login_notification
from user.models import UserDetails, Unit, Group

logger = logging.getLogger(__name__)
User = get_user_model()


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


# ---------------------------------------------------------------------------------------------------------------------
# register / verify=ture
# ---------------------------------------------------------------------------------------------------------------------

class RegisterVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    email = serializers.EmailField(max_length=100, required=False, allow_blank=True)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    gender = serializers.ChoiceField(choices=User.GENDER, required=False)

    def validate(self, data):
        mobile = data.get('mobile', '')
        code = data.get('code', '')
        password = data.get('password', '')
        re_password = data.get('re_password', '')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"mobile": "فرمت شماره موبایل نادرست است."})

        if password != re_password:
            raise serializers.ValidationError({"re_password": "رمز عبور مطابقت ندارد."})

        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError({"mobile": "این شماره قبلاً ثبت شده است."})

        redis_conn = get_redis_connection("default")
        stored_code = redis_conn.get(f"verification_code:{mobile}")
        if not stored_code:
            raise serializers.ValidationError({"code": "کد تأیید یافت نشد."})
        if stored_code.decode('utf-8') != code:
            raise serializers.ValidationError({"code": "کد تأیید اشتباه است."})

        return data

    def save(self):
        data = self.validated_data

        with transaction.atomic():
            user = User.objects.create_user(
                mobile=data['mobile'],
                email=data.get('email', ''),
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                gender=data.get('gender', ''),
                is_verified=True,
                is_active=False,
            )
            if not user.is_active:
                if MobileList.objects.filter(mobile=user.mobile, is_active=True).exists():
                    user.is_active = True
                    user.save()
                else:
                    raise serializers.ValidationError({
                        "error": "حساب کاربری غیرفعال است و شماره موبایل در لیست نیست لطفا با پشتیبانی تماس بگیرید."
                    })
            redis_conn = get_redis_connection("default")
            redis_conn.delete(f"verification_code:{data['mobile']}")

        queue_login_notification(user)

        return user

# ---------------------------------------------------------------------------------------------------------------------
# register / BC
# ---------------------------------------------------------------------------------------------------------------------
class CreateUserSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES,required=True)

    def validate(self, data):
        mobile = data.get('mobile', '')
        password = data.get('password', '')
        re_password = data.get('re_password', '')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"mobile": "فرمت شماره موبایل نادرست است."})

        if password != re_password:
            raise serializers.ValidationError({"re_password": "رمز عبور مطابقت ندارد."})

        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError({"mobile": "این شماره قبلاً ثبت شده است."})

        return data

    def save(self):
        data = self.validated_data

        with transaction.atomic():
            user = User.objects.create_user(
                mobile=data['mobile'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                role=data['role'],
                is_verified=True,
                is_active=True,
            )
        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    re_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['mobile', 'first_name', 'last_name', 'role', 'password', 're_password']
        extra_kwargs = {
            'mobile': {'required': False},
            'role': {'required': False},
        }

    def validate(self, data):
        password = data.get('password')
        re_password = data.get('re_password')

        if password or re_password:
            if password != re_password:
                raise serializers.ValidationError({"re_password": "رمز عبور مطابقت ندارد."})

        return data

    def update(self, instance, validated_data):
        # Update simple fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.role = validated_data.get('role', instance.role)

        # Handle password
        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.save()
        return instance
# ---------------------------------------------------------------------------------------------------------------------
# forget password
# ---------------------------------------------------------------------------------------------------------------------
# - 1 ------send code
class ForgotPasswordSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=100)

    def validate(self, data):
        mobile = data['mobile']

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError("فرمت شماره موبایل نادرست است")
        user = User.objects.filter(mobile=mobile).first()
        if not user:
            raise serializers.ValidationError("کاربری با این شماره موبایل ساخته نشده .")

        verification_code = ''.join(random.choices(string.digits, k=6))

        redis_conn = get_redis_connection("default")
        redis_conn.setex(f"forgot_code:{mobile}", 120, verification_code)

        send_verification_sms.delay(mobile, verification_code)

        return data


# - 2--------verify code
class VerifyForgotCodeSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    def validate(self, data):
        mobile = data['mobile']
        code = data['code']
        password = data['password']
        re_password = data['re_password']

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است."})

        if password != re_password:
            raise serializers.ValidationError({"رمز عبور مطابقت ندارد."})

        user = User.objects.filter(mobile=mobile).first()
        if not user:
            raise serializers.ValidationError({"فرمت شماره موبایل نادرست است."})

        redis_conn = get_redis_connection("default")
        stored_code = redis_conn.get(f"forgot_code:{mobile}")

        if not stored_code or stored_code.decode('utf-8') != code:
            raise serializers.ValidationError({"error": "کد تایید نا معتبر است یا متقضی شده است "})

        data['user'] = user
        return data

    def save(self):
        mobile = self.validated_data['mobile']
        password = self.validated_data['password']
        user = User.objects.get(mobile=mobile)
        user.set_password(password)
        user.save()
        redis_conn = get_redis_connection("default")
        redis_conn.delete(f"forgot_code:{mobile}")
        return user

# ---------------------------------------------------------------------------------------------------------------------
# send code mobile redis register
# ---------------------------------------------------------------------------------------------------------------------
class SendCodeSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)


    def validate(self, data):
        mobile = data.get('mobile')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است"})

        try:
            verification_code = ''.join(random.choices(string.digits, k=6))
            redis_conn = get_redis_connection("default")
            redis_conn.setex(f"verification_code:{mobile}", 120, verification_code)
            logger.info(f"OTP {verification_code} stored for mobile {mobile}")

            send_verification_sms.delay(mobile, verification_code)
            logger.info(f"OTP send task triggered for mobile {mobile}")
        except Exception as e:
            logger.error(f"Error sending OTP for mobile {mobile}: {str(e)}")
            raise serializers.ValidationError({"error": f"ارسال کد تأیید ناموفق بود: {str(e)}"})

        return data


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: log-in user
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SendCodeLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate(self, data):
        mobile = data.get('mobile')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است"})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "کاربری با این شماره موبایل یافت نشد."})

        if user.role not in ['admin', 'user', 'superuser']:
            raise serializers.ValidationError({"error": "دسترسی برای کاربران بیزینس کوچ مجاز نیست."})

        try:
            verification_code = ''.join(random.choices(string.digits, k=6))
            redis_conn = get_redis_connection("default")
            redis_conn.setex(f"verification_code:{mobile}", 120, verification_code)
            logger.info(f"OTP {verification_code} stored for mobile {mobile}")

            send_verification_sms.delay(mobile, verification_code)
            logger.info(f"OTP send task triggered for mobile {mobile}")
        except Exception as e:
            logger.error(f"Error sending OTP for mobile {mobile}: {str(e)}")
            raise serializers.ValidationError({"error": f"ارسال کد تأیید ناموفق بود: {str(e)}"})

        return data


class LoginOtpSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        mobile = data.get('mobile')
        code = data.get('code')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است"})

        redis_conn = get_redis_connection("default")
        stored_code = redis_conn.get(f"verification_code:{mobile}")

        if not stored_code or stored_code.decode() != code:
            raise serializers.ValidationError({"error": "کد تایید نا معتبر است یا متقضی شده است "})

        redis_conn.delete(f"verification_code:{mobile}")

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=mobile,
                password=None
            )

        if not user.is_verified:
            raise serializers.ValidationError({"error": "حساب کاربری شما تایید نشده است ."})

        if not user.is_active:
            if MobileList.objects.filter(mobile=mobile, is_active=True).exists():
                user.is_active = True
                user.save()
            else:
                raise serializers.ValidationError(
                    {"error": "حساب کاربری غیرفعال است و شماره موبایل در لیست نیست لطفا با پشتیبانی تماس بگیرید."})

        data['user'] = user
        return data


class LoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        mobile = data.get('mobile')
        password = data.get('password')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است"})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "کاربری با این شماره موبایل ساخته نشده."})
        except Exception as e:
            raise serializers.ValidationError({"error": f"An error occurred while fetching user: {str(e)}"})

        if not user.is_verified:
            raise serializers.ValidationError({"error": "حساب کاربری شما تایید نشده است ."})

        if not user.is_active:
            if MobileList.objects.filter(mobile=mobile, is_active=True).exists():
                user.is_active = True
                user.save()
            else:
                raise serializers.ValidationError(
                    {"error": "حساب کاربری غیرفعال است و شماره موبایل در لیست نیست لطفا با پشتیبانی تماس بگیرید."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "رمز عبور نامعتبر"})

        data['user'] = user
        return data


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: list user
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserDetailsListSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), many=True)
    city_label = serializers.CharField(source='city.label', read_only=True)
    state_label = serializers.CharField(source='state.label', read_only=True)
    company_state_label = serializers.CharField(source='company_state.label', read_only=True)
    company_city_label = serializers.CharField(source='company_city.label', read_only=True)

    class Meta:
        model = UserDetails
        fields = (
            'id', 'company_name','first_name_en', 'last_name_en', 'zipcode', 'is_completed', 'mobile2', 'city', 'state', 'user', 'city_label', 'state_label',
            'company_city', 'company_state', 'company_city_label', 'company_state_label',
            'is_international_course', 'birthday',
            'company_address', 'count_course', 'establishment_year', 'address', 'website', 'instagram',
            'member_instagram', 'logo',
            'employees_count', 'average_income', 'unit', 'created_at')




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: profile user
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ProfileUserSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source='industry.name', read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'first_name', 'last_name', 'gender', 'email', 'role', 'mobile', 'is_active', 'avatar', 'industry',
            'industry_name', 'core_user',
            'sub_industry')
        read_only_fields = ('id', 'role', 'is_active', 'is_verified')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: change password user
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        return super().validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    re_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["password"] == attrs["re_password"]:
            return attrs
        else:
            raise serializers.ValidationError({"error": "رمز عبور مطابقت ندارد."})


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            raise serializers.ValidationError({"error": 'رمز عبور فعلی اشتباه است'})


class ChangePasswordSerializer(PasswordRetypeSerializer, PasswordSerializer, CurrentPasswordSerializer):
    pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: ADMIN  panel
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SendCodePasswordCheckBCSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        mobile = data.get('mobile')
        password = data.get('password')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است"})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "کاربری با این شماره موبایل یافت نشد."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "رمز عبور نادرست است."})

        if not user.is_verified:
            raise serializers.ValidationError({"error": "حساب کاربری شما تایید نشده است."})

        if user.role != 'bc':
            raise serializers.ValidationError({"error": "دسترسی فقط برای بیزینس کوچ ها مجاز است."})

        try:
            verification_code = ''.join(random.choices(string.digits, k=6))
            redis_conn = get_redis_connection("default")
            redis_conn.setex(f"verification_code:{mobile}", 120, verification_code)

            logger.info(f"OTP {verification_code} stored for mobile {mobile}")
            send_verification_sms.delay(mobile, verification_code)
            logger.info(f"OTP send task triggered for mobile {mobile}")
        except Exception as e:
            logger.error(f"Error sending OTP for mobile {mobile}: {str(e)}")
            raise serializers.ValidationError({"error": f"ارسال کد تأیید ناموفق بود: {str(e)}"})

        return data


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SendCodePasswordCheckAdminSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        mobile = data.get('mobile')
        password = data.get('password')

        if not (mobile.isdigit() and len(mobile) == 11):
            raise serializers.ValidationError({"error": "فرمت شماره موبایل نادرست است"})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "کاربری با این شماره موبایل یافت نشد."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "رمز عبور نادرست است."})

        if not user.is_verified:
            raise serializers.ValidationError({"error": "حساب کاربری شما تایید نشده است."})

        if user.role not in ['admin', 'superuser']:
            raise serializers.ValidationError({"error": "دسترسی فقط برای مدیران مجاز است."})

        try:
            verification_code = ''.join(random.choices(string.digits, k=6))
            redis_conn = get_redis_connection("default")
            redis_conn.setex(f"verification_code:{mobile}", 120, verification_code)

            logger.info(f"OTP {verification_code} stored for mobile {mobile}")
            send_verification_sms.delay(mobile, verification_code)
            logger.info(f"OTP send task triggered for mobile {mobile}")
        except Exception as e:
            logger.error(f"Error sending OTP for mobile {mobile}: {str(e)}")
            raise serializers.ValidationError({"error": f"ارسال کد تأیید ناموفق بود: {str(e)}"})

        return data


class LoginVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        mobile = data['mobile']
        code = data['code']

        redis_conn = get_redis_connection("default")
        stored_code = redis_conn.get(f"verification_code:{mobile}")

        if not stored_code or stored_code.decode() != code:
            raise serializers.ValidationError({"error": "کد تایید نامعتبر یا منقضی شده است."})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "کاربر یافت نشد."})

        if not user.is_verified:
            raise serializers.ValidationError({"error": "حساب کاربری تایید نشده است."})

        if user.role not in ['admin', 'bc', 'superuser']:
            raise serializers.ValidationError({"error": "دسترسی فقط برای کاربران ادمین یا بیزینس کوچ مجاز است."})

        redis_conn.delete(f"verification_code:{mobile}")

        data['user'] = user
        return data
