import logging
logger = logging.getLogger(__name__)
import requests
from celery import shared_task


@shared_task
def test_beat():
    print("Celery Beat is working!")
    return "Task executed!"

KAVENEGAR_API_KEY="5478516E4B616739623445764937643855615A6A4675724F4C6F55472B354966334B77635A6D72757473493D"
def send_sms(receptor, variables, pattern_code):
    url = f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json"
    payload = {
        'receptor': receptor,
        'template': pattern_code,
        'token': variables.get('verification-code'),
        'type': 'sms'
    }
    logger.info(f"Sending SMS to {receptor} with payload: {payload}")
    try:
        response = requests.post(url, data=payload, timeout=10)  # Add timeout
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        if response.status_code == 200:
            result = response.json()
            if result.get('return', {}).get('status') == 200:
                logger.info(f"SMS sent successfully to {receptor}")
            else:
                logger.error(f"API error: {result}")
        else:
            logger.error(f"Error sending SMS: {response.status_code} - {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in send_sms: {e}", exc_info=True)
        return None

@shared_task
def send_verification_sms(mobile, code):
    logger.info(f"Starting to send SMS to {mobile} with code {code}")
    try:
        variables = {
            "verification-code": str(code)
        }
        response = send_sms(mobile, variables, 'ibc-otp')
        if response and response.status_code == 200:
            logger.info(f"Verification SMS sent to {mobile}")
        else:
            raise Exception("Failed to send SMS")
    except Exception as e:
        logger.error(f"Error in send_verification_sms: {e}", exc_info=True)
        raise  # For Celery retry
