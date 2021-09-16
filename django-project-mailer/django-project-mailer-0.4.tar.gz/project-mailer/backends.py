from django.core.mail.backends.smtp import EmailBackend
from .models import EmailModel

email_data = EmailModel.objects.get(id=4)
backends = EmailBackend(host=email_data.email_host, port=email_data.email_port,
                        username=email_data.email_host_user, password=email_data.email_host_password,
                        use_tls=email_data.email_use_tls
                        )


def email_from(request):
    from_email = email_data.email_host_user
    request.session['from_email'] = from_email
    return from_email
