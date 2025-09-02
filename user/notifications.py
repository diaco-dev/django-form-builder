from django.contrib.auth.tokens import default_token_generator
from utils.encode import encode_uid
from mail.generics import BaseEmailMessage


class ActivationEmail(BaseEmailMessage):
    template_name = "email/activation.html"

    def get_context_data(self):
        # ActivationEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        # context["url"] = ACTIVATION_URL.format(**context)
        return context


class PasswordResetEmail(BaseEmailMessage):
    template_name = "email/password_reset.html"

    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["site_name"] = 'chavoshinia.de'
        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        # context["url"] = PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context


class ConfirmationEmail(BaseEmailMessage):
    template_name = "email/confirmation.html"


class ManagerSetPasswrdNotifyEmail(BaseEmailMessage):
    template_name = "email/manager-set-password-notify.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["password"] = context.get("password")
        return context


class UserBanNotifyEmail(BaseEmailMessage):
    template_name = "email/user-banned-notify.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["status"] = context.get("status")
        return context


class LoginNotification(BaseEmailMessage):
    template_name = "email/login-notification.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["time"] = context.get("time")
        context["ip"] = context.get("ip")
        context["tz"] = context.get("tz")
        return context
