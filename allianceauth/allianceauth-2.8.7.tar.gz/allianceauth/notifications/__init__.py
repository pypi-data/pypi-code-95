default_app_config = 'allianceauth.notifications.apps.NotificationsConfig'


def notify(
    user: object, title: str, message: str = None, level: str = 'info'
) -> None:
    """Sends a new notification to user. Convenience function to manager pendant."""
    from .models import Notification
    Notification.objects.notify_user(user, title, message, level)
