from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    NotFound, PermissionDenied, AuthenticationFailed, NotAuthenticated,
    ValidationError, ParseError, MethodNotAllowed, Throttled, NotAcceptable,
    UnsupportedMediaType
)
from rest_framework.response import Response
from core.messages import get_error_message
import logging

logger = logging.getLogger(__name__)


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')

        if response is None or data is None:
            return super().render({
                'success': False,
                'code': 'no_data',
                'message': 'هیچ داده‌ای موجود نیست.',
                'errors': {}
            }, accepted_media_type, renderer_context)

        # status ok
        if 200 <= response.status_code < 300:
            return super().render(data, accepted_media_type, renderer_context)

        # error massage
        return super().render(data, accepted_media_type, renderer_context)


def custom_exception_handler(exc, context):
    exception_map = {
        NotFound: 'not_found',
        PermissionDenied: 'permission_denied',
        AuthenticationFailed: 'authentication_failed',
        NotAuthenticated: 'not_authenticated',
        ValidationError: 'validation_error',
        ParseError: 'parse_error',
        MethodNotAllowed: 'method_not_allowed',
        Throttled: 'throttled',
        NotAcceptable: 'not_acceptable',
        UnsupportedMediaType: 'unsupported_media_type',
    }

    error_key = next((key for exc_type, key in exception_map.items() if isinstance(exc, exc_type)), None)

    if error_key:
        code, message, status_code = get_error_message(error_key)

        #  ValidationError
        if isinstance(exc, ValidationError):
            errors = {}
            detail = exc.detail

            if isinstance(detail, dict):
                for field, msgs in detail.items():
                    if isinstance(msgs, list):
                        errors[field] = [str(msg) for msg in msgs[:10]]
                    else:
                        errors[field] = [str(msgs)]
            elif isinstance(detail, list):
                errors['non_field_errors'] = [str(msg) for msg in detail]
            else:
                errors['non_field_errors'] = [str(detail)]
        else:
            errors = {'detail': str(getattr(exc, 'detail', exc))}

        return Response({
            'success': False,
            'code': code,
            'message': message,
            'errors': errors
        }, status=status_code)

    # error DRF
    response = drf_exception_handler(exc, context)
    if response is not None:
        code, message, _ = get_error_message('server_error')
        response.data = {
            'success': False,
            'code': code,
            'message': message,
            'errors': response.data
        }
        return response

    # db - unecpted error
    logger.error("Unhandled exception occurred", exc_info=True)
    code, message, status_code = get_error_message('server_error')
    return Response({
        'success': False,
        'code': code,
        'message': message,
        'errors': {'detail': str(exc)}
    }, status=status_code)
