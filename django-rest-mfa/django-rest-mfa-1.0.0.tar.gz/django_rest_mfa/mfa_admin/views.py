from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, TemplateView
from django.views.generic.list import ListView
from django_rest_mfa.models import UserKey
from django_rest_mfa.helpers import has_mfa


@method_decorator(login_required, name='dispatch')
class UserKeyListView(ListView):
    model = UserKey

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_otp"] = self.get_queryset().filter(key_type=UserKey.KeyType.TOTP).exists()
        return context


@method_decorator(login_required, name='dispatch')
class UserKeyDeleteView(DeleteView):
    model = UserKey
    success_url = reverse_lazy("user-key-list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)



class MFAAdminLoginView(LoginView):
    template_name = "django_rest_mfa/login.html"

    def form_valid(self, form):
        if has_mfa(self.request, form.get_user()):
            user = form.get_user()
            next_url = ""
            next_param = self.request.GET.get("next")
            if next_param:
                next_url = "?next=" + next_param
            return HttpResponseRedirect(reverse("login-mfa") + next_url)
        return super().form_valid(form)


class MFAAdminSecondFactorView(TemplateView):
    template_name = "django_rest_mfa/second_factor.html"