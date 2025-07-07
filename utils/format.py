from django.utils import timezone
from datetime import datetime
import os
from django.core.exceptions import ValidationError

def common_user_str(user):
    if not user:
        return ''
    return user.full_name if user.full_name else user.email


def common_datetime_str(datetime):
    if not datetime:
        return ''
    return datetime.strftime("%Y.%m.%d %H:%M")


def common_date_str(datetime):
    if not datetime:
        return ''
    return datetime.strftime("%Y.%m.%d")


def file_name_datetime_str():
    dt = timezone.now()
    return f'{dt.year}-{dt.month}-{dt.day}-{dt.hour}-{dt.minute}-{dt.second}'


#---------------------------------------------------
def upload_to_by_date(instance, filename):
    today = datetime.now()
    timestamp = today.strftime("%Y%m%d%H%M%S")
    file_extension = os.path.splitext(filename)[1]
    new_filename = f"{timestamp}{file_extension}"
    return os.path.join(f"storage/{today.year}/", new_filename)

#
#
# def validate_file_size(file):
#     max_size = 1024 * 1024 * 1024  # 1 GB
#     if file.size > max_size:
#         raise ValidationError("File size exceeds 1 GB limit.")