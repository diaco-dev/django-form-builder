import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from django.conf import settings
from pathlib import Path
import logging.config

LOG_DIR = Path(settings.BASE_DIR) / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {module} {funcName} {lineno} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s %(pathname)s',
        },
        'request_formatter': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s %(pathname)s %(lineno)d %(request_method)s %(request_url)s %(status_code)d %(remote_addr)s %(user_agent)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'debug.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'request_info_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'info.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'request_formatter',
        },
        'request_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'request_formatter',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'debug_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'myapp': {
            'handlers': ['console', 'file', 'debug_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'project.requests.info': {
            'handlers': ['request_info_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'project.requests.error': {
            'handlers': ['request_error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.info_logger = logging.getLogger('project.requests.info')
        self.error_logger = logging.getLogger('project.requests.error')

    def __call__(self, request):
        response = self.get_response(request)

        log_data = {
            'request_method': request.method,
            'request_url': request.get_full_path(),
            'status_code': response.status_code,
            'remote_addr': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'message': f'HTTP {request.method} request to {request.get_full_path()}',
        }

        if response.status_code == 404:
            log_data['message'] = f'Not Found: {request.get_full_path()}'
        elif response.status_code == 401:
            log_data['message'] = f'Unauthorized: {request.get_full_path()}'

        if response.status_code >= 400:
            self.error_logger.error(log_data)
        else:
            self.info_logger.info(log_data)

        return response


def get_custom_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    custom_handler = RotatingFileHandler(
        filename=str(LOG_DIR / f'{name}.log'),
        maxBytes=1024 * 1024 * 15,  # 15MB
        backupCount=10
    )
    custom_handler.setFormatter(jsonlogger.JsonFormatter())

    if not logger.handlers:
        logger.addHandler(custom_handler)

    return logger

logging.config.dictConfig(LOGGING)