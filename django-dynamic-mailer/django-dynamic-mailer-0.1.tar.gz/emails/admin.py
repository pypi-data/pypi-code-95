from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(EmailModel)
admin.site.register(Actions)
admin.site.register(Modules)
admin.site.register(Notifications)
admin.site.register(Policies)
admin.site.register(UserEmails)
admin.site.register(EmailReminder)
admin.site.register(List)
