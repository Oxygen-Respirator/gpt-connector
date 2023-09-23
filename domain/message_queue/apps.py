from django.apps import AppConfig


class MessageQueueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domain.message_queue'
