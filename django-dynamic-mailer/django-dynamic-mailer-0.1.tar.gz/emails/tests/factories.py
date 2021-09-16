from faker import Factory, Faker
from emails.models import EmailModel, EmailReminder, Notifications
import factory
from datetime import datetime
import random
from faker.providers import BaseProvider

faker = Factory.create()
fake = Faker()

# Create your models here.

email_host = [
    'Smtp.1and1.com', 'Mail.airmail.net', 'Smtp.aol.com', 'Outbound.att.net', 'Smtpauths.bluewin.ch',
    'Mail.btconnect.tom', 'Smtp.comcast.net', 'Smtpauth.earthlink.net', 'Smtp.gmail.com', 'Mail.gmx.net',
    'Mail.hotpop.com', 'Mail.libero.it', 'Smtp.lycos.com', 'Smtp.o2.com', 'Smtp.orange.net', 'Smtp.live.com',
    'Mail.tin.it', 'Smtp.tiscali.co.uk', 'Outgoing.verizon.net', 'Smtp.virgin.net', 'Smtp.wanadoo.fr',
    'Mail.yahoo.com']


class Provider(BaseProvider):
    def email_host(self):
        return self.random_element(email_host)


fake.add_provider(Provider)


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailModel

    creator_name = faker.name()
    email_host_user = faker.company_email()
    email_host_password = faker.password()
    email_port = faker.port_number()
    email_use_tls = faker.boolean(chance_of_getting_true=50)
    email_use_ssl = faker.boolean(chance_of_getting_true=50)
    email_host = fake.email_host()


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notifications

    notification_type = faker.name()


class EmailRemainderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailReminder

    subject = faker.text()
    body = fake.paragraph(nb_sentences=20)
    signature = fake.paragraph(nb_sentences=10)
    email_notification_type = faker.name()
    occurrence = faker.boolean(chance_of_getting_true=50)
    schedule = faker.boolean(chance_of_getting_true=50)
    interval_period = faker.date_time()
    status = faker.boolean(chance_of_getting_true=50)
    is_deleted = faker.boolean(chance_of_getting_true=50)
