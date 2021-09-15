from django.urls import path, include


urls = [
    path('', include('sha_accounts.urls'))
]

urlpatterns = urls
