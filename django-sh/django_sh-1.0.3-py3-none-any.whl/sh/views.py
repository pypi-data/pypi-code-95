from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .models import SavedCommand, ShellSettings, Command
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.urls import reverse


class anyimport(object):
    def __init__(self, importmodule, scope):
        exec (importmodule, scope)

@user_passes_test(lambda u: u.is_superuser)
def command(request, pk=None): 
    error = ''
    command_obj = None
    objects = []
    
    if request.method == 'POST':
        command_obj, error = ejecutar(request)  
        return redirect(reverse("sh:command", args=[command_obj.pk]))
    
    default_command_text = ""
    if pk:
        command_obj = get_object_or_404(Command, pk=pk)
        default_command_text = command_obj.text

    command = request.POST.get("query", default_command_text)
    return render(request, 'sh/command.html', { 
        'objects':objects, 
        'query': command, 
        'command_obj': command_obj, 
        'error':error 
    }) 


@user_passes_test(lambda u: u.is_superuser)
def ejecutar(request):
    from builtins import str

    try:
        shell_settings = ShellSettings.objects.get()
    except ObjectDoesNotExist:
        shell_settings = ShellSettings.objects.get_or_create()[0]
    
    command = Command()
    objects = []
    query = request.POST.get('query', '').strip()
    q = query.replace("\r","")
    q += "\n"
    error = ""

    command.start = timezone.now()
    command.text = ""

    if shell_settings.code_before:
        command.text += f"{shell_settings.code_before}\n\n-------"
        exec(shell_settings.code_before)

    # helpers
    _ = objects.append
    
    command.text += f"{q}\n"
    if request.POST.get("enable_try"):
        try:
            exec(q)
        except Exception as e:
            error = u"%s %s" % (str(e.__class__), str(e))

    else:
        exec(q)    
    
    if shell_settings.code_after:
        command.text += f"-------\n\n{shell_settings.code_after}"
        exec(shell_settings.code_after)

    command.end = timezone.now()
    command.output = "\n".join(objects)
    command.save()
    return command, error

@user_passes_test(lambda u: u.is_superuser)
def editar_configuracion(request):
    shell_settings = ShellSettings.objects.get_or_create()[0]

    if request.method == "POST":
        shell_settings.code_before = request.POST.get("code_before")
        shell_settings.code_after = request.POST.get("code_after")
        shell_settings.save()
        return redirect("sh:command")
    
    return render(
        request,
        'sh/settings.html',
        {"shell_settings":shell_settings},
    )

@user_passes_test(lambda u: u.is_superuser)
def save_command(request, pk):
    instance = get_object_or_404(Command, pk=pk)
    saved_command = SavedCommand.objects.create(
        command=instance, 
        user=request.user,
    )
    return redirect("sh:command_history")

@user_passes_test(lambda u: u.is_superuser)
def saved_commands(request):
    objects = request.user.saved_commands.all()
    return render(
        request,
        'sh/saved_commands.html',
        {"objects": objects},
    )


@user_passes_test(lambda u: u.is_superuser)
def command_history(request):
    objects = Command.objects.all()
    return render(
        request,
        'sh/command_history.html',
        {"objects": objects},
    )
