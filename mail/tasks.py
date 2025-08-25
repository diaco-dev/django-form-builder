from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template

from config import settings
from config.celery import app
from core.exceptions import EmailTemplateNotFound


def get_email_template(template_name):
    has_html, has_txt = True, True
    try:
        html_template = get_template('%s.html' % template_name)
    except TemplateDoesNotExist:
        has_html, html_template = False, None

    try:
        txt_template = get_template('%s.txt' % template_name)
    except TemplateDoesNotExist:
        has_txt, txt_template = False, None

    if has_txt is False:
        raise EmailTemplateNotFound("An Email Template was not found")
    return {
        'txt': txt_template,
        'html': html_template,
    }


@app.task
def send_email(context):
    email_to = context['to'].split(',')
    email_cc = context['cc'].split(',')
    email_bcc = context['bcc'].split(',')

    # subject, body, from_email, to, bcc, connection, attachments, headers, cc, reply_to,
    msg = EmailMultiAlternatives(subject=context['subject'],
                                 body=context['body'],
                                 to=email_to,
                                 )

    if msg:
        if email_cc:
            msg.cc = email_cc
        if email_bcc:
            msg.bcc = email_bcc
        if context['from_email']:
            msg.from_email = context['from_email']
        else:
            msg.from_email = settings.DEFAULT_FROM_EMAIL
        if context['reply_to']:
            msg.reply_to = context['reply_to']
        if context['html']:
            msg.attach_alternative(context['html'], 'text/html')

    try:
        msg.send()
        # email.status = EMAILTYPE_CHOICES.DONE
        # email.error_message = "done"
        # email.message = text_content
        # email.body = html_content
        # email.save()
    except Exception as e:
        # email.status = EMAILTYPE_CHOICES.FAIL
        # email.error_message = e
        # email.save()
        print(e)
