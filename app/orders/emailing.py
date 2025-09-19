from django.core.mail import send_mail
from django.conf import settings


def send_order_emails(order):
    """Отправка email-уведомлений клиенту и админу после оплаты заказа"""

    subject_client = f"Ваш заказ №{order.id} успешно оплачен"
    message_client = (
        f"Здравствуйте, {order.first_name}!\n\n"
        f"Спасибо за ваш заказ №{order.id}.\n"
        f"Сумма: {order.get_total_cost()}.\n\n"
        f"Мы скоро свяжемся с вами для подтверждения."
    )

    subject_admin = f"Новый оплаченный заказ №{order.id}"
    message_admin = (
        f"Заказ №{order.id} был успешно оплачен.\n\n"
        f"Клиент: {order.first_name} {order.last_name}\n"
        f"Email: {order.email}\n"
        f"Телефон: {order.phone}\n\n"
        f"Сумма заказа: {order.get_total_cost()}"
    )

    # письмо клиенту
    send_mail(
        subject_client,
        message_client,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
    )

    # письмо админу
    send_mail(
        subject_admin,
        message_admin,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
    )
