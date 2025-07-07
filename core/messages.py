from rest_framework import status
from typing import Tuple

ERROR_MAP = {
    'not_found': {
        'code': 'not_found',
        'message': 'موردی با این مشخصات یافت نشد.',
        'status': status.HTTP_404_NOT_FOUND
    },
    'permission_denied': {
        'code': 'permission_denied',
        'message': 'شما اجازه دسترسی به این بخش را ندارید.',
        'status': status.HTTP_403_FORBIDDEN
    },
    'authentication_failed': {
        'code': 'unauthorized',
        'message': 'احراز هویت انجام نشد. لطفاً اعتبارنامه‌های معتبر وارد کنید.',
        'status': status.HTTP_401_UNAUTHORIZED
    },
    'not_authenticated': {
        'code': 'not_authenticated',
        'message': 'شما وارد سیستم نشده‌اید. لطفاً ابتدا وارد شوید.',
        'status': status.HTTP_401_UNAUTHORIZED
    },
    'invalid_token': {
        'code': 'invalid_token',
        'message': 'توکن احراز هویت نامعتبر است.',
        'status': status.HTTP_401_UNAUTHORIZED
    },
    'credentials_not_provided': {
        'code': 'credentials_not_provided',
        'message': 'اعتبارنامه‌های احراز هویت ارائه نشده‌اند.',
        'status': status.HTTP_401_UNAUTHORIZED
    },
    'validation_error': {
        'code': 'invalid_data',
        'message': 'برخی از فیلدها معتبر نیستند.',
        'status': status.HTTP_400_BAD_REQUEST
    },
    'parse_error': {
        'code': 'parse_error',
        'message': 'خطا در پردازش درخواست.',
        'status': status.HTTP_400_BAD_REQUEST
    },
    'method_not_allowed': {
        'code': 'method_not_allowed',
        'message': 'متد درخواست مجاز نیست.',
        'status': status.HTTP_405_METHOD_NOT_ALLOWED
    },
    'throttled': {
        'code': 'throttled',
        'message': 'تعداد درخواست‌ها بیش از حد مجاز است.',
        'status': status.HTTP_429_TOO_MANY_REQUESTS
    },
    'not_acceptable': {
        'code': 'not_acceptable',
        'message': 'فرمت درخواست غیرقابل قبول است.',
        'status': status.HTTP_406_NOT_ACCEPTABLE
    },
    'unsupported_media_type': {
        'code': 'unsupported_media_type',
        'message': 'نوع رسانه پشتیبانی نمی‌شود.',
        'status': status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    },
    'server_error': {
        'code': 'server_error',
        'message': 'خطای داخلی سرور.',
        'status': status.HTTP_500_INTERNAL_SERVER_ERROR
    },
    'custom_error': {
        'code': 'custom_error',
        'message': 'خطای سفارشی رخ داده است.',
        'status': status.HTTP_400_BAD_REQUEST
    },
}


def get_error_message(error_key: str, default_message: str = None) -> Tuple[str, str, int]:

    error = ERROR_MAP.get(error_key)

    if error:
        return error['code'], error['message'], error['status']

    # generic error
    return (
        'server_error',
        default_message or 'خطای ناشناخته‌ای رخ داده است.',
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
