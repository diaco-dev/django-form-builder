from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.template.loader_tags import BlockNode
from django.views.generic.base import ContextMixin
from render_block import render_block_to_string

from mail.tasks import send_email


# django-templated-mail
class BaseEmailMessage(EmailMultiAlternatives, ContextMixin):
    _node_map = {
        'subject': 'subject',
        'text_body': 'body',
        'html_body': 'html',
    }
    template_name = None

    def __init__(self, request=None, context=None, template_name=None,
                 *args, **kwargs):
        super(BaseEmailMessage, self).__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        self.html = None

        if template_name is not None:
            self.template_name = template_name

    def get_context_data(self, **kwargs):
        ctx = super(BaseEmailMessage, self).get_context_data(**kwargs)
        context = dict(ctx, **self.context)
        if self.request:
            site = get_current_site(self.request)
            domain = context.get('domain') or (
                    getattr(settings, 'DOMAIN', '') or site.domain
            )
            protocol = context.get('protocol') or (
                'https' if self.request.is_secure() else 'http'
            )
            site_name = context.get('site_name') or (
                    getattr(settings, 'SITE_NAME', '') or site.name
            )
            user = context.get('user') or self.request.user
        else:
            domain = context.get('domain') or getattr(settings, 'DOMAIN', '')
            protocol = context.get('protocol') or 'http'
            site_name = context.get('site_name') or getattr(
                settings, 'SITE_NAME', ''
            )
            user = context.get('user')

        context.update({
            'domain': domain,
            'protocol': protocol,
            'site_name': site_name,
            'user': user,
        })
        return context

    def render(self):
        context = self.get_context_data()
        self.html = render_to_string(self.template_name, context)
        self.body = render_block_to_string(self.template_name, 'text_body', context)
        self.subject = render_block_to_string(self.template_name, 'subject', context).replace('\n', '')

    def send(self, to, *args, **kwargs):
        self.render()

        email_to = ','.join(to)
        email_cc = ','.join(kwargs.pop('cc', []))
        email_bcc = ','.join(kwargs.pop('bcc', []))
        reply_to = kwargs.pop('reply_to', '')
        from_email = kwargs.pop(
            'from_email', settings.DEFAULT_FROM_EMAIL
        )

        if settings.DEVELOPMENT:
            try:
                send_email({
                    'to': email_to,
                    'cc': email_cc,
                    'bcc': email_bcc,
                    'reply_to': reply_to,
                    'subject': self.subject,
                    'body': self.body,
                    'html': self.html,
                    'from_email': from_email,
                })
            except Exception as e:
                print(e)
        else:
            # send_email({
            send_email.delay({
                'to': email_to,
                'cc': email_cc,
                'bcc': email_bcc,
                'reply_to': reply_to,
                'subject': self.subject,
                'body': self.body,
                'html': self.html,
                'from_email': from_email,
            })

    # def _get_block(self, template_name, context, name='subject'):
    #     template = get_template(template_name)
    #
    #     blocks = self._get_blocks(template.template.nodelist, context)
    #     for block_node in blocks.values():
    #         self._process_block(block_node, context)

    def _get_block(self, template_name, context, block_name='subject'):
        return render_block_to_string(template_name, block_name, context)
