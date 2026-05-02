from celery import shared_task
from django.core.mail import send_mail

from core.settings import DEFAULT_FROM_EMAIL

@shared_task
def send_activation_key(user_email, activation_key):
    """Отправляет сообщение с ключом регистрации на почту"""
    subject = 'Активация аккаунта'
    message = f'Привет!\nРегистрация прошла успешно. Ключ для активации:\n{activation_key}'
    from_email = DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

