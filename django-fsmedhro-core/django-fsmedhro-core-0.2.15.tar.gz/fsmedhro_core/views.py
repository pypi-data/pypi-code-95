import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import redirect, render
from django.views import View

from .forms import FachschaftUserForm
from .models import Studienabschnitt, Studiengang, Gender, FachschaftUser


logger = logging.getLogger(__name__)


class FachschaftUserEdit(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # FachschaftUser bereits vorhanden?
            form = FachschaftUserForm(instance=request.user.fachschaftuser)
        except ObjectDoesNotExist:
            form = FachschaftUserForm()

        context = {
            'form': form,
        }

        return render(request, 'fsmedhro_core/user_edit.html', context)

    def post(self, request):
        try:
            form = FachschaftUserForm(
                data=request.POST,
                instance=request.user.fachschaftuser,
            )
        except ObjectDoesNotExist:
            form = FachschaftUserForm(
                data=request.POST,
            )

        if form.is_valid():
            fachschaftuser = form.save(commit=False)
            fachschaftuser.user = request.user
            fachschaftuser.save()

        return redirect('fsmedhro_core:detail')


class FachschaftUserDetail(LoginRequiredMixin, View):
    def get(self, request):
        try:
            fachschaftuser = request.user.fachschaftuser
        except ObjectDoesNotExist:
            return redirect('fsmedhro_core:edit')

        context = {
            'fachschaftuser': fachschaftuser,
        }

        return render(request, 'fsmedhro_core/user_detail.html', context)


class Rundmail(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self):
        context = {
            'studienabschnitte': Studienabschnitt.objects.all(),
            'studiengaenge': Studiengang.objects.all(),
            'gender': Gender.objects.all(),
        }
        return context

    def get(self, request):
        context = self.get_context_data()
        return render(request, 'fsmedhro_core/rundmail.html', context)

    def post(self, request):
        context = self.get_context_data()
        errors = []

        studiengaenge = list(map(int, request.POST.getlist('studiengang', [])))
        context['gew_studiengaenge'] = studiengaenge
        if not studiengaenge:
            errors.append("Es wurde kein Studiengang ausgewählt.")

        studienabschnitte = list(map(int, request.POST.getlist('studienabschnitt', [])))
        context['gew_studienabschnitte'] = studienabschnitte
        if not studienabschnitte:
            errors.append("Es wurde kein Studienabschnitt ausgewählt.")

        gender = list(map(int, request.POST.getlist('gender', [])))
        context['gew_gender'] = gender
        if not gender:
            errors.append("Es wurde kein Geschlecht ausgewählt.")

        betreff = request.POST.get('email_subject', '')
        context['betreff'] = betreff
        if not betreff:
            errors.append('Der Betreff fehlt.')

        text = request.POST.get('email_text', '')
        context['text'] = text
        if not text:
            errors.append('Der Text fehlt.')

        send_testmail = bool(request.POST.get('send_testmail', False))

        if errors:
            context['errors'] = errors
            return render(request, 'fsmedhro_core/rundmail.html', context)
        elif send_testmail:
            anzahl_verschickt = send_mail(
                subject=betreff,
                message=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            logger.info(
                f'{request.user} verschickte Testmail\n' +
                f'{betreff=}\n' +
                f'{text=}'
            )
            context['testmail_verschickt'] = True
            context['anzahl_verschickt'] = anzahl_verschickt

            return render(request, 'fsmedhro_core/rundmail.html', context)
        else:
            empfaenger = FachschaftUser.objects.filter(
                studiengang__in=studiengaenge,
                studienabschnitt__in=studienabschnitte,
                gender__in=gender,
            ).order_by('user__email')
            empfaenger_adressen = [empf.user.email for empf in empfaenger]

            mails = EmailMessage(
                subject=betreff,
                body=text,
                bcc=empfaenger_adressen,
            )

            mails.send()
            logger.info(
                f'{request.user} verschickte Rundmail\n' +
                f'{betreff=}\n' +
                f'{text=}\n' +
                f'an' +
                ', '.join(empfaenger_adressen)
            )

            context['anzahl_verschickt'] = len(empfaenger)

            sicherheitsnachricht = (
                f'Die folgende Nachricht:\n\n' +
                f'Betreff: {betreff}\n' +
                f'Text:\n' +
                f'{text}\n\n' +
                f'wurde von {request.user} '
                f'an {len(empfaenger)} Personen verschickt:\n\n' +
                '\n'.join(empfaenger_adressen)
            )
            send_mail(
                subject='Rundmail verschickt: ' + betreff,
                message=sicherheitsnachricht,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            return render(request, 'fsmedhro_core/rundmail.html', context)
